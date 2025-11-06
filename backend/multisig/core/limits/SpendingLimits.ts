/**
 * @class SpendingLimits
 * @dev Advanced spending limit management for multi-signature wallets
 * @author MultiSig Wallet System
 */

import Web3 from 'web3';
import { ethers } from 'ethers';

export interface LimitPeriod {
  daily: LimitConfig;
  weekly: LimitConfig;
  monthly: LimitConfig;
  single: LimitConfig;
}

export interface LimitConfig {
  amount: bigint;
  used: bigint;
  resetTime: number;
  resetInterval: number; // in seconds
}

export interface SpendingHistory {
  transactions: SpendingRecord[];
  periodStart: number;
  periodEnd: number;
}

export interface SpendingRecord {
  id: string;
  value: bigint;
  timestamp: number;
  status: 'executed' | 'cancelled' | 'failed';
}

export interface LimitViolation {
  type: 'daily' | 'weekly' | 'monthly' | 'single';
  limit: bigint;
  used: bigint;
  attempted: bigint;
  violation: bigint;
}

export interface RateLimit {
  window: number; // time window in seconds
  maxTransactions: number;
  currentCount: number;
  windowStart: number;
}

export class SpendingLimits {
  private provider: ethers.JsonRpcProvider;
  private walletAddress: string;
  private limits: Map<string, LimitPeriod> = new Map();
  private history: Map<string, SpendingHistory> = new Map();
  private rateLimits: Map<string, RateLimit> = new Map();

  constructor() {}

  initialize(walletAddress: string, provider: ethers.JsonRpcProvider): void {
    this.walletAddress = walletAddress;
    this.provider = provider;
  }

  /**
   * Configure spending limits
   */
  async configureLimits(periodLimits: LimitPeriod): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    
    // Store current limits
    this.limits.set(this.walletAddress, {
      daily: {
        ...periodLimits.daily,
        used: 0,
        resetTime: this.getNextResetTime(now, periodLimits.daily.resetInterval)
      },
      weekly: {
        ...periodLimits.weekly,
        used: 0,
        resetTime: this.getNextResetTime(now, periodLimits.weekly.resetInterval)
      },
      monthly: {
        ...periodLimits.monthly,
        used: 0,
        resetTime: this.getNextResetTime(now, periodLimits.monthly.resetInterval)
      },
      single: {
        ...periodLimits.single,
        used: 0,
        resetTime: this.getNextResetTime(now, periodLimits.single.resetInterval)
      }
    });

