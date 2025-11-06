import { useState, useRef, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Settings, 
  Download,
  Trash2,
  FileAudio
} from 'lucide-react';
import { useMediaDevices } from '../hooks/useMediaDevices';

interface AudioRecorderProps {
  onRecordingComplete?: (blob: Blob) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  className?: string;
}

export default function AudioRecorder({ 
  onRecordingComplete, 
  onRecordingStart,
  onRecordingStop,
  className = "" 
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [duration, setDuration] = useState(0);
  const [hasPermission, setHasPermission] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordedUrl, setRecordedUrl] = useState<string>('');

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const levelIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const {
    devices,
    error,
    requestPermission,
    getDevices
  } = useMediaDevices();

  useEffect(() => {
    // Check permission on mount
    checkPermission();
    getDevices();

    return () => {
      // Cleanup
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (levelIntervalRef.current) {
        clearInterval(levelIntervalRef.current);
      }
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (recordedUrl) {
        URL.revokeObjectURL(recordedUrl);
      }
    };
  }, []);

  const checkPermission = async () => {
    const granted = await requestPermission();
    setHasPermission(granted);
  };

  const startAudioLevelMonitoring = (stream: MediaStream) => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext();
    }

    const source = audioContextRef.current.createMediaStreamSource(stream);
    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 256;
    source.connect(analyserRef.current);

    const bufferLength = analyserRef.current.frequencyBinCount;
    dataArrayRef.current = new Uint8Array(bufferLength);

    // Monitor audio level
    levelIntervalRef.current = setInterval(() => {
      if (analyserRef.current && dataArrayRef.current) {
        analyserRef.current.getByteFrequencyData(dataArrayRef.current);
        const average = dataArrayRef.current.reduce((a, b) => a + b) / bufferLength;
        setAudioLevel(average / 255);
      }
    }, 100);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: selectedDevice ? { deviceId: { exact: selectedDevice } } : true
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setRecordedBlob(blob);
        
        if (recordedUrl) {
          URL.revokeObjectURL(recordedUrl);
        }
        const url = URL.createObjectURL(blob);
        setRecordedUrl(url);

        // Clean up
        stream.getTracks().forEach(track => track.stop());
        
        if (levelIntervalRef.current) {
          clearInterval(levelIntervalRef.current);
        }
        
        if (onRecordingComplete) {
          onRecordingComplete(blob);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setDuration(0);
      
      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);

      // Start audio level monitoring
      startAudioLevelMonitoring(stream);
      
      onRecordingStart?.();
    } catch (error) {
      console.error('Recording failed:', error);
      alert('Yozib olishda xatolik yuz berdi');
    }
  };

  const stopRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
      })
      .catch(() => {}); // Ignore errors when trying to find recorder

    setIsRecording(false);
    setIsPaused(false);
    setDuration(0);
    
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
    
    onRecordingStop?.();
  };

  const pauseRecording = () => {
    setIsPaused(true);
    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
    }
  };

  const resumeRecording = () => {
    setIsPaused(false);
    if (recordedUrl) {
      // Re-establish audio monitoring
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          startAudioLevelMonitoring(stream);
          stream.getTracks().forEach(track => track.stop());
        })
        .catch(() => {});
    }
  };

  const playRecording = () => {
    if (audioElementRef.current && recordedUrl) {
      if (isPlaying) {
        audioElementRef.current.pause();
        setIsPlaying(false);
      } else {
        audioElementRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const downloadRecording = () => {
    if (recordedBlob && recordedUrl) {
      const a = document.createElement('a');
      a.href = recordedUrl;
      a.download = `audio_recording_${Date.now()}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const deleteRecording = () => {
    setRecordedBlob(null);
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl);
      setRecordedUrl('');
    }
    setIsPlaying(false);
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getAudioDevices = () => {
    return devices.filter(device => device.kind === 'audioinput');
  };

  if (!hasPermission) {
    return (
      <div className={`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 ${className}`}>
        <div className="text-center">
          <MicOff className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Ruxsat kerak</h3>
          <p className="text-slate-400 mb-4">Audio yozib olish uchun mikrofon ruxsati kerak</p>
          <button
            onClick={checkPermission}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-colors"
          >
            Ruxsat so'rash
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-500/10 border border-red-500/30 rounded-xl p-6 ${className}`}>
        <div className="text-center">
          <MicOff className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Xatolik</h3>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <FileAudio className="w-8 h-8 text-green-400" />
        <h3 className="text-2xl font-bold text-white">Audio Yozib Olish</h3>
      </div>

      {/* Device Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Mikrofon tanlang
        </label>
        <select
          value={selectedDevice}
          onChange={(e) => setSelectedDevice(e.target.value)}
          className="w-full px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="">Standart mikrofon</option>
          {getAudioDevices().map(device => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label}
            </option>
          ))}
        </select>
      </div>

      {/* Recording Controls */}
      <div className="text-center mb-6">
        <div className="mb-4">
          {/* Audio Level Indicator */}
          <div className="w-full bg-slate-700 rounded-full h-3 mb-4">
            <div
              className="bg-gradient-to-r from-green-500 to-red-500 h-3 rounded-full transition-all duration-100"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
          
          {/* Duration Display */}
          <div className="text-2xl font-mono text-white mb-4">
            {formatDuration(duration)}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center items-center gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="w-16 h-16 bg-red-600 hover:bg-red-500 rounded-full flex items-center justify-center text-white transition-all transform hover:scale-105"
            >
              <Mic className="w-8 h-8" />
            </button>
          ) : (
            <>
              {!isPaused ? (
                <button
                  onClick={pauseRecording}
                  className="w-12 h-12 bg-yellow-600 hover:bg-yellow-500 rounded-full flex items-center justify-center text-white transition-all"
                >
                  <Pause className="w-6 h-6" />
                </button>
              ) : (
                <button
                  onClick={resumeRecording}
                  className="w-12 h-12 bg-green-600 hover:bg-green-500 rounded-full flex items-center justify-center text-white transition-all"
                >
                  <Play className="w-6 h-6" />
                </button>
              )}
              
              <button
                onClick={stopRecording}
                className="w-12 h-12 bg-red-600 hover:bg-red-500 rounded-full flex items-center justify-center text-white transition-all"
              >
                <Square className="w-6 h-6" />
              </button>
            </>
          )}
        </div>

        <p className="text-slate-400 text-sm mt-4">
          {isRecording 
            ? (isPaused ? 'Tugallab qo\'yilgan' : 'Yozib olinmoqda...') 
            : 'Bosish orqali yozib olishni boshlang'
          }
        </p>
      </div>

      {/* Playback Controls */}
      {recordedBlob && (
        <div className="border-t border-slate-700 pt-6">
          <h4 className="text-lg font-semibold text-white mb-4">Yozib olingan audio</h4>
          
          <div className="flex items-center gap-4">
            <button
              onClick={playRecording}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isPlaying ? 'To\'xtatish' : 'O\'ynash'}
            </button>
            
            <button
              onClick={downloadRecording}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Yuklab olish
            </button>
            
            <button
              onClick={deleteRecording}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              O'chirish
            </button>
          </div>
        </div>
      )}

      {/* Hidden audio element for playback */}
      {recordedUrl && (
        <audio
          ref={audioElementRef}
          src={recordedUrl}
          onEnded={() => setIsPlaying(false)}
          className="hidden"
        />
      )}
    </div>
  );
}