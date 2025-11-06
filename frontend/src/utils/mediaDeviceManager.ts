// Device management utilities
export interface DeviceInfo {
  deviceId: string;
  kind: 'audioinput' | 'videoinput' | 'audiooutput';
  label: string;
  groupId: string;
  state: 'connected' | 'disconnected' | 'in-use';
}

export interface MediaConstraints {
  video: {
    width?: { ideal?: number; min?: number; max?: number };
    height?: { ideal?: number; min?: number; max?: number };
    frameRate?: { ideal?: number; min?: number; max?: number };
    facingMode?: 'user' | 'environment' | 'left' | 'right';
    deviceId?: string;
  };
  audio?: {
    deviceId?: string;
    echoCancellation?: boolean;
    noiseSuppression?: boolean;
    autoGainControl?: boolean;
  };
}

export interface RecordingOptions {
  mimeType?: string;
  videoBitsPerSecond?: number;
  audioBitsPerSecond?: number;
}

// Device Manager Class
export class DeviceManager {
  private static instance: DeviceManager;
  private devices: DeviceInfo[] = [];
  private permissionsGranted: boolean = false;

  private constructor() {
    this.setupDeviceChangeListener();
  }

  public static getInstance(): DeviceManager {
    if (!DeviceManager.instance) {
      DeviceManager.instance = new DeviceManager();
    }
    return DeviceManager.instance;
  }

  // Setup device change listener
  private setupDeviceChangeListener() {
    if ('ondevicechange' in navigator.mediaDevices) {
      navigator.mediaDevices.ondevicechange = () => {
        this.refreshDevices();
        this.notifyDeviceChange();
      };
    }
  }

  // Notify device changes
  private notifyDeviceChange() {
    window.dispatchEvent(new CustomEvent('devicechange', {
      detail: { timestamp: new Date() }
    }));
  }

  // Get all devices
  public async getDevices(): Promise<DeviceInfo[]> {
    try {
      // Request permission first to get device labels
      await this.requestPermissions();
      
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      this.devices = deviceList.map(device => ({
        deviceId: device.deviceId,
        kind: device.kind as 'audioinput' | 'videoinput' | 'audiooutput',
        label: device.label || this.getDefaultLabel(device),
        groupId: device.groupId,
        state: 'connected' // Default state
      }));

      return this.devices;
    } catch (error) {
      throw new Error(`Qurilmalarni yuklashda xatolik: ${error}`);
    }
  }

  // Get devices by type
  public getDevicesByType(type: 'audioinput' | 'videoinput' | 'audiooutput'): DeviceInfo[] {
    return this.devices.filter(device => device.kind === type);
  }

  // Get default label for unnamed devices
  private getDefaultLabel(device: MediaDeviceInfo): string {
    const typeMap = {
      'audioinput': 'Mikrofon',
      'videoinput': 'Kamera',
      'audiooutput': 'Speaker'
    };
    
    const baseName = typeMap[device.kind] || 'Noma\'lum qurilma';
    const deviceIndex = this.devices.filter(d => d.kind === device.kind).length + 1;
    
    return `${baseName} ${deviceIndex}`;
  }

  // Request permissions
  public async requestPermissions(constraints?: MediaStreamConstraints): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints || {
        video: true,
        audio: true
      });

      // Stop the stream immediately
      stream.getTracks().forEach(track => track.stop());
      
      this.permissionsGranted = true;
      return true;
    } catch (error) {
      console.error('Permission request failed:', error);
      return false;
    }
  }

  // Check permission status
  public async checkPermission(kind: PermissionName): Promise<PermissionState> {
    if ('permissions' in navigator) {
      const permission = await navigator.permissions.query({ name: kind });
      return permission.state;
    }
    return 'prompt';
  }

  // Refresh device list
  public async refreshDevices(): Promise<DeviceInfo[]> {
    this.devices = [];
    return this.getDevices();
  }

  // Get current device
  public getCurrentDevice(deviceId: string): DeviceInfo | undefined {
    return this.devices.find(device => device.deviceId === deviceId);
  }

  // Check if device is available
  public isDeviceAvailable(deviceId: string): boolean {
    return this.devices.some(device => device.deviceId === deviceId);
  }
}

