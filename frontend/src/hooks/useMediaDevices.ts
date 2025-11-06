import { useState, useEffect, useCallback, useRef } from 'react';

interface MediaDevice {
  deviceId: string;
  kind: 'audioinput' | 'videoinput' | 'audiooutput';
  label: string;
  groupId: string;
}

interface MediaStreamState {
  stream: MediaStream | null;
  isLoading: boolean;
  error: string | null;
}

interface UseMediaDevicesReturn {
  devices: MediaDevice[];
  currentStream: MediaStream | null;
  isRecording: boolean;
  isStreaming: boolean;
  error: string | null;
  requestPermission: () => Promise<boolean>;
  getDevices: () => Promise<void>;
  startRecording: (options?: MediaRecorderOptions) => Promise<MediaRecorder | null>;
  stopRecording: () => void;
  startCamera: (deviceId?: string) => Promise<boolean>;
  stopCamera: () => void;
  switchCamera: (deviceId: string) => Promise<boolean>;
  takePhoto: () => string | null;
  getAudioLevel: () => number;
}

export function useMediaDevices(): UseMediaDevicesReturn {
  const [devices, setDevices] = useState<MediaDevice[]>([]);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // Get all media devices
  const getDevices = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      const mediaDevices = deviceList.map(device => ({
        deviceId: device.deviceId,
        kind: device.kind as 'audioinput' | 'videoinput' | 'audiooutput',
        label: device.label || `${device.kind} ${device.deviceId.slice(0, 8)}`,
        groupId: device.groupId
      }));
      
      setDevices(mediaDevices);
    } catch (err) {
      setError(`Qurilmalarni yuklashda xatolik: ${err}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Request media permissions
  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      // Stop the stream immediately as we just wanted permissions
      stream.getTracks().forEach(track => track.stop());
      
      await getDevices();
      return true;
    } catch (err) {
      setError(`Ruxsat so'rashda xatolik: ${err}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [getDevices]);

  // Start camera
  const startCamera = useCallback(async (deviceId?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const constraints: MediaStreamConstraints = {
        video: deviceId ? { deviceId: { exact: deviceId } } : true,
        audio: false
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Stop previous stream
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
      
      setMediaStream(stream);
      setIsStreaming(true);
      return true;
    } catch (err) {
      setError(`Kamerani ishga tushirishda xatolik: ${err}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [mediaStream]);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      setMediaStream(null);
      setIsStreaming(false);
    }
  }, [mediaStream]);

  // Switch camera
  const switchCamera = useCallback(async (deviceId: string): Promise<boolean> => {
    const success = await startCamera(deviceId);
    return success;
  }, [startCamera]);

  // Take photo
  const takePhoto = useCallback((): string | null => {
    if (!videoRef.current || !mediaStream) return null;
    
    const canvas = document.createElement('canvas');
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const context = canvas.getContext('2d');
    if (!context) return null;
    
    context.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg');
  }, [mediaStream]);

  // Start recording
  const startRecording = useCallback(async (options?: MediaRecorderOptions): Promise<MediaRecorder | null> => {
    if (!mediaStream) {
      setError('Kamerani avval ishga tushiring');
      return null;
    }

    try {
      setError(null);
      const recorderOptions: MediaRecorderOptions = {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 2500000,
        ...options
      };

      const mediaRecorder = new MediaRecorder(mediaStream, recorderOptions);
      
      const chunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        
        // Auto-download or handle the recording
        const a = document.createElement('a');
        a.href = url;
        a.download = `recording_${Date.now()}.webm`;
        a.click();
        
        URL.revokeObjectURL(url);
        setIsRecording(false);
      };
      
      mediaRecorder.start(1000); // Record in 1-second chunks
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      
      return mediaRecorder;
    } catch (err) {
      setError(`Yozib olishda xatolik: ${err}`);
      return null;
    }
  }, [mediaStream]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
  }, [isRecording]);

  // Get audio level
  const getAudioLevel = useCallback((): number => {
    if (!analyserRef.current) return 0;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    const sum = dataArray.reduce((a, b) => a + b, 0);
    return sum / dataArray.length / 255; // Normalize to 0-1
  }, []);

  // Setup audio analysis
  useEffect(() => {
    if (mediaStream && !audioContextRef.current) {
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(mediaStream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
    }
  }, [mediaStream]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [mediaStream]);

  return {
    devices,
    currentStream: mediaStream,
    isRecording,
    isStreaming,
    error,
    requestPermission,
    getDevices,
    startRecording,
    stopRecording,
    startCamera,
    stopCamera,
    switchCamera,
    takePhoto,
    getAudioLevel
  };
}

// Hook for managing video element
export function useVideoStream(stream: MediaStream | null) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return { videoRef };
}

// Hook for managing audio recording
export function useAudioRecording() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const startRecording = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      const chunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        setIsRecording(false);
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      return true;
    } catch (err) {
      console.error('Audio recording error:', err);
      return false;
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      // @ts-ignore - stream property access
      const stream = mediaRecorderRef.current.stream;
      if (stream) {
        stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
      }
    }
  }, [isRecording]);

  const playAudio = useCallback(() => {
    if (audioBlob) {
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audio.play();
      URL.revokeObjectURL(url);
    }
  }, [audioBlob]);

  return {
    isRecording,
    audioBlob,
    startRecording,
    stopRecording,
    playAudio
  };
}