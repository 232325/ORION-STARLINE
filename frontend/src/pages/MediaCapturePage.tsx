import { useState } from 'react';
import { 
  Camera, 
  Mic, 
  Settings, 
  Video, 
  Upload, 
  Download,
  FileVideo,
  FileAudio,
  Play,
  Pause
} from 'lucide-react';
import AudioRecorder from '../components/AudioRecorder';
import VideoRecorder from '../components/VideoRecorder';
import { useMediaDevices } from '../hooks/useMediaDevices';
import { DeviceManager } from '../utils/mediaDeviceManager';

export default function MediaCapturePage() {
  const [activeTab, setActiveTab] = useState<'video' | 'audio' | 'both'>('both');
  const [recordings, setRecordings] = useState<Array<{
    id: string;
    type: 'video' | 'audio';
    blob: Blob;
    url: string;
    duration: number;
    timestamp: Date;
  }>>([]);

  const {
    devices,
    isRecording,
    isStreaming,
    error,
    getDevices,
    requestPermission
  } = useMediaDevices();

  const handleRecordingComplete = (blob: Blob, type: 'video' | 'audio') => {
    const url = URL.createObjectURL(blob);
    const id = Date.now().toString();
    const duration = type === 'video' ? 0 : 0; // You can track duration
    
    setRecordings(prev => [...prev, {
      id,
      type,
      blob,
      url,
      duration,
      timestamp: new Date()
    }]);
  };

  const deleteRecording = (id: string) => {
    setRecordings(prev => {
      const recording = prev.find(r => r.id === id);
      if (recording) {
        URL.revokeObjectURL(recording.url);
      }
      return prev.filter(r => r.id !== id);
    });
  };

  const downloadRecording = (recording: { url: string; type: string; timestamp: Date }) => {
    const a = document.createElement('a');
    a.href = recording.url;
    a.download = `${recording.type}_${recording.timestamp.getTime()}.${recording.type === 'video' ? 'webm' : 'webm'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const getDeviceStats = () => {
    const videoDevices = devices.filter(d => d.kind === 'videoinput');
    const audioDevices = devices.filter(d => d.kind === 'audioinput');
    const outputDevices = devices.filter(d => d.kind === 'audiooutput');

    return {
      cameras: videoDevices.length,
      microphones: audioDevices.length,
      speakers: outputDevices.length
    };
  };

  const stats = getDeviceStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Camera className="w-10 h-10 text-green-400" />
          Media Yozib Olish Markazi
        </h1>
        <p className="text-slate-400">Audio va video yozib olish uchun professional vosita</p>
      </div>

      {/* Device Status */}
      <div className="mb-8 max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-4 text-center">
            <Camera className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <p className="text-white font-semibold">Kameralar</p>
            <p className="text-2xl font-bold text-blue-400">{stats.cameras}</p>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-4 text-center">
            <Mic className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <p className="text-white font-semibold">Mikrofonlar</p>
            <p className="text-2xl font-bold text-green-400">{stats.microphones}</p>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-4 text-center">
            <Settings className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <p className="text-white font-semibold">Speakers</p>
            <p className="text-2xl font-bold text-yellow-400">{stats.speakers}</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="flex justify-center">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-2 flex">
            <button
              onClick={() => setActiveTab('both')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'both'
                  ? 'bg-green-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <FileVideo className="w-5 h-5" />
              Ikkalasi
            </button>
            <button
              onClick={() => setActiveTab('video')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'video'
                  ? 'bg-green-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Video className="w-5 h-5" />
              Faqat Video
            </button>
            <button
              onClick={() => setActiveTab('audio')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'audio'
                  ? 'bg-green-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <FileAudio className="w-5 h-5" />
              Faqat Audio
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-6xl mx-auto">
        {activeTab === 'video' && (
          <VideoRecorder
            onRecordingComplete={(blob) => handleRecordingComplete(blob, 'video')}
            className="mb-8"
            showPreview={true}
            allowMultiple={true}
          />
        )}

        {activeTab === 'audio' && (
          <AudioRecorder
            onRecordingComplete={(blob) => handleRecordingComplete(blob, 'audio')}
            className="mb-8"
          />
        )}

        {activeTab === 'both' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
            <VideoRecorder
              onRecordingComplete={(blob) => handleRecordingComplete(blob, 'video')}
              showPreview={true}
              allowMultiple={true}
            />
            <AudioRecorder
              onRecordingComplete={(blob) => handleRecordingComplete(blob, 'audio')}
            />
          </div>
        )}

        {/* Recordings List */}
        {recordings.length > 0 && (
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Upload className="w-8 h-8 text-green-400" />
              Yozib Olingan Fayllar ({recordings.length})
            </h3>
            
            <div className="space-y-4">
              {recordings.map((recording) => (
                <div key={recording.id} className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-all">
                  <div className="flex-shrink-0">
                    {recording.type === 'video' ? (
                      <Video className="w-8 h-8 text-blue-400" />
                    ) : (
                      <FileAudio className="w-8 h-8 text-green-400" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-semibold">
                        {recording.type === 'video' ? 'Video' : 'Audio'} yozib olish
                      </span>
                      <span className="text-xs bg-slate-600 text-slate-300 px-2 py-1 rounded">
                        {recording.type.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm">
                      {recording.timestamp.toLocaleString('uz')}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => window.open(recording.url, '_blank')}
                      className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                      title="Ochish"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => downloadRecording(recording)}
                      className="p-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
                      title="Yuklab olish"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => deleteRecording(recording.id)}
                      className="p-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
                      title="O'chirish"
                    >
                      <FileVideo className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Bulk Actions */}
            <div className="mt-6 flex justify-center gap-4">
              <button
                onClick={() => {
                  if (confirm('Barcha yozib olingan fayllarni o\'chirishni xohlaysizmi?')) {
                    recordings.forEach(r => URL.revokeObjectURL(r.url));
                    setRecordings([]);
                  }
                }}
                className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-lg transition-colors"
              >
                Barchasini O'chirish
              </button>
              
              <button
                onClick={() => {
                  recordings.forEach(r => downloadRecording(r));
                }}
                className="px-6 py-3 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-lg transition-colors"
              >
                Barchasini Yuklab Olish
              </button>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-8 bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Settings className="w-6 h-6 text-blue-400" />
            Yordam va Maslahatlar
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-slate-300">
            <div>
              <h4 className="font-semibold text-white mb-2">Audio yozib olish:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Mikrofon sifatini sozlang</li>
                <li>• Ovoz darajasini kuzating</li>
                <li>• To'xtatish tugmasini bosing</li>
                <li>• Faylni o'ynash yoki yuklab olish</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">Video yozib olish:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Kamera sifatini tanlang</li>
                <li>• To'liq ekran rejimidan foydalaning</li>
                <li>• Tanafus tugmasi bilan photo oling</li>
                <li>• Bir nechta video yozib olish mumkin</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}