// Media Stream Manager
export class MediaStreamManager {
  private static instance: MediaStreamManager;
  private streams: Map<string, MediaStream> = new Map();

  private constructor() {}

  public static getInstance(): MediaStreamManager {
    if (!MediaStreamManager.instance) {
      MediaStreamManager.instance = new MediaStreamManager();
    }
    return MediaStreamManager.instance;
  }

  // Create video stream
  public async createVideoStream(constraints?: MediaConstraints['video']): Promise<MediaStream> {
    const videoConstraints: MediaStreamConstraints = {
      video: {
        width: { ideal: 1280, min: 640 },
        height: { ideal: 720, min: 480 },
        frameRate: { ideal: 30, min: 15 },
        ...constraints
      }
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(videoConstraints);
      return stream;
    } catch (error) {
      throw new Error(`Video stream yaratishda xatolik: ${error}`);
    }
  }

  // Create audio stream
  public async createAudioStream(constraints?: MediaConstraints['audio']): Promise<MediaStream> {
    const audioConstraints: MediaStreamConstraints = {
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        ...constraints
      }
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(audioConstraints);
      return stream;
    } catch (error) {
      throw new Error(`Audio stream yaratishda xatolik: ${error}`);
    }
  }

  // Create combined stream
  public async createCombinedStream(
    videoConstraints?: MediaConstraints['video'],
    audioConstraints?: MediaConstraints['audio']
  ): Promise<MediaStream> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints || true,
        audio: audioConstraints || true
      });
      return stream;
    } catch (error) {
      throw new Error(`Combined stream yaratishda xatolik: ${error}`);
    }
  }

  // Store stream with ID
  public storeStream(id: string, stream: MediaStream): void {
    this.streams.set(id, stream);
  }

  // Get stored stream
  public getStream(id: string): MediaStream | undefined {
    return this.streams.get(id);
  }

  // Remove stream
  public removeStream(id: string): void {
    const stream = this.streams.get(id);
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      this.streams.delete(id);
    }
  }

  // Stop all streams
  public stopAllStreams(): void {
    this.streams.forEach(stream => {
      stream.getTracks().forEach(track => track.stop());
    });
    this.streams.clear();
  }
}

// Media Recorder Manager
export class MediaRecorderManager {
  private recorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];

  // Start recording
  public startRecording(
    stream: MediaStream,
    options?: RecordingOptions
  ): Promise<MediaRecorder> {
    return new Promise((resolve, reject) => {
      try {
        const mimeType = options?.mimeType || this.getSupportedMimeType();
        
        this.recorder = new MediaRecorder(stream, {
          mimeType,
          videoBitsPerSecond: options?.videoBitsPerSecond || 2500000,
          audioBitsPerSecond: options?.audioBitsPerSecond || 128000
        });

        this.chunks = [];

        this.recorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.chunks.push(event.data);
          }
        };

        this.recorder.onstop = () => {
          const blob = new Blob(this.chunks, { type: mimeType });
          const url = URL.createObjectURL(blob);
          
          // Trigger download
          const a = document.createElement('a');
          a.href = url;
          a.download = `recording_${Date.now()}.${this.getFileExtension(mimeType)}`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          URL.revokeObjectURL(url);
        };

        this.recorder.onerror = (event) => {
          reject(new Error(`Recording error: ${event}`));
        };

        this.recorder.start(1000); // Collect data every second
        resolve(this.recorder);
      } catch (error) {
        reject(error);
      }
    });
  }

  // Stop recording
  public stopRecording(): void {
    if (this.recorder && this.recorder.state === 'recording') {
      this.recorder.stop();
    }
  }

  // Pause recording
  public pauseRecording(): void {
    if (this.recorder && this.recorder.state === 'recording') {
      this.recorder.pause();
    }
  }

  // Resume recording
  public resumeRecording(): void {
    if (this.recorder && this.recorder.state === 'paused') {
      this.recorder.resume();
    }
  }

  // Get recording state
  public getRecordingState(): string {
    return this.recorder?.state || 'inactive';
  }

  // Get supported MIME type
  private getSupportedMimeType(): string {
    const types = [
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm',
      'video/mp4'
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return 'video/webm'; // Fallback
  }

  // Get file extension from MIME type
  private getFileExtension(mimeType: string): string {
    const extMap: { [key: string]: string } = {
      'video/webm': 'webm',
      'video/mp4': 'mp4',
      'video/ogg': 'ogv',
      'audio/webm': 'webm',
      'audio/mp4': 'mp4'
    };

    return extMap[mimeType] || 'webm';
  }
}

