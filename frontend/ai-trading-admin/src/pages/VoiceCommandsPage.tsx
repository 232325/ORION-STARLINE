import { useState } from 'react';
import { Mic, MicOff, Volume2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface CommandHistory {
  id: string;
  command_text: string;
  command_type: string;
  status: string;
  result: any;
  created_at: string;
}

export default function VoiceCommandsPage() {
  const { user } = useAuth();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [history, setHistory] = useState<CommandHistory[]>([]);
  const [processing, setProcessing] = useState(false);

  const startListening = () => {
    setIsListening(true);
    // Browser Speech Recognition API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.lang = 'uz-UZ';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        setTranscript(text);
        processCommand(text);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } else {
      alert('Brauzeringiz ovozli buyruqlarni qo\'llab-quvvatlamaydi');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    setIsListening(false);
  };

  const processCommand = async (text: string) => {
    if (!user) return;

    setProcessing(true);
    try {
      const { data, error } = await supabase.functions.invoke('voice-commands', {
        body: {
          user_id: user.id,
          text: text,
        },
      });

      if (error) throw error;

      // Javobni ovoz bilan o'qish
      if (data.response_text) {
        speak(data.response_text);
      }

      // Tarixga qo'shish
      setHistory(prev => [data.command, ...prev]);
      setTranscript('');
    } catch (error) {
      console.error('Xatolik:', error);
      speak('Kechirasiz, buyruqni bajara olmadim');
    } finally {
      setProcessing(false);
    }
  };

  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'uz-UZ';
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const exampleCommands = [
    'BTC sotib ol',
    'ETH sotish',
    'Balansimni ko\'rsat',
    'BTC narxi qancha',
    'BTC 70000 da ogohlantirish o\'rnat',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Mic className="w-10 h-10 text-green-400" />
          Voice Commands
        </h1>
        <p className="text-slate-400">Ovoz bilan trading - qulay va tez</p>
      </div>

      {/* Voice Control */}
      <div className="mb-8 max-w-3xl mx-auto">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-12 text-center">
          {/* Microphone Button */}
          <button
            onClick={isListening ? stopListening : startListening}
            disabled={processing}
            className={`w-32 h-32 rounded-full mx-auto mb-6 flex items-center justify-center transition-all ${
              isListening
                ? 'bg-green-500 shadow-lg shadow-green-500/50 animate-pulse'
                : 'bg-slate-700 hover:bg-slate-600'
            } disabled:opacity-50`}
          >
            {isListening ? (
              <MicOff className="w-16 h-16 text-white" />
            ) : (
              <Mic className="w-16 h-16 text-white" />
            )}
          </button>

          {/* Status */}
          <div className="mb-6">
            {processing ? (
              <p className="text-yellow-400 text-lg font-medium">Buyruq bajarilmoqda...</p>
            ) : isListening ? (
              <p className="text-green-400 text-lg font-medium animate-pulse">Tinglanmoqda...</p>
            ) : (
              <p className="text-slate-400 text-lg">Bosing va buyruq bering</p>
            )}
          </div>

          {/* Transcript */}
          {transcript && (
            <div className="bg-slate-900/50 rounded-lg p-4 mb-6">
              <p className="text-white text-xl">&ldquo;{transcript}&rdquo;</p>
            </div>
          )}

          {/* Example Commands */}
          <div className="text-left">
            <p className="text-slate-400 text-sm mb-3">Misol buyruqlar:</p>
            <div className="space-y-2">
              {exampleCommands.map((cmd, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setTranscript(cmd);
                    processCommand(cmd);
                  }}
                  className="w-full p-3 bg-slate-900/50 hover:bg-slate-900/70 rounded-lg text-left text-slate-300 text-sm transition-all flex items-center gap-2"
                >
                  <Volume2 className="w-4 h-4 text-green-400" />
                  {cmd}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Command History */}
      <div className="max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-4">Buyruqlar tarixi</h2>
        
        {history.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
            <Clock className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Hozircha buyruqlar yo'q</p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((cmd) => (
              <div
                key={cmd.id}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-green-500/50 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {cmd.status === 'processed' ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-400" />
                      )}
                      <span className="text-white font-semibold text-lg">{cmd.command_text}</span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm mb-3">
                      <span className={`px-3 py-1 rounded-lg ${
                        cmd.command_type === 'BUY'
                          ? 'bg-green-500/20 text-green-400'
                          : cmd.command_type === 'SELL'
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {cmd.command_type}
                      </span>
                      <span className="text-slate-400">
                        {new Date(cmd.created_at).toLocaleString('uz')}
                      </span>
                    </div>

                    {cmd.result && (
                      <div className="bg-slate-900/50 rounded-lg p-4 text-sm">
                        <p className="text-slate-300">
                          <strong>Natija:</strong> {JSON.stringify(cmd.result, null, 2)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="mt-8 max-w-3xl mx-auto bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
          <Volume2 className="w-6 h-6 text-blue-400" />
          Qanday foydalanish
        </h3>
        <ul className="space-y-2 text-slate-300">
          <li>• Mikrofon tugmasini bosing</li>
          <li>• Buyruqni aniq va ravon talaffuz qiling</li>
          <li>• Tizim buyruqni tanib, bajaradi</li>
          <li>• Natija ovoz va matn ko'rinishida qaytadi</li>
          <li>• Qo'llab-quvvatlanadigan buyruqlar: sotib olish, sotish, balans, narx, ogohlantirish</li>
        </ul>
      </div>
    </div>
  );
}
