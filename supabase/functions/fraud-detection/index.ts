/**
 * Fraud Detection Engine Edge Function
 * Purpose: Detect and prevent fraudulent trading activities
 * Directive: E) Advanced Security & Monitoring
 */

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, userId, transactionData, sessionData } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'analyze_transaction':
                result = await analyzeTransaction(supabaseUrl!, serviceRoleKey!, userId, transactionData);
                break;

            case 'check_session':
                result = await checkSessionAnomaly(supabaseUrl!, serviceRoleKey!, userId, sessionData);
                break;

            case 'get_alerts':
                result = await getFraudAlerts(supabaseUrl!, serviceRoleKey!, userId);
                break;

            case 'review_alert':
                const { alertId, status, notes } = await req.json();
                result = await reviewFraudAlert(supabaseUrl!, serviceRoleKey!, alertId, status, notes);
                break;

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Fraud Detection error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'FRAUD_DETECTION_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Analyze transaction for fraud indicators
 */
async function analyzeTransaction(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    transactionData: any
): Promise<any> {
    const indicators: any[] = [];
    let riskScore = 0;

    // Check 1: Unusual transaction amount
    if (transactionData.amount > 10000) {
        indicators.push({
            type: 'large_transaction',
            description: 'Transaction amount exceeds normal threshold',
            severity: 'medium'
        });
        riskScore += 0.3;
    }

    // Check 2: Rapid successive transactions
    const recentTxResponse = await fetch(
        `${supabaseUrl}/rest/v1/comprehensive_audit_logs?user_id=eq.${userId}&action=eq.trade_executed&created_at=gte.${new Date(Date.now() - 300000).toISOString()}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const recentTransactions = await recentTxResponse.json();

    if (recentTransactions.length > 5) {
        indicators.push({
            type: 'rapid_trading',
            description: `${recentTransactions.length} transactions in 5 minutes`,
            severity: 'high'
        });
        riskScore += 0.4;
    }

    // Check 3: Unusual trading pattern
    if (transactionData.symbol && isUnusualSymbol(transactionData.symbol)) {
        indicators.push({
            type: 'unusual_asset',
            description: 'Trading in unusual or high-risk asset',
            severity: 'medium'
        });
        riskScore += 0.2;
    }

    // Check 4: IP address change
    const sessionsResponse = await fetch(
        `${supabaseUrl}/rest/v1/security_sessions?user_id=eq.${userId}&is_active=eq.true&order=created_at.desc&limit=2`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const sessions = await sessionsResponse.json();

    if (sessions.length >= 2 && sessions[0].ip_address !== sessions[1].ip_address) {
        indicators.push({
            type: 'ip_address_change',
            description: 'Transaction from different IP address',
            severity: 'high'
        });
        riskScore += 0.3;
    }

    // Determine alert type
    let alertType = 'normal';
    if (riskScore >= 0.7) {
        alertType = 'money_laundering';
    } else if (indicators.some(i => i.type === 'rapid_trading')) {
        alertType = 'unusual_trading';
    } else if (indicators.some(i => i.type === 'ip_address_change')) {
        alertType = 'account_takeover';
    }

    // Create fraud alert if risk is high
    if (riskScore >= 0.5) {
        await fetch(`${supabaseUrl}/rest/v1/fraud_detection_alerts`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                alert_type: alertType,
                risk_score: riskScore,
                indicators,
                status: 'pending'
            })
        });

        // Log security event
        await fetch(`${supabaseUrl}/rest/v1/security_events`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                event_type: 'fraud_alert_created',
                severity: riskScore >= 0.7 ? 'critical' : 'high',
                details: { riskScore, indicators, transaction: transactionData }
            })
        });
    }

    return {
        userId,
        riskScore: riskScore.toFixed(2),
        riskLevel: riskScore >= 0.7 ? 'CRITICAL' : riskScore >= 0.5 ? 'HIGH' : riskScore >= 0.3 ? 'MEDIUM' : 'LOW',
        indicators,
        alertCreated: riskScore >= 0.5,
        recommendation: riskScore >= 0.7 ? 'Block transaction and review' : 
                       riskScore >= 0.5 ? 'Require additional verification' : 
                       'Allow with monitoring'
    };
}

/**
 * Check session for anomalies
 */
async function checkSessionAnomaly(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    sessionData: any
): Promise<any> {
    const anomalies: any[] = [];
    let suspicionScore = 0;

    // Get user's historical sessions
    const historicalResponse = await fetch(
        `${supabaseUrl}/rest/v1/security_sessions?user_id=eq.${userId}&order=created_at.desc&limit=10`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const historicalSessions = await historicalResponse.json();

    // Check 1: New device
    const knownDevices = historicalSessions.map((s: any) => s.device_fingerprint);
    if (sessionData.deviceFingerprint && !knownDevices.includes(sessionData.deviceFingerprint)) {
        anomalies.push({
            type: 'new_device',
            description: 'Login from unrecognized device'
        });
        suspicionScore += 0.3;
    }

    // Check 2: Unusual location
    if (sessionData.location && !isKnownLocation(historicalSessions, sessionData.location)) {
        anomalies.push({
            type: 'unusual_location',
            description: `Login from ${sessionData.location.country}`
        });
        suspicionScore += 0.4;
    }

    // Check 3: Impossible travel
    if (historicalSessions.length > 0) {
        const lastSession = historicalSessions[0];
        const timeDiff = new Date().getTime() - new Date(lastSession.last_activity_at).getTime();
        const hoursDiff = timeDiff / (1000 * 60 * 60);

        if (hoursDiff < 2 && sessionData.location && lastSession.location) {
            // Different locations within 2 hours - impossible travel
            anomalies.push({
                type: 'impossible_travel',
                description: 'Location changed too quickly'
            });
            suspicionScore += 0.6;
        }
    }

    // Create security event if suspicious
    if (suspicionScore >= 0.5) {
        await fetch(`${supabaseUrl}/rest/v1/security_events`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                event_type: 'suspicious_activity',
                severity: suspicionScore >= 0.7 ? 'critical' : 'high',
                details: { suspicionScore, anomalies, session: sessionData }
            })
        });
    }

    return {
        userId,
        suspicionScore: suspicionScore.toFixed(2),
        anomalies,
        recommendation: suspicionScore >= 0.7 ? 'Require 2FA verification' :
                       suspicionScore >= 0.5 ? 'Send security notification' :
                       'Monitor session'
    };
}

/**
 * Get fraud alerts for user or admin
 */
async function getFraudAlerts(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId?: string
): Promise<any> {
    let url = `${supabaseUrl}/rest/v1/fraud_detection_alerts?order=created_at.desc&limit=50`;
    
    if (userId) {
        url += `&user_id=eq.${userId}`;
    }

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const alerts = await response.json();

    return {
        alerts,
        total: alerts.length,
        pending: alerts.filter((a: any) => a.status === 'pending').length,
        confirmed: alerts.filter((a: any) => a.status === 'confirmed').length,
        falsePositives: alerts.filter((a: any) => a.status === 'false_positive').length
    };
}

/**
 * Review and update fraud alert status
 */
async function reviewFraudAlert(
    supabaseUrl: string,
    serviceRoleKey: string,
    alertId: string,
    status: string,
    notes: string
): Promise<any> {
    await fetch(`${supabaseUrl}/rest/v1/fraud_detection_alerts?id=eq.${alertId}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status,
            notes,
            reviewed_at: new Date().toISOString()
        })
    });

    return {
        success: true,
        alertId,
        status,
        message: `Alert ${status === 'confirmed' ? 'confirmed as fraud' : status === 'false_positive' ? 'marked as false positive' : 'updated'}`
    };
}

/**
 * Check if symbol is unusual or high-risk
 */
function isUnusualSymbol(symbol: string): boolean {
    const highRiskPatterns = ['DOGE', 'SHIB', 'PEPE', 'PUMP', 'MOON'];
    return highRiskPatterns.some(pattern => symbol.toUpperCase().includes(pattern));
}

/**
 * Check if location is known for the user
 */
function isKnownLocation(sessions: any[], location: any): boolean {
    if (!location || !location.country) return true;
    
    const knownCountries = sessions
        .filter((s: any) => s.location?.country)
        .map((s: any) => s.location.country);
    
    return knownCountries.includes(location.country);
}