// Audio/Video Processing Utilities
export class MediaProcessor {
  // Create canvas from video
  public static createCanvasFromVideo(video: HTMLVideoElement): HTMLCanvasElement {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0);
    }
    
    return canvas;
  }

  // Convert canvas to blob
  public static canvasToBlob(canvas: HTMLCanvasElement, quality: number = 0.8): Promise<Blob> {
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob!);
      }, 'image/jpeg', quality);
    });
  }

  // Resize video stream
  public static resizeStream(stream: MediaStream, width: number, height: number): Promise<MediaStream> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        reject(new Error('Canvas context yaratib bo\'lmadi'));
        return;
      }

      video.srcObject = stream;
      video.play();

      video.onloadedmetadata = () => {
        canvas.width = width;
        canvas.height = height;

        const destStream = canvas.captureStream(30);

        const draw = () => {
          ctx.drawImage(video, 0, 0, width, height);
          requestAnimationFrame(draw);
        };

        draw();
        resolve(destStream);
      };

      video.onerror = () => reject(new Error('Video yuklanmadi'));
    });
  }

  // Get video thumbnail
  public static getVideoThumbnail(video: HTMLVideoElement): Promise<string> {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        resolve('');
        return;
      }

      canvas.width = 320;
      canvas.height = 240;
      
      ctx.drawImage(video, 0, 0, 320, 240);
      resolve(canvas.toDataURL('image/jpeg', 0.8));
    });
  }
}

// Device compatibility checker
export class DeviceCompatibility {
  // Check if browser supports media devices
  public static isSupported(): boolean {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  // Check specific feature support
  public static checkFeature(feature: string): boolean {
    const features: { [key: string]: boolean } = {
      'videoRecording': !!(window.MediaRecorder && MediaRecorder.isTypeSupported('video/webm')),
      'audioRecording': !!(window.MediaRecorder && MediaRecorder.isTypeSupported('audio/webm')),
      'deviceEnumerate': !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices),
      'deviceChange': !!(navigator.mediaDevices && 'ondevicechange' in navigator.mediaDevices),
      'permissionAPI': 'permissions' in navigator,
      'webRTC': !!(window.RTCPeerConnection || (window as any).webkitRTCPeerConnection)
    };

    return features[feature] || false;
  }

  // Get browser capabilities
  public static getCapabilities(): { [key: string]: boolean } {
    const capabilities: { [key: string]: boolean } = {};
    
    Object.keys({
      'videoRecording': 'videoRecording',
      'audioRecording': 'audioRecording',
      'deviceEnumerate': 'deviceEnumerate',
      'deviceChange': 'deviceChange',
      'permissionAPI': 'permissionAPI',
      'webRTC': 'webRTC'
    }).forEach(key => {
      capabilities[key] = this.checkFeature(key);
    });

    return capabilities;
  }
}

// Event handlers
export class MediaEventManager {
  private handlers: Map<string, Function[]> = new Map();

  public on(event: string, handler: Function): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
    }
    this.handlers.get(event)!.push(handler);
  }

  public off(event: string, handler: Function): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  public emit(event: string, data?: any): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  public clear(): void {
    this.handlers.clear();
  }
}