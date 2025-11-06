/**
 * GPT-4 Turbo Advanced Trading Assistant Edge Function
 * Purpose: Natural Language Trading + Voice Commands + Intelligent Analysis
 * Phase: 2 - Advanced AI Integration
 * Features:
 *  - Natural language processing for trading commands
 *  - Voice-to-text integration support
 *  - Intelligent market recommendations
 *  - Real-time analysis and insights
 *  - Multi-turn conversations with context
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
        const { 
            action, 
            userId, 
            message, 
            conversationId,
            voiceInput,
            context 
        } = await req.json();

        if (!userId) {
            throw new Error('User ID is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const openaiApiKey = Deno.env.get('OPENAI_API_KEY');

        if (!openaiApiKey) {
            throw new Error('OpenAI API key not configured');
        }

        let result: any = {};

        switch (action) {
            case 'chat':
                result = await handleChatMessage(
                    supabaseUrl!,
                    serviceRoleKey!,
                    openaiApiKey,
                    userId,
                    message,
                    conversationId,
                    context
                );
                break;

            case 'voice_command':
                result = await handleVoiceCommand(
                    supabaseUrl!,
                    serviceRoleKey!,
                    openaiApiKey,
                    userId,
                    voiceInput,
                    context
                );
                break;

            case 'analyze_market':
                result = await analyzeMarketWithGPT4(
                    supabaseUrl!,
                    serviceRoleKey!,
                    openaiApiKey,
                    userId,
                    message,
                    context
                );
                break;

            case 'trading_recommendation':
                result = await getTradingRecommendation(
                    supabaseUrl!,
                    serviceRoleKey!,
                    openaiApiKey,
                    userId,
                    context
                );
                break;

            case 'parse_trading_command':
                result = await parseTradingCommand(
                    openaiApiKey,
                    message
                );
                break;

            default:
                throw new Error('Invalid action specified');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('GPT-4 Advanced Assistant error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'GPT4_ASSISTANT_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Handle chat message with GPT-4 Turbo
 */
async function handleChatMessage(
    supabaseUrl: string,
    serviceRoleKey: string,
    openaiApiKey: string,
    userId: string,
    message: string,
    conversationId?: string,
    context?: any
): Promise<any> {
    // Get conversation history if conversationId provided
    let conversationHistory: any[] = [];
    
    if (conversationId) {
        const historyResponse = await fetch(
            `${supabaseUrl}/rest/v1/ai_conversations?conversation_id=eq.${conversationId}&order=timestamp.asc&limit=10`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );
        const history = await historyResponse.json();
        
        if (Array.isArray(history)) {
            conversationHistory = history.map(h => ({
                role: h.role,
                content: h.content
            }));
        }
    }

    // Build system prompt with context
    const systemPrompt = buildSystemPrompt(context);

    // Prepare messages for GPT-4
    const messages = [
        { role: 'system', content: systemPrompt },
        ...conversationHistory,
        { role: 'user', content: message }
    ];

    // Call GPT-4 Turbo
    const gptResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openaiApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'gpt-4-turbo-preview',
            messages: messages,
            max_tokens: 1000,
            temperature: 0.7,
            functions: getTradingFunctions()
        })
    });

    const gptData = await gptResponse.json();

    if (gptData.error) {
        throw new Error(`OpenAI API error: ${gptData.error.message}`);
    }

    const assistantMessage = gptData.choices[0].message;
    const functionCall = assistantMessage.function_call;

    // Save conversation to database
    const newConversationId = conversationId || generateConversationId();
    
    await saveConversationMessage(
        supabaseUrl,
        serviceRoleKey,
        newConversationId,
        userId,
        'user',
        message
    );
    
    await saveConversationMessage(
        supabaseUrl,
        serviceRoleKey,
        newConversationId,
        userId,
        'assistant',
        assistantMessage.content || 'Function call initiated'
    );

    return {
        conversationId: newConversationId,
        message: assistantMessage.content,
        functionCall: functionCall,
        usage: gptData.usage
    };
}

/**
 * Handle voice command
 */
async function handleVoiceCommand(
    supabaseUrl: string,
    serviceRoleKey: string,
    openaiApiKey: string,
    userId: string,
    voiceInput: string,
    context?: any
): Promise<any> {
    // Voice input is already transcribed text
    // Parse it as a trading command
    const parsedCommand = await parseTradingCommand(openaiApiKey, voiceInput);

    // Log voice command
    await fetch(`${supabaseUrl}/rest/v1/voice_commands`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            command_text: voiceInput,
            parsed_action: parsedCommand.action,
            parameters: parsedCommand.parameters,
            confidence: parsedCommand.confidence
        })
    });

    return {
        originalCommand: voiceInput,
        parsedCommand: parsedCommand,
        response: generateVoiceResponse(parsedCommand)
    };
}

/**
 * Analyze market with GPT-4
 */
async function analyzeMarketWithGPT4(
    supabaseUrl: string,
    serviceRoleKey: string,
    openaiApiKey: string,
    userId: string,
    query: string,
    context?: any
): Promise<any> {
    // Get market data context
    const marketContext = await getMarketContext(supabaseUrl, serviceRoleKey, context);

    const systemPrompt = `You are an expert financial analyst and trading advisor.
Analyze the following market data and provide insights.

Current Market Context:
${JSON.stringify(marketContext, null, 2)}

Provide:
1. Technical analysis
2. Fundamental insights
3. Risk assessment
4. Trading opportunities
5. Recommended actions`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openaiApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'gpt-4-turbo-preview',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: query }
            ],
            max_tokens: 2000,
            temperature: 0.5
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(`OpenAI API error: ${data.error.message}`);
    }

    const analysis = data.choices[0].message.content;

    // Save analysis
    await fetch(`${supabaseUrl}/rest/v1/gpt4_market_analysis`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            analysis_type: 'comprehensive',
            query: query,
            analysis_result: analysis,
            market_context: marketContext
        })
    });

    return {
        analysis: analysis,
        marketContext: marketContext,
        timestamp: new Date().toISOString()
    };
}

