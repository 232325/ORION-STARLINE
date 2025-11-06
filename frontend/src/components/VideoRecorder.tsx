import { useState, useRef, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  Camera, 
  CameraOff, 
  Video, 
  VideoOff,
  Settings, 
  Download,
  Trash2,
  FileVideo,
  Maximize,
  Minimize,
  RotateCcw
} from 'lucide-react';
import { useMediaDevices } from '../hooks/useMediaDevices';

interface VideoRecorderProps {
  onRecordingComplete?: (blob: Blob) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  className?: string;
  showPreview?: boolean;
  allowMultiple?: boolean;
}

export default function VideoRecorder({ 
  onRecordingComplete, 
  onRecordingStart,
  onRecordingStop,
  className = "",
  showPreview = true,
  allowMultiple = true
}: VideoRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [hasPermission, setHasPermission] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<string>('');
  const [recordedVideos, setRecordedVideos] = useState<Array<{
    id: string;
    blob: Blob;
    url: string;
    duration: number;
    timestamp: Date;
  }>>([]);
  const [currentStream, setCurrentStream] = useState<MediaStream | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [videoQuality, setVideoQuality] = useState<'low' | 'medium' | 'high'>('medium');
  const [isStreaming, setIsStreaming] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const streamIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const {
    devices,
    currentStream: hookStream,
    error,
    requestPermission,
    getDevices,
    startCamera,
    stopCamera
  } = useMediaDevices();

  useEffect(() => {
    initializeDevice();
    return () => {
      cleanup();
    };
  }, []);

  useEffect(() => {
    if (hookStream && videoRef.current) {
      videoRef.current.srcObject = hookStream;
    }
  }, [hookStream]);

  const initializeDevice = async () => {
    const granted = await requestPermission();
    setHasPermission(granted);
    if (granted) {
      await getDevices();
      await startCamera();
    }
  };

  const cleanup = () => {
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
    }
    if (currentStream) {
      currentStream.getTracks().forEach(track => track.stop());
    }
    stopCamera();
  };

  const getVideoConstraints = () => {
    const qualitySettings = {
      low: { width: 640, height: 480, frameRate: 15 },
      medium: { width: 1280, height: 720, frameRate: 30 },
      high: { width: 1920, height: 1080, frameRate: 30 }
    };

    const settings = qualitySettings[videoQuality];
    
    return {
      width: { ideal: settings.width, min: 320 },
      height: { ideal: settings.height, min: 240 },
      frameRate: { ideal: settings.frameRate, min: 10 },
      facingMode: 'user'
    };
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: selectedCamera 
          ? { deviceId: { exact: selectedCamera }, ...getVideoConstraints() }
          : getVideoConstraints(),
        audio: true
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9,opus',
        videoBitsPerSecond: videoQuality === 'high' ? 5000000 : 
                           videoQuality === 'medium' ? 2500000 : 1000000
      });

      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const videoId = Date.now().toString();

        const newVideo = {
          id: videoId,
          blob,
          url,
          duration,
          timestamp: new Date()
        };

        setRecordedVideos(prev => 
          allowMultiple ? [...prev, newVideo] : [newVideo]
        );

        stream.getTracks().forEach(track => track.stop());
        
        if (durationIntervalRef.current) {
          clearInterval(durationIntervalRef.current);
        }

        onRecordingComplete?.(blob);
      };

      mediaRecorder.start(1000); // Collect data every second
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setDuration(0);
      
      durationIntervalRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);

      onRecordingStart?.();
    } catch (error) {
      console.error('Video recording failed:', error);
      alert('Video yozib olishda xatolik yuz berdi');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    
    setIsRecording(false);
    setIsPaused(false);
    setDuration(0);
    
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
    
    onRecordingStop?.();
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    }
  };

  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const context = canvas.getContext('2d');
      
      if (!context) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);

      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `photo_${Date.now()}.jpg`;
          a.click();
          URL.revokeObjectURL(url);
        }
      }, 'image/jpeg', 0.9);
    }
  };

  const downloadVideo = (video: { url: string; duration: number; timestamp: Date }) => {
    const a = document.createElement('a');
    a.href = video.url;
    a.download = `video_${video.timestamp.getTime()}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const deleteVideo = (id: string) => {
    setRecordedVideos(prev => {
      const video = prev.find(v => v.id === id);
      if (video) {
        URL.revokeObjectURL(video.url);
      }
      return prev.filter(v => v.id !== id);
    });
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getVideoDevices = () => {
    return devices.filter(device => device.kind === 'videoinput');
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (videoRef.current?.requestFullscreen) {
        videoRef.current.requestFullscreen();
        setIsFullscreen(true);
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  if (!hasPermission) {
    return (
      <div className={`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 ${className}`}>
        <div className="text-center">
          <CameraOff className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Ruxsat kerak</h3>
          <p className="text-slate-400 mb-4">Video yozib olish uchun kamera ruxsati kerak</p>
          <button
            onClick={initializeDevice}
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
          <CameraOff className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Xatolik</h3>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileVideo className="w-8 h-8 text-green-400" />
          <h3 className="text-2xl font-bold text-white">Video Yozib Olish</h3>
        </div>
        
        {/* Quality Selector */}
        <select
          value={videoQuality}
          onChange={(e) => setVideoQuality(e.target.value as 'low' | 'medium' | 'high')}
          className="px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="low">Past (640x480)</option>
          <option value="medium">O'rta (1280x720)</option>
          <option value="high">Yuqori (1920x1080)</option>
        </select>
      </div>

      {/* Camera Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Kamera tanlang
        </label>
        <div className="flex gap-4">
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="flex-1 px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Standart kamera</option>
            {getVideoDevices().map(device => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label}
              </option>
            ))}
          </select>
          
          <button
            onClick={initializeDevice}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Video Preview */}
      {showPreview && (
        <div className="relative mb-6 bg-black rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            className="w-full h-64 object-cover"
            autoPlay
            muted
            playsInline
          />
          
          {/* Recording indicator */}
          {isRecording && (
            <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500/90 text-white px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">
                {isPaused ? 'Tugallab qo\'yilgan' : 'REC'}
              </span>
            </div>
          )}

          {/* Duration overlay */}
          {isRecording && (
            <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-lg text-lg font-mono">
              {formatDuration(duration)}
            </div>
          )}

          {/* Fullscreen button */}
          {showPreview && (
            <button
              onClick={toggleFullscreen}
              className="absolute top-4 left-4 p-2 bg-black/50 hover:bg-black/70 text-white rounded-lg transition-colors"
            >
              {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
            </button>
          )}
        </div>
      )}

      {/* Recording Controls */}
      <div className="text-center mb-6">
        <div className="flex justify-center items-center gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="w-16 h-16 bg-red-600 hover:bg-red-500 rounded-full flex items-center justify-center text-white transition-all transform hover:scale-105"
            >
              <Video className="w-8 h-8" />
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

          {/* Photo button */}
          <button
            onClick={takePhoto}
            disabled={isRecording}
            className="w-12 h-12 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 rounded-full flex items-center justify-center text-white transition-all disabled:cursor-not-allowed"
          >
            <Camera className="w-6 h-6" />
          </button>
        </div>

        <p className="text-slate-400 text-sm mt-4">
          {isRecording 
            ? (isPaused ? 'Tugallab qo\'yilgan' : 'Video yozib olinmoqda...') 
            : 'Bosish orqali yozib olishni boshlang'
          }
        </p>
      </div>

      {/* Recorded Videos */}
      {recordedVideos.length > 0 && (
        <div className="border-t border-slate-700 pt-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            Yozib olingan videolar ({recordedVideos.length})
          </h4>
          
          <div className="space-y-3">
            {recordedVideos.map((video) => (
              <div key={video.id} className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-lg">
                <video
                  src={video.url}
                  className="w-24 h-16 object-cover rounded"
                  muted
                />
                
                <div className="flex-1">
                  <p className="text-white font-medium">
                    {formatDuration(video.duration)}
                  </p>
                  <p className="text-slate-400 text-sm">
                    {video.timestamp.toLocaleString('uz')}
                  </p>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => window.open(video.url, '_blank')}
                    className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => downloadVideo(video)}
                    className="p-2 bg-green-600 hover:bg-green-500 text-white rounded transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => deleteVideo(video.id)}
                    className="p-2 bg-red-600 hover:bg-red-500 text-white rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden canvas for photo capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}