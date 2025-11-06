// GPT Trading Assistant - AI Chat Interface
Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders, status: 200 });
    }

    try {
        const { message, session_id } = await req.json();
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        const authHeader = req.headers.get('authorization');
        let userId = null;
        
        if (authHeader) {
            const token = authHeader.replace('Bearer ', '');
            const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
                headers: { 'Authorization': `Bearer ${token}`, 'apikey': serviceRoleKey }
            });
            if (userResponse.ok) {
                const userData = await userResponse.json();
                userId = userData.id;
            }
        }

        if (!userId) {
            throw new Error('Authentication required');
        }

        // Save user message
        await fetch(
            `${supabaseUrl}/rest/v1/ai_chat_conversations`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    session_id: session_id || crypto.randomUUID(),
                    message_type: 'user',
                    content: message
                })
            }
        );

        // Generate AI response (simplified - production would use actual GPT API)
        let aiResponse = '';
        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes('portfel') || lowerMessage.includes('portfolio')) {
            aiResponse = "Sizning portfelingiz hozirda diversifikatsiya qilingan. BTC 40%, ETH 30%, altcoinlar 30%. Risk-return nisbati yaxshi holatda. Volatillikni kamaytrish uchun stablecoinlar qo'shishni tavsiya etaman.";
        } else if (lowerMessage.includes('strategiya') || lowerMessage.includes('strategy')) {
            aiResponse = "Trading strategiyasi uchun quyidagilarni tavsiya qilaman:\n1. DCA (Dollar Cost Averaging) - barqaror kirim uchun\n2. Momentum trading - trend davomida\n3. Mean reversion - korrektion davrida\nQaysi bozor sharoitida savdo qilmoqchisiz?";
        } else if (lowerMessage.includes('risk') || lowerMessage.includes('xavf')) {
            aiResponse = "Risk boshqaruvi juda muhim. Sizning hozirgi risk darajangiz o'rtacha. Tavsiyalarim:\n- Stop-loss har doim qo'ying (2-3%)\n- Bir treyda kapitalning 1-2% dan ortiq riskga qo'ymang\n- Diversifikatsiya qiling\n- Leverage ehtiyotkorlik bilan ishlating";
        } else if (lowerMessage.includes('signal') || lowerMessage.includes('tavsiya')) {
            aiResponse = "AI tahlilimizga ko'ra:\n- BTC/USDT: BUY signal (ishonch 75%)\n- ETH/USDT: HOLD (neytrал)\n- SOL/USDT: BUY signal (ishonch 68%)\nBatafsil tahlil uchun AI Signals bo'limiga o'ting.";
        } else {
            aiResponse = "Savol uchun rahmat! Men sizga trading, portfel boshqaruvi, risk tahlili va strategiyalar bo'yicha yordam bera olaman. Nimani bilmoqchisiz?";
        }

        // Save AI response
        await fetch(
            `${supabaseUrl}/rest/v1/ai_chat_conversations`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    session_id: session_id || crypto.randomUUID(),
                    message_type: 'assistant',
                    content: aiResponse,
                    model_name: 'gpt-trading-assistant-v1'
                })
            }
        );

        return new Response(JSON.stringify({
            response: aiResponse,
            session_id: session_id || crypto.randomUUID(),
            success: true
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message, success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500
        });
    }
});