/**
 * Get trading recommendation
 */
async function getTradingRecommendation(
    supabaseUrl: string,
    serviceRoleKey: string,
    openaiApiKey: string,
    userId: string,
    context?: any
): Promise<any> {
    // Get user portfolio
    const portfolioResponse = await fetch(
        `${supabaseUrl}/rest/v1/portfolios?user_id=eq.${userId}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );
    const portfolio = await portfolioResponse.json();

    // Get market trends
    const marketData = await getMarketContext(supabaseUrl, serviceRoleKey, context);

    const systemPrompt = `You are a professional trading advisor.
Based on the user's portfolio and current market conditions, provide personalized trading recommendations.

User Portfolio: ${JSON.stringify(portfolio)}
Market Data: ${JSON.stringify(marketData)}

Provide:
1. Top 3 trading opportunities
2. Risk level for each
3. Entry/exit points
4. Position sizing recommendations
5. Stop-loss levels`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openaiApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'gpt-4-turbo-preview',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: 'What are your top trading recommendations for me today?' }
            ],
            max_tokens: 1500,
            temperature: 0.6
        })
    });

    const data = await response.json();

    return {
        recommendations: data.choices[0].message.content,
        portfolio: portfolio,
        marketData: marketData,
        timestamp: new Date().toISOString()
    };
}

/**
 * Parse trading command using GPT-4
 */
async function parseTradingCommand(
    openaiApiKey: string,
    command: string
): Promise<any> {
    const systemPrompt = `You are a trading command parser. 
Extract trading actions from natural language.

Return JSON with:
{
  "action": "buy" | "sell" | "check" | "analyze" | "unknown",
  "symbol": "stock symbol if mentioned",
  "quantity": number,
  "amount": number in USD,
  "price": specific price if mentioned,
  "orderType": "market" | "limit",
  "confidence": 0-1,
  "parameters": {}
}

Examples:
"Buy 100 shares of Apple" -> {"action": "buy", "symbol": "AAPL", "quantity": 100}
"Sell all my Tesla stock" -> {"action": "sell", "symbol": "TSLA", "quantity": "all"}
"What's the price of Bitcoin?" -> {"action": "check", "symbol": "BTC"}`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openaiApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'gpt-4-turbo-preview',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: command }
            ],
            response_format: { type: 'json_object' },
            max_tokens: 300,
            temperature: 0.3
        })
    });

    const data = await response.json();
    
    if (data.error) {
        return {
            action: 'unknown',
            confidence: 0,
            error: data.error.message
        };
    }

    return JSON.parse(data.choices[0].message.content);
}

// Helper functions

function buildSystemPrompt(context?: any): string {
    return `You are Orion Starline AI Trading Assistant, powered by GPT-4 Turbo.
You help users with:
- Trading decisions and market analysis
- Portfolio management
- Risk assessment
- Technical and fundamental analysis
- Natural language trading commands

Always be:
- Professional and accurate
- Risk-aware
- Clear and concise
- Helpful and educational

Current context: ${context ? JSON.stringify(context) : 'None'}`;
}

function getTradingFunctions(): any[] {
    return [
        {
            name: 'execute_trade',
            description: 'Execute a trading order',
            parameters: {
                type: 'object',
                properties: {
                    action: {
                        type: 'string',
                        enum: ['buy', 'sell'],
                        description: 'Trading action'
                    },
                    symbol: {
                        type: 'string',
                        description: 'Stock/crypto symbol'
                    },
                    quantity: {
                        type: 'number',
                        description: 'Number of shares/units'
                    },
                    orderType: {
                        type: 'string',
                        enum: ['market', 'limit'],
                        description: 'Order type'
                    }
                },
                required: ['action', 'symbol', 'quantity']
            }
        },
        {
            name: 'check_price',
            description: 'Check current price of an asset',
            parameters: {
                type: 'object',
                properties: {
                    symbol: {
                        type: 'string',
                        description: 'Asset symbol'
                    }
                },
                required: ['symbol']
            }
        }
    ];
}

function generateConversationId(): string {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

async function saveConversationMessage(
    supabaseUrl: string,
    serviceRoleKey: string,
    conversationId: string,
    userId: string,
    role: string,
    content: string
): Promise<void> {
    await fetch(`${supabaseUrl}/rest/v1/ai_conversations`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            conversation_id: conversationId,
            user_id: userId,
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        })
    });
}

async function getMarketContext(
    supabaseUrl: string,
    serviceRoleKey: string,
    context?: any
): Promise<any> {
    // Get recent prices
    const pricesResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?order=timestamp.desc&limit=10`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );
    
    let prices = await pricesResponse.json();
    if (!Array.isArray(prices)) {
        prices = [];
    }

    return {
        currentPrices: prices,
        timestamp: new Date().toISOString(),
        additionalContext: context || {}
    };
}

function generateVoiceResponse(parsedCommand: any): string {
    const { action, symbol, quantity } = parsedCommand;
    
    if (action === 'buy') {
        return `I understand you want to buy ${quantity} shares of ${symbol}. Would you like to proceed with this market order?`;
    } else if (action === 'sell') {
        return `I understand you want to sell ${quantity} shares of ${symbol}. Shall I execute this sell order?`;
    } else if (action === 'check') {
        return `Let me check the current price of ${symbol} for you.`;
    } else {
        return `I'm not sure I understood that command. Could you please rephrase?`;
    }
}
