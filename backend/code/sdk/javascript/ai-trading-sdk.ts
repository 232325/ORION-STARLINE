/**
 * AI Trading Evolution - JavaScript/TypeScript SDK
 * ================================================
 * Official JavaScript client library for AI Trading Evolution API
 * 
 * @author MiniMax Agent
 * @version 1.0.0
 * @date 2025-11-04
 * 
 * @example
 * ```javascript
 * import { TradingClient } from 'ai-trading-sdk';
 * 
 * const client = new TradingClient({
 *   baseUrl: 'http://localhost:8000',
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Get market data
 * const data = await client.market.getData('BTC/USDT');
 * 
 * // Execute strategy
 * const signal = await client.strategy.execute('grid', 'BTC/USDT');
 * 
 * // Run analytics
 * const sentiment = await client.analytics.sentiment('BTC/USDT');
 * ```
 */

// =============================================================================
// Types
// =============================================================================

export interface ClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
}

export interface MarketDataRequest {
  symbol: string;
  market_type?: 'crypto' | 'forex' | 'stocks' | 'commodities';
  timeframe?: string;
  limit?: number;
}

export interface StrategyRequest {
  strategy_name: string;
  symbol: string;
  timeframe?: string;
  parameters?: Record<string, any>;
}

export interface AnalyticsRequest {
  analysis_type: string;
  symbol?: string;
  parameters?: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  uptime: number;
  modules: Record<string, any>;
}

export interface StrategyResponse {
  strategy_name: string;
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  price: number;
  entry_price?: number;
  stop_loss?: number;
  take_profit?: number;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface WebSocketMessage {
  action: 'subscribe' | 'unsubscribe' | 'ping' | 'get_stats';
  channel?: string;
}

// =============================================================================
// API Error
// =============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// =============================================================================
// Base Client
// =============================================================================

class BaseClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(config: ClientConfig = {}) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 30000;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, string>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new APIError(
          `API Error ${response.status}: ${error.error || 'Unknown error'}`,
          response.status,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      if (error.name === 'AbortError') {
        throw new APIError('Request timeout');
      }
      throw new APIError(`Connection error: ${error.message}`);
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>('GET', endpoint, undefined, params);
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }
}

// =============================================================================
// Market API
// =============================================================================

export class MarketAPI {
  constructor(private client: BaseClient) {}

  /**
   * Get market data
   */
  async getData(
    symbol: string,
    options: Partial<MarketDataRequest> = {}
  ): Promise<any> {
    return this.client.post('/api/v1/market/data', {
      symbol,
      market_type: options.market_type || 'crypto',
      timeframe: options.timeframe || '1h',
      limit: options.limit || 100,
    });
  }

  /**
   * Get list of available symbols
   */
  async listSymbols(marketType: string = 'crypto'): Promise<any> {
    return this.client.get('/api/v1/market/symbols', { market_type: marketType });
  }
}

// =============================================================================
// Strategy API
// =============================================================================

export class StrategyAPI {
  constructor(private client: BaseClient) {}

  /**
   * Execute trading strategy
   */
  async execute(
    strategyName: string,
    symbol: string,
    options: Partial<StrategyRequest> = {}
  ): Promise<StrategyResponse> {
    return this.client.post<StrategyResponse>('/api/v1/strategy/execute', {
      strategy_name: strategyName,
      symbol,
      timeframe: options.timeframe || '1h',
      parameters: options.parameters || {},
    });
  }

  /**
   * Get list of available strategies
   */
  async list(): Promise<any> {
    return this.client.get('/api/v1/strategy/list');
  }
}

// =============================================================================
// Analytics API
// =============================================================================

export class AnalyticsAPI {
  constructor(private client: BaseClient) {}

  /**
   * Run analytics
   */
  async analyze(
    analysisType: string,
    symbol?: string,
    parameters?: Record<string, any>
  ): Promise<any> {
    return this.client.post('/api/v1/analytics/analyze', {
      analysis_type: analysisType,
      symbol,
      parameters: parameters || {},
    });
  }