    // Load historical data
    await this.loadHistory();
  }

  /**
   * Validate transaction against spending limits
   */
  async validateTransaction(walletAddress: string, value: bigint): Promise<boolean> {
    const limits = this.limits.get(walletAddress);
    if (!limits) {
      return true; // No limits configured
    }

    // Reset counters if needed
    await this.resetIfNeeded(walletAddress);

    const violations = await this.checkViolations(walletAddress, value);
    
    if (violations.length > 0) {
      console.warn('Spending limit violations:', violations);
      return false;
    }

    // Check rate limits
    if (!this.checkRateLimit(walletAddress)) {
      console.warn('Rate limit exceeded');
      return false;
    }

    return true;
  }

  /**
   * Record transaction execution
   */
  async recordTransaction(
    txId: string,
    value: bigint,
    status: 'executed' | 'cancelled' | 'failed' = 'executed'
  ): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    const limits = this.limits.get(this.walletAddress);
    
    if (!limits) return;

    // Add to spending history
    const history = this.history.get(this.walletAddress) || {
      transactions: [],
      periodStart: now,
      periodEnd: this.getNextResetTime(now, limits.monthly.resetInterval)
    };

    history.transactions.push({
      id: txId,
      value,
      timestamp: now,
      status
    });

    this.history.set(this.walletAddress, history);

    // Update used amounts only if executed
    if (status === 'executed') {
      limits.daily.used += value;
      limits.weekly.used += value;
      limits.monthly.used += value;

      // Update rate limit
      this.updateRateLimit();
    }

    // Clean old records
    await this.cleanOldRecords();
  }

  /**
   * Get current spending status
   */
  async getSpendingStatus(walletAddress: string): Promise<{
    limits: LimitPeriod;
    history: SpendingRecord[];
    violations: LimitViolation[];
    rateLimit: RateLimit;
  }> {
    await this.resetIfNeeded(walletAddress);
    
    const limits = this.limits.get(walletAddress);
    const history = this.history.get(walletAddress);
    const violations = await this.checkViolations(walletAddress, 0n);
    const rateLimit = this.rateLimits.get(walletAddress) || this.getDefaultRateLimit();

    return {
      limits: limits || this.getDefaultLimits(),
      history: history?.transactions || [],
      violations,
      rateLimit
    };
  }

  /**
   * Get spending analytics
   */
  async getSpendingAnalytics(
    startDate: number,
    endDate: number
  ): Promise<{
    totalSpent: bigint;
    transactionCount: number;
    averageTransaction: bigint;
    largestTransaction: bigint;
    periodBreakdown: {
      daily: bigint;
      weekly: bigint;
      monthly: bigint;
    };
    topCategories: Array<{
      category: string;
      amount: bigint;
      count: number;
    }>;
  }> {
    const history = this.history.get(this.walletAddress);
    if (!history) {
      return {
        totalSpent: 0n,
        transactionCount: 0,
        averageTransaction: 0n,
        largestTransaction: 0n,
        periodBreakdown: {
          daily: 0n,
          weekly: 0n,
          monthly: 0n
        },
        topCategories: []
      };
    }

    const relevantTransactions = history.transactions.filter(
      tx => tx.status === 'executed' && 
            tx.timestamp >= startDate && 
            tx.timestamp <= endDate
    );

    let totalSpent = 0n;
    let transactionCount = 0;
    let largestTransaction = 0n;
    const categoryTotals = new Map<string, { amount: bigint; count: number }>();

    for (const tx of relevantTransactions) {
      totalSpent += tx.value;
      transactionCount++;
      largestTransaction = tx.value > largestTransaction ? tx.value : largestTransaction;
      
      // Categorize transaction (simplified)
      const category = this.categorizeTransaction(tx);
      const current = categoryTotals.get(category) || { amount: 0n, count: 0 };
      current.amount += tx.value;
      current.count++;
      categoryTotals.set(category, current);
    }

    const averageTransaction = transactionCount > 0 ? totalSpent / BigInt(transactionCount) : 0n;

    // Sort categories by amount
    const topCategories = Array.from(categoryTotals.entries())
      .sort((a, b) => b[1].amount > a[1].amount ? 1 : -1)
      .slice(0, 10)
      .map(([category, data]) => ({ category, amount: data.amount, count: data.count }));

    return {
      totalSpent,
      transactionCount,
      averageTransaction,
      largestTransaction,
      periodBreakdown: {
        daily: await this.getPeriodSpending(startDate, endDate, 24 * 60 * 60),
        weekly: await this.getPeriodSpending(startDate, endDate, 7 * 24 * 60 * 60),
        monthly: await this.getPeriodSpending(startDate, endDate, 30 * 24 * 60 * 60)
      },
      topCategories
    };
  }

  /**
   * Set up rate limiting
   */
  configureRateLimit(window: number, maxTransactions: number): void {
    this.rateLimits.set(this.walletAddress, {
      window,
      maxTransactions,
      currentCount: 0,
      windowStart: Math.floor(Date.now() / 1000)
    });
  }

  /**
   * Load historical spending data
   */
  async loadHistory(): Promise<void> {
    try {
      // This would typically load from blockchain or database
      // For now, initialize with empty history
      const now = Math.floor(Date.now() / 1000);
      this.history.set(this.walletAddress, {
        transactions: [],
        periodStart: now,
        periodEnd: now + 30 * 24 * 60 * 60 // 30 days
      });
    } catch (error) {
      console.error('Failed to load spending history:', error);
    }
  }

  /**
   * Export spending data
   */
  async exportData(format: 'csv' | 'json' = 'json'): Promise<string> {
    const status = await this.getSpendingStatus(this.walletAddress);
    const analytics = await this.getSpendingAnalytics(
      status.limits.daily.resetTime - 24 * 60 * 60,
      Date.now()
    );

    if (format === 'csv') {
      return this.convertToCSV(status.history, analytics);
    } else {
      return JSON.stringify({
        status,
        analytics,
        exportedAt: new Date().toISOString()
      }, null, 2);
    }
  }

  /**
   * Private helper methods
   */
  private getNextResetTime(now: number, interval: number): number {
    return Math.floor(now / interval) * interval + interval;
  }

  private async resetIfNeeded(walletAddress: string): Promise<void> {
    const limits = this.limits.get(walletAddress);
    if (!limits) return;

    const now = Math.floor(Date.now() / 1000);

    // Reset daily limit
    if (now >= limits.daily.resetTime) {
      limits.daily.used = 0n;
      limits.daily.resetTime = this.getNextResetTime(now, limits.daily.resetInterval);
    }

    // Reset weekly limit
    if (now >= limits.weekly.resetTime) {
      limits.weekly.used = 0n;
      limits.weekly.resetTime = this.getNextResetTime(now, limits.weekly.resetInterval);
    }

    // Reset monthly limit
    if (now >= limits.monthly.resetTime) {
      limits.monthly.used = 0n;
      limits.monthly.resetTime = this.getNextResetTime(now, limits.monthly.resetInterval);
    }

    // Reset rate limit
    await this.resetRateLimitIfNeeded(walletAddress);
  }

  private async resetRateLimitIfNeeded(walletAddress: string): Promise<void> {
    const rateLimit = this.rateLimits.get(walletAddress);
    if (!rateLimit) return;

    const now = Math.floor(Date.now() / 1000);
    
    if (now >= rateLimit.windowStart + rateLimit.window) {
      rateLimit.currentCount = 0;
      rateLimit.windowStart = now;
    }
  }

  private async checkViolations(
    walletAddress: string,
    value: bigint
  ): Promise<LimitViolation[]> {
    const violations: LimitViolation[] = [];
    const limits = this.limits.get(walletAddress);
    if (!limits) return violations;

    // Check daily limit
    if (limits.daily.used + value > limits.daily.amount) {
      violations.push({
        type: 'daily',
        limit: limits.daily.amount,
        used: limits.daily.used,
        attempted: value,
        violation: limits.daily.used + value - limits.daily.amount
      });
    }

    // Check weekly limit
    if (limits.weekly.used + value > limits.weekly.amount) {
      violations.push({
        type: 'weekly',
        limit: limits.weekly.amount,
        used: limits.weekly.used,
        attempted: value,
        violation: limits.weekly.used + value - limits.weekly.amount
      });
    }

    // Check monthly limit
    if (limits.monthly.used + value > limits.monthly.amount) {
      violations.push({
        type: 'monthly',
        limit: limits.monthly.amount,
        used: limits.monthly.used,
        attempted: value,
        violation: limits.monthly.used + value - limits.monthly.amount
      });
    }

    // Check single transaction limit
    if (value > limits.single.amount) {
      violations.push({
        type: 'single',
        limit: limits.single.amount,
        used: 0n,
        attempted: value,
        violation: value - limits.single.amount
      });
    }

    return violations;
  }

  private checkRateLimit(walletAddress: string): boolean {
    const rateLimit = this.rateLimits.get(walletAddress);
    if (!rateLimit) return true;

    return rateLimit.currentCount < rateLimit.maxTransactions;
  }

  private updateRateLimit(): void {
    const rateLimit = this.rateLimits.get(this.walletAddress);
    if (rateLimit) {
      rateLimit.currentCount++;
    }
  }

  private categorizeTransaction(tx: SpendingRecord): string {
    // Simplified categorization based on value patterns
    if (tx.value > 1000000000000000000n) { // > 1 ETH
      return 'Large';
    } else if (tx.value > 100000000000000000n) { // > 0.1 ETH
      return 'Medium';
    } else {
      return 'Small';
    }
  }

  private async getPeriodSpending(
    startDate: number,
    endDate: number,
    periodSeconds: number
  ): Promise<bigint> {
    const history = this.history.get(this.walletAddress);
    if (!history) return 0n;

    let total = 0n;
    const periodStart = Math.floor(startDate / periodSeconds) * periodSeconds;

    for (const tx of history.transactions) {
      if (tx.status === 'executed' && 
          tx.timestamp >= periodStart && 
          tx.timestamp < periodStart + periodSeconds) {
        total += tx.value;
      }
    }

    return total;
  }

  private async cleanOldRecords(): Promise<void> {
    const history = this.history.get(this.walletAddress);
    if (!history) return;

    const thirtyDaysAgo = Math.floor(Date.now() / 1000) - (30 * 24 * 60 * 60);
    
    // Keep only recent transactions for performance
    history.transactions = history.transactions.filter(
      tx => tx.timestamp >= thirtyDaysAgo
    );
  }

  private getDefaultLimits(): LimitPeriod {
    const now = Math.floor(Date.now() / 1000);
    
    return {
      daily: { amount: 0n, used: 0n, resetTime: now + 24 * 60 * 60, resetInterval: 24 * 60 * 60 },
      weekly: { amount: 0n, used: 0n, resetTime: now + 7 * 24 * 60 * 60, resetInterval: 7 * 24 * 60 * 60 },
      monthly: { amount: 0n, used: 0n, resetTime: now + 30 * 24 * 60 * 60, resetInterval: 30 * 24 * 60 * 60 },
      single: { amount: 0n, used: 0n, resetTime: now, resetInterval: 1 }
    };
  }

  private getDefaultRateLimit(): RateLimit {
    return {
      window: 3600, // 1 hour
      maxTransactions: 10,
      currentCount: 0,
      windowStart: Math.floor(Date.now() / 1000)
    };
  }

  private convertToCSV(transactions: SpendingRecord[], analytics: any): string {
    const headers = ['ID', 'Value', 'Timestamp', 'Status'];
    const rows = transactions.map(tx => [
      tx.id,
      tx.value.toString(),
      new Date(tx.timestamp * 1000).toISOString(),
      tx.status
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
}