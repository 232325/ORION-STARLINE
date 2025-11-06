import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, TrendingUp, DollarSign, AlertCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export default function GPTAssistantPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadConversation();
  }, [user]);

  const loadConversation = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase.functions.invoke('gpt-trading-assistant', {
        method: 'GET',
        body: { user_id: user.id },
      });

      if (error) throw error;
      setMessages(data.conversation || []);
    } catch (error) {
      console.error('Xatolik:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const { data, error } = await supabase.functions.invoke('gpt-trading-assistant', {
        body: {
          user_id: user.id,
          message: input,
        },
      });

      if (error) throw error;

      const assistantMessage: Message = {
        id: Date.now().toString() + '1',
        role: 'assistant',
        content: data.response,
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Xatolik:', error);
      const errorMessage: Message = {
        id: Date.now().toString() + '1',
        role: 'assistant',
        content: 'Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    { icon: TrendingUp, text: 'BTC narxi qanday o\'zgaradi?' },
    { icon: DollarSign, text: 'Eng yaxshi investitsiya strategiyasi?' },
    { icon: AlertCircle, text: 'Bugungi bozor tahlili' },
  ];

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-indigo-500/20 rounded-xl">
            <Bot className="w-8 h-8 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">GPT Trading Assistant</h1>
            <p className="text-slate-400">AI yordamchisi - savol bering, maslahat oling</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-indigo-400 mx-auto mb-4 opacity-50" />
            <p className="text-slate-400 mb-6">Salom! Men sizga trading bo'yicha yordam beraman.</p>
            <div className="max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt.text)}
                  className="p-4 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl hover:border-indigo-500/50 transition-all text-left"
                >
                  <prompt.icon className="w-6 h-6 text-indigo-400 mb-2" />
                  <p className="text-white text-sm">{prompt.text}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="p-2 bg-indigo-500/20 rounded-lg h-fit">
                  <Bot className="w-6 h-6 text-indigo-400" />
                </div>
              )}
              <div
                className={`max-w-2xl p-4 rounded-xl ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800/50 backdrop-blur border border-slate-700 text-white'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs mt-2 opacity-50">
                  {new Date(message.created_at).toLocaleTimeString('uz')}
                </p>
              </div>
              {message.role === 'user' && (
                <div className="p-2 bg-indigo-500/20 rounded-lg h-fit">
                  <User className="w-6 h-6 text-indigo-400" />
                </div>
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="p-2 bg-indigo-500/20 rounded-lg h-fit">
              <Bot className="w-6 h-6 text-indigo-400" />
            </div>
            <div className="max-w-2xl p-4 rounded-xl bg-slate-800/50 backdrop-blur border border-slate-700">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-slate-700">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Savol yoki buyruq yozing..."
              className="flex-1 px-6 py-4 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              <Send className="w-5 h-5" />
              Yuborish
            </button>
          </div>
          <p className="text-slate-500 text-sm mt-3 text-center">
            AI javoblari faqat ma'lumot uchun. Moliyaviy maslahat emas.
          </p>
        </div>
      </div>
    </div>
  );
}
