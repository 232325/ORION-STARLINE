import { useState, useEffect, useRef } from 'react';
import { 
  Camera, 
  Mic, 
  Monitor, 
  Settings, 
  CheckCircle, 
  AlertCircle, 
  Video, 
  VideoOff,
  MicOff,
  Volume2,
  VolumeX,
  CameraOff,
  RefreshCw
} from 'lucide-react';

interface DeviceInfo {
  deviceId: string;
  kind: 'audioinput' | 'videoinput' | 'audiooutput';
  label: string;
  groupId: string;
}

interface DeviceSettings {
  camera: string;
  microphone: string;
  speaker: string;
}

export default function DeviceSettingsPage() {
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [settings, setSettings] = useState<DeviceSettings>({
    camera: '',
    microphone: '',
    speaker: ''
  });
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [testResults, setTestResults] = useState({
    camera: false,
    microphone: false,
    speaker: false
  });

  const videoRef = useRef<HTMLVideoElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    loadDevices();
    loadSettings();
  }, []);

  const loadDevices = async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      setDevices(deviceList);
    } catch (error) {
      console.error('Qurilmalarni yuklashda xatolik:', error);
    }
  };

  const loadSettings = () => {
    const savedSettings = localStorage.getItem('deviceSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  };

  const saveSettings = () => {
    localStorage.setItem('deviceSettings', JSON.stringify(settings));
  };

  const requestPermissions = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      setStream(stream);
      return true;
    } catch (error) {
      console.error('Ruxsat so\'rashda xatolik:', error);
      return false;
    }
  };

  const testCamera = async () => {
    setIsTesting(true);
    setTestResults(prev => ({ ...prev, camera: false }));

    try {
      const hasPermission = await requestPermissions();
      if (!hasPermission) {
        setIsTesting(false);
        return;
      }

      if (videoRef.current && stream) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setTestResults(prev => ({ ...prev, camera: true }));
      }
    } catch (error) {
      console.error('Kamera testi xatosi:', error);
    }
    setIsTesting(false);
  };

  const testMicrophone = async () => {
    setIsTesting(true);
    setTestResults(prev => ({ ...prev, microphone: false }));

    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      const hasPermission = await requestPermissions();
      if (!hasPermission) {
        setIsTesting(false);
        return;
      }

      if (stream) {
        const source = audioContextRef.current.createMediaStreamSource(stream);
        const analyser = audioContextRef.current.createAnalyser();
        source.connect(analyser);

        // Audio level check
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        const isWorking = average > 10; // Threshold for audio detection

        setTestResults(prev => ({ ...prev, microphone: isWorking }));

        if (isWorking) {
          // Test speech synthesis
          const utterance = new SpeechSynthesisUtterance('Mikrofon testi muvaffaqiyatli');
          utterance.volume = 0.5;
          window.speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Mikrofon testi xatosi:', error);
    }
    setIsTesting(false);
  };

  const testSpeaker = () => {
    setTestResults(prev => ({ ...prev, speaker: false }));

    try {
      const utterance = new SpeechSynthesisUtterance('Speaker testi - ovoz sinovi');
      utterance.volume = 0.8;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      utterance.onend = () => {
        setTestResults(prev => ({ ...prev, speaker: true }));
      };

      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error('Speaker testi xatosi:', error);
    }
  };

  const stopTest = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsTesting(false);
  };

  const getDevicesByKind = (kind: 'audioinput' | 'videoinput' | 'audiooutput') => {
    return devices.filter(device => device.kind === kind);
  };

  const DeviceSelector = ({ 
    kind, 
    label, 
    value, 
    onChange, 
    icon: Icon 
  }: { 
    kind: 'audioinput' | 'videoinput' | 'audiooutput';
    label: string;
    value: string;
    onChange: (value: string) => void;
    icon: any;
  }) => {
    const deviceList = getDevicesByKind(kind);
    
    return (
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Icon className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">{label}</h3>
        </div>
        
        <div className="space-y-3">
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Qurilma tanlang</option>
            {deviceList.map(device => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `${label} ${device.deviceId.slice(0, 8)}`}
              </option>
            ))}
          </select>
          
          <button
            onClick={async () => {
              if (kind === 'videoinput') {
                await testCamera();
              } else if (kind === 'audioinput') {
                await testMicrophone();
              } else if (kind === 'audiooutput') {
                testSpeaker();
              }
            }}
            disabled={isTesting}
            className="w-full py-2 bg-green-600 hover:bg-green-500 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {isTesting ? 'Test qilish...' : 'Test qilish'}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Settings className="w-10 h-10 text-green-400" />
          Qurilma Sozlamalari
        </h1>
        <p className="text-slate-400">Mikrofon, kamera va audio qurilmalarni boshqaring</p>
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Camera Settings */}
          <DeviceSelector
            kind="videoinput"
            label="Kamera"
            value={settings.camera}
            onChange={(value) => setSettings(prev => ({ ...prev, camera: value }))}
            icon={Camera}
          />

          {/* Microphone Settings */}
          <DeviceSelector
            kind="audioinput"
            label="Mikrofon"
            value={settings.microphone}
            onChange={(value) => setSettings(prev => ({ ...prev, microphone: value }))}
            icon={Mic}
          />

          {/* Speaker Settings */}
          <DeviceSelector
            kind="audiooutput"
            label="Speaker"
            value={settings.speaker}
            onChange={(value) => setSettings(prev => ({ ...prev, speaker: value }))}
            icon={Volume2}
          />
        </div>

        {/* Test Results */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-400" />
            Test Natijalari
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-lg">
              {testResults.camera ? (
                <CheckCircle className="w-6 h-6 text-green-400" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-400" />
              )}
              <div>
                <p className="text-white font-medium">Kamera</p>
                <p className={`text-sm ${testResults.camera ? 'text-green-400' : 'text-red-400'}`}>
                  {testResults.camera ? 'Ishlaydi' : 'Ishlamaydi'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-lg">
              {testResults.microphone ? (
                <CheckCircle className="w-6 h-6 text-green-400" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-400" />
              )}
              <div>
                <p className="text-white font-medium">Mikrofon</p>
                <p className={`text-sm ${testResults.microphone ? 'text-green-400' : 'text-red-400'}`}>
                  {testResults.microphone ? 'Ishlaydi' : 'Ishlamaydi'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-lg">
              {testResults.speaker ? (
                <CheckCircle className="w-6 h-6 text-green-400" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-400" />
              )}
              <div>
                <p className="text-white font-medium">Speaker</p>
                <p className={`text-sm ${testResults.speaker ? 'text-green-400' : 'text-red-400'}`}>
                  {testResults.speaker ? 'Ishlaydi' : 'Ishlamaydi'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Video Preview */}
        {(testResults.camera || stream) && (
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 mb-8">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-3">
              <Video className="w-6 h-6 text-green-400" />
              Kamera Oldindan Ko'rish
            </h3>
            
            <div className="relative">
              <video
                ref={videoRef}
                className="w-full max-w-md mx-auto rounded-lg"
                autoPlay
                muted
                playsInline
              />
              
              {isTesting && (
                <div className="absolute top-4 right-4">
                  <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="sr-only">Yozib olinmoqda</span>
                </div>
              )}
            </div>
            
            <div className="mt-4 flex justify-center">
              <button
                onClick={stopTest}
                className="px-6 py-2 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg transition-colors"
              >
                To'xtatish
              </button>
            </div>
          </div>
        )}

        {/* Save Settings */}
        <div className="flex justify-center">
          <button
            onClick={() => {
              saveSettings();
              // You can also save to backend here
            }}
            className="px-8 py-3 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg transition-colors flex items-center gap-2"
          >
            <CheckCircle className="w-5 h-5" />
            Sozlamalarni Saqlash
          </button>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-blue-400" />
            Yordam
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-slate-300">
            <div>
              <h4 className="font-semibold text-white mb-2">Kamera sozlamalari:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Kamera qurilmasini tanlang</li>
                <li>• "Test qilish" tugmasini bosing</li>
                <li>• Videoni oldindan ko'ring</li>
                <li>• Sozlamalarni saqlang</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">Audio sozlamalari:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Mikrofon va speaker tanlang</li>
                <li>• Audio testini bajaring</li>
                <li>• Ovoz sinovini eshiting</li>
                <li>• Sozlamalarni saqlang</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}