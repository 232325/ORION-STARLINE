/**
 * Advanced Risk Management System Edge Function
 * Purpose: Portfolio risk assessment, dynamic stop-loss, stress testing
 * Phase: 3 - Risk Management
 */

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, userId, portfolioId, positionId, ...params } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'assess_portfolio_risk':
                result = await assessPortfolioRisk(supabaseUrl!, serviceRoleKey!, userId, portfolioId);
                break;
            case 'calculate_var':
                result = await calculateValueAtRisk(supabaseUrl!, serviceRoleKey!, portfolioId, params);
                break;
            case 'stress_test':
                result = await performStressTest(supabaseUrl!, serviceRoleKey!, portfolioId, params.scenarios);
                break;
            case 'set_dynamic_stoploss':
                result = await setDynamicStopLoss(supabaseUrl!, serviceRoleKey!, positionId, params);
                break;
            case 'get_risk_metrics':
                result = await getRiskMetrics(supabaseUrl!, serviceRoleKey!, userId);
                break;
            case 'risk_alert_check':
                result = await checkRiskAlerts(supabaseUrl!, serviceRoleKey!, userId);
                break;
            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        return new Response(JSON.stringify({
            error: { code: 'RISK_MANAGEMENT_ERROR', message: error.message }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Assess overall portfolio risk
 */
async function assessPortfolioRisk(url: string, key: string, userId: string, portfolioId: string) {
    // Get portfolio positions
    const positionsResp = await fetch(`${url}/rest/v1/positions?portfolio_id=eq.${portfolioId}&is_open=eq.true`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let positions = await positionsResp.json();
    if (!Array.isArray(positions)) positions = [];

    // Calculate portfolio metrics
    let totalValue = 0;
    let totalRisk = 0;
    const assetAllocation: any = {};
    const sectorExposure: any = {};

    for (const pos of positions) {
        const value = parseFloat(pos.current_value || 0);
        totalValue += value;
        
        // Asset allocation
        const assetType = pos.asset_type || 'unknown';
        assetAllocation[assetType] = (assetAllocation[assetType] || 0) + value;
        
        // Calculate position risk (volatility * position size)
        const volatility = parseFloat(pos.volatility || 0.2);
        const positionRisk = value * volatility;
        totalRisk += positionRisk;
    }

    // Calculate concentration risk
    const maxPositionSize = Math.max(...positions.map((p: any) => parseFloat(p.current_value || 0)));
    const concentrationRisk = totalValue > 0 ? (maxPositionSize / totalValue) : 0;

    // Risk score (0-100)
    let riskScore = 0;
    riskScore += concentrationRisk * 30; // Concentration contributes 30%
    riskScore += (totalRisk / totalValue) * 50; // Volatility contributes 50%
    riskScore += (positions.length > 20 ? 0 : (20 - positions.length)) * 1; // Diversification 20%
    
    const riskLevel = riskScore < 30 ? 'LOW' : riskScore < 60 ? 'MEDIUM' : riskScore < 80 ? 'HIGH' : 'CRITICAL';

    // Save risk assessment
    await fetch(`${url}/rest/v1/risk_assessments`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            portfolio_id: portfolioId,
            risk_score: riskScore,
            risk_level: riskLevel,
            total_value: totalValue,
            concentration_risk: concentrationRisk,
            asset_allocation: assetAllocation,
            sector_exposure: sectorExposure,
            assessed_at: new Date().toISOString()
        })
    });

    return {
        riskScore,
        riskLevel,
        totalValue,
        concentrationRisk,
        assetAllocation,
        positions: positions.length,
        recommendations: generateRiskRecommendations(riskScore, concentrationRisk)
    };
}

/**
 * Calculate Value at Risk (VaR)
 */
async function calculateValueAtRisk(url: string, key: string, portfolioId: string, params: any) {
    const confidenceLevel = params.confidenceLevel || 0.95;
    const timeHorizon = params.timeHorizon || 1; // days

    // Get historical returns
    const returnsResp = await fetch(`${url}/rest/v1/portfolio_returns?portfolio_id=eq.${portfolioId}&order=date.desc&limit=252`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let returns = await returnsResp.json();
    if (!Array.isArray(returns)) returns = [];

    if (returns.length < 30) {
        return {
            var: 0,
            cvar: 0,
            message: 'Insufficient historical data for VaR calculation'
        };
    }

    // Calculate historical VaR
    const returnValues = returns.map((r: any) => parseFloat(r.daily_return || 0)).sort((a, b) => a - b);
    const varIndex = Math.floor((1 - confidenceLevel) * returnValues.length);
    const var95 = Math.abs(returnValues[varIndex]);

    // Calculate Conditional VaR (Expected Shortfall)
    const tailReturns = returnValues.slice(0, varIndex);
    const cvar = tailReturns.length > 0 
        ? Math.abs(tailReturns.reduce((sum, val) => sum + val, 0) / tailReturns.length)
        : var95;

    // Get current portfolio value
    const portfolioResp = await fetch(`${url}/rest/v1/portfolios?id=eq.${portfolioId}`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    const portfolioData = await portfolioResp.json();
    const portfolioValue = Array.isArray(portfolioData) && portfolioData[0] 
        ? parseFloat(portfolioData[0].total_value || 0) 
        : 0;

    const varAmount = portfolioValue * var95;
    const cvarAmount = portfolioValue * cvar;

    return {
        var: var95 * 100, // percentage
        varAmount,
        cvar: cvar * 100,
        cvarAmount,
        confidenceLevel: confidenceLevel * 100,
        timeHorizon,
        interpretation: `With ${confidenceLevel * 100}% confidence, portfolio will not lose more than $${varAmount.toFixed(2)} in ${timeHorizon} day(s)`
    };
}

/**
 * Perform stress testing on portfolio
 */
async function performStressTest(url: string, key: string, portfolioId: string, scenarios: any[]) {
    // Default scenarios if none provided
    const defaultScenarios = [
        { name: 'Market Crash', marketDrop: -0.20, volatilityIncrease: 2.0 },
        { name: 'Interest Rate Shock', marketDrop: -0.10, volatilityIncrease: 1.5 },
        { name: 'Black Swan Event', marketDrop: -0.35, volatilityIncrease: 3.0 },
        { name: 'Moderate Correction', marketDrop: -0.15, volatilityIncrease: 1.3 }
    ];

    const testScenarios = scenarios && scenarios.length > 0 ? scenarios : defaultScenarios;

    // Get current portfolio
    const positionsResp = await fetch(`${url}/rest/v1/positions?portfolio_id=eq.${portfolioId}&is_open=eq.true`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let positions = await positionsResp.json();
    if (!Array.isArray(positions)) positions = [];

    const currentValue = positions.reduce((sum: number, p: any) => sum + parseFloat(p.current_value || 0), 0);

    // Run stress tests
    const results = testScenarios.map(scenario => {
        let stressedValue = 0;
        
        for (const pos of positions) {
            const posValue = parseFloat(pos.current_value || 0);
            const beta = parseFloat(pos.beta || 1.0);
            
            // Apply scenario
            const expectedLoss = posValue * scenario.marketDrop * beta;
            stressedValue += (posValue + expectedLoss);
        }

        const loss = currentValue - stressedValue;
        const lossPercentage = (loss / currentValue) * 100;

        return {
            scenario: scenario.name,
            currentValue,
            stressedValue,
            loss,
            lossPercentage: lossPercentage.toFixed(2) + '%',
            severity: lossPercentage < 10 ? 'LOW' : lossPercentage < 25 ? 'MEDIUM' : 'HIGH'
        };
    });

    return {
        portfolioId,
        stressTestDate: new Date().toISOString(),
        scenarios: results,
        worstCase: results.reduce((worst, current) => 
            current.loss > worst.loss ? current : worst
        )
    };
}

/**
 * Set dynamic stop-loss based on volatility
 */
async function setDynamicStopLoss(url: string, key: string, positionId: string, params: any) {
    const atrMultiplier = params.atrMultiplier || 2.0;
    const trailingPercent = params.trailingPercent || 5;

    // Get position details
    const posResp = await fetch(`${url}/rest/v1/positions?id=eq.${positionId}`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    const posData = await posResp.json();
    if (!Array.isArray(posData) || posData.length === 0) {
        throw new Error('Position not found');
    }

    const position = posData[0];
    const currentPrice = parseFloat(position.current_price || position.entry_price || 0);
    const entryPrice = parseFloat(position.entry_price || currentPrice);

    // Calculate ATR-based stop-loss
    const atr = parseFloat(position.atr || currentPrice * 0.02); // 2% default ATR
    const atrStopLoss = currentPrice - (atr * atrMultiplier);

    // Calculate trailing stop-loss
    const highestPrice = Math.max(currentPrice, parseFloat(position.highest_price || currentPrice));
    const trailingStopLoss = highestPrice * (1 - trailingPercent / 100);

    // Use the higher stop-loss (less aggressive)
    const finalStopLoss = Math.max(atrStopLoss, trailingStopLoss);

    // Update position with dynamic stop-loss
    await fetch(`${url}/rest/v1/positions?id=eq.${positionId}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            stop_loss: finalStopLoss,
            highest_price: highestPrice,
            stop_loss_type: 'dynamic',
            updated_at: new Date().toISOString()
        })
    });

    return {
        positionId,
        currentPrice,
        stopLoss: finalStopLoss,
        atrStopLoss,
        trailingStopLoss,
        protectionAmount: currentPrice - finalStopLoss,
        protectionPercent: ((currentPrice - finalStopLoss) / currentPrice * 100).toFixed(2) + '%'
    };
}

/**
 * Get comprehensive risk metrics
 */
async function getRiskMetrics(url: string, key: string, userId: string) {
    // Get all user portfolios
    const portfoliosResp = await fetch(`${url}/rest/v1/portfolios?user_id=eq.${userId}`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let portfolios = await portfoliosResp.json();
    if (!Array.isArray(portfolios)) portfolios = [];

    const metrics = {
        totalValue: 0,
        totalRisk: 0,
        averageRiskScore: 0,
        portfoliosAtRisk: 0,
        recommendations: []
    };

    for (const portfolio of portfolios) {
        const riskAssessment = await assessPortfolioRisk(url, key, userId, portfolio.id);
        metrics.totalValue += riskAssessment.totalValue;
        metrics.averageRiskScore += riskAssessment.riskScore;
        if (riskAssessment.riskLevel === 'HIGH' || riskAssessment.riskLevel === 'CRITICAL') {
            metrics.portfoliosAtRisk++;
        }
    }

    if (portfolios.length > 0) {
        metrics.averageRiskScore /= portfolios.length;
    }

    return metrics;
}

/**
 * Check for risk alerts
 */
async function checkRiskAlerts(url: string, key: string, userId: string) {
    const alerts: any[] = [];

    // Get recent risk assessments
    const assessmentsResp = await fetch(
        `${url}/rest/v1/risk_assessments?user_id=eq.${userId}&order=assessed_at.desc&limit=10`,
        { headers: { 'Authorization': `Bearer ${key}`, 'apikey': key } }
    );
    let assessments = await assessmentsResp.json();
    if (!Array.isArray(assessments)) assessments = [];

    for (const assessment of assessments) {
        if (assessment.risk_level === 'CRITICAL') {
            alerts.push({
                type: 'CRITICAL_RISK',
                message: `Portfolio ${assessment.portfolio_id} has critical risk level`,
                riskScore: assessment.risk_score,
                action: 'Immediate review required'
            });
        }
        
        if (assessment.concentration_risk > 0.3) {
            alerts.push({
                type: 'CONCENTRATION_RISK',
                message: 'High concentration in single position',
                concentration: (assessment.concentration_risk * 100).toFixed(1) + '%',
                action: 'Diversify portfolio'
            });
        }
    }

    return { alerts, alertCount: alerts.length };
}

/**
 * Generate risk recommendations
 */
function generateRiskRecommendations(riskScore: number, concentrationRisk: number): string[] {
    const recommendations: string[] = [];

    if (riskScore > 70) {
        recommendations.push('Consider reducing overall portfolio risk');
        recommendations.push('Increase allocation to defensive assets');
    }

    if (concentrationRisk > 0.25) {
        recommendations.push('Diversify portfolio to reduce concentration risk');
        recommendations.push('No single position should exceed 25% of portfolio');
    }

    if (riskScore < 30) {
        recommendations.push('Portfolio is well-balanced with low risk');
        recommendations.push('Consider opportunities for controlled growth');
    }

    return recommendations;
}