  /**
   * Get sentiment analysis
   */
  async sentiment(symbol: string): Promise<any> {
    return this.analyze('sentiment', symbol);
  }

  /**
   * Get risk scoring
   */
  async riskScoring(symbol: string): Promise<any> {
    return this.analyze('risk_scoring', symbol);
  }

  /**
   * Get list of analytics types
   */
  async listTypes(): Promise<any> {
    return this.client.get('/api/v1/analytics/types');
  }
}

// =============================================================================
// WebSocket Client
// =============================================================================

export class WebSocketClient {
  private ws?: WebSocket;
  private clientId?: string;
  private subscriptions: Set<string> = new Set();
  private messageHandlers: Map<string, Function[]> = new Map();

  constructor(private baseUrl: string) {
    this.baseUrl = baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  /**
   * Connect to WebSocket
   */
  async connect(clientId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.clientId = clientId || this.generateClientId();
      const url = `${this.baseUrl}/ws/${this.clientId}`;

      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'welcome') {
          resolve();
        }
        
        // Trigger handlers
        const handlers = this.messageHandlers.get(message.type) || [];
        handlers.forEach(handler => handler(message));
        
        // Trigger channel handlers
        if (message.channel) {
          const channelHandlers = this.messageHandlers.get(message.channel) || [];
          channelHandlers.forEach(handler => handler(message));
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
    });
  }

  /**
   * Subscribe to channel
   */
  async subscribe(channel: string, handler?: Function): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.send({
      action: 'subscribe',
      channel,
    });

    this.subscriptions.add(channel);

    if (handler) {
      this.on(channel, handler);
    }
  }

  /**
   * Unsubscribe from channel
   */
  async unsubscribe(channel: string): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.send({
      action: 'unsubscribe',
      channel,
    });

    this.subscriptions.delete(channel);
    this.messageHandlers.delete(channel);
  }

  /**
   * Send message
   */
  send(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Register message handler
   */
  on(event: string, handler: Function): void {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, []);
    }
    this.messageHandlers.get(event)!.push(handler);
  }

  /**
   * Send ping
   */
  async ping(): Promise<void> {
    this.send({ action: 'ping' });
  }

  /**
   * Close connection
   */
  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  private generateClientId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

// =============================================================================
// Main Trading Client
// =============================================================================

/**
 * Main AI Trading Evolution client
 * 
 * @example
 * ```typescript
 * const client = new TradingClient({
 *   baseUrl: 'http://localhost:8000',
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Get market data
 * const data = await client.market.getData('BTC/USDT');
 * 
 * // Execute strategy
 * const signal = await client.strategy.execute('grid', 'BTC/USDT');
 * 
 * // Run analytics
 * const sentiment = await client.analytics.sentiment('BTC/USDT');
 * 
 * // WebSocket
 * const ws = client.websocket();
 * await ws.connect();
 * await ws.subscribe('market:BTC/USDT', (message) => {
 *   console.log('Market update:', message);
 * });
 * ```
 */
export class TradingClient {
  private _baseClient: BaseClient;

  public readonly market: MarketAPI;
  public readonly strategy: StrategyAPI;
  public readonly analytics: AnalyticsAPI;

  constructor(config: ClientConfig = {}) {
    this._baseClient = new BaseClient(config);

    // Initialize API endpoints
    this.market = new MarketAPI(this._baseClient);
    this.strategy = new StrategyAPI(this._baseClient);
    this.analytics = new AnalyticsAPI(this._baseClient);
  }

  /**
   * Get API health status
   */
  async health(): Promise<HealthResponse> {
    return this._baseClient.get<HealthResponse>('/health');
  }

  /**
   * Get performance metrics
   */
  async metrics(): Promise<any> {
    return this._baseClient.get('/metrics');
  }

  /**
   * Get WebSocket client
   */
  websocket(): WebSocketClient {
    return new WebSocketClient(this._baseClient.getBaseUrl());
  }
}

// =============================================================================
// Export all
// =============================================================================

export default TradingClient;
