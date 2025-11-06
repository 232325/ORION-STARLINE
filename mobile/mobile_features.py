"""
React Native Mobile Features - Orion Starline
Mobile ilovaning barcha xususiyatlari va funksionalliklari

Author: Orion Starline AI Trading System
Date: 2025-11-05
"""

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Alert,
  AsyncStorage,
  Platform,
  PushNotificationIOS,
  AppState,
  Linking,
  BackHandler,
  NetInfo,
  Vibration,
  CameraRoll,
  Share,
  Location,
  DeviceEventEmitter,
} from 'react-native';
import { Notifications } from 'expo-notifications';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import * as Location from 'expo-location';
import { Accelerometer } from 'expo-sensors';
import { BarCodeScanner } from 'expo-barcode-scanner';
import * as Print from 'expo-print';
import * as IntentLauncher from 'expo-intent-launcher';
import * as WebBrowser from 'expo-web-browser';
import Icon from 'react-native-vector-icons/Ionicons';
import { WebView } from 'react-native-webview';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import Camera from 'react-native-camera';

const { width, height } = Dimensions.get('window');

// Konfiguratsiya
const CONFIG = {
  API_URL: 'https://api.orion-starline.com',
  OFFLINE_DATA_KEY: 'offline_trading_data',
  USER_SETTINGS_KEY: 'user_preferences',
  BIOMETRIC_TIMEOUT: 30000, // 30 sekund
  LOCATION_TIMEOUT: 10000,
  SCREENSHOT_DELAY: 5000,
  MAX_OFFLINE_RECORDS: 1000,
};

// Authentication Service
export class AuthenticationService {
  constructor() {
    this.biometricSupported = false;
    this.init();
  }

  async init() {
    try {
      this.biometricSupported = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      this.biometricSupported = this.biometricSupported && isEnrolled;
    } catch (error) {
      console.error('Biometric init xatosi:', error);
    }
  }

  async authenticateWithBiometric(promptMessage) {
    try {
      if (!this.biometricSupported) {
        throw new Error('Biometric autentifikatsiya qo\'llab-quvvatlanmaydi');
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: promptMessage || 'Biometrik autentifikatsiya',
        fallbackLabel: 'Alternativ usul',
        disableDeviceFallback: false,
      });

      return result.success;
    } catch (error) {
      console.error('Biometric auth xatosi:', error);
      return false;
    }
  }

  async storeCredentialsSecurely(username, password) {
    try {
      await SecureStore.setItemAsync('user_credentials', JSON.stringify({
        username,
        password,
        timestamp: Date.now(),
      }));
      return true;
    } catch (error) {
      console.error('Credentials saqlash xatosi:', error);
      return false;
    }
  }

  async getStoredCredentials() {
    try {
      const credentials = await SecureStore.getItemAsync('user_credentials');
      return credentials ? JSON.parse(credentials) : null;
    } catch (error) {
      console.error('Credentials olish xatosi:', error);
      return null;
    }
  }

  async clearStoredCredentials() {
    try {
      await SecureStore.deleteItemAsync('user_credentials');
      return true;
    } catch (error) {
      console.error('Credentials tozalash xatosi:', error);
      return false;
    }
  }

  // Timeout bilan biometric auth
  async authenticateWithTimeout(promptMessage, timeout = CONFIG.BIOMETRIC_TIMEOUT) {
    return new Promise((resolve) => {
      const timeoutId = setTimeout(() => {
        resolve(false);
      }, timeout);

      this.authenticateWithBiometric(promptMessage)
        .then((result) => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch(() => {
          clearTimeout(timeoutId);
          resolve(false);
        });
    });
  }
}

// Notification Service
export class NotificationService {
  constructor() {
    this.notificationListener = null;
    this.init();
  }

  async init() {
    try {
      // Permission so'rash
      const { status } = await Notifications.getPermissionsAsync();
      if (status !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        if (status !== 'granted') {
          console.warn('Push bildirishnomalar uchun ruxsat berilmagan');
          return;
        }
      }

      // Expo push token olish
      const token = await Notifications.getExpoPushTokenAsync();
      console.log('Expo push token:', token.data);

      // Notification listener o'rnatish
      this.notificationListener = Notifications.addNotificationReceivedListener(
        this.handleNotification.bind(this)
      );

      // Channel yaratish (Android)
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('orion-starline-trading', {
          name: 'Orion Starline Trading',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
          sound: 'default',
        });
      }
    } catch (error) {
      console.error('Notification service init xatosi:', error);
    }
  }

  handleNotification(notification) {
    const { data } = notification;
    
    if (data.type === 'trading_signal') {
      this.handleTradingSignal(data);
    } else if (data.type === 'market_alert') {
      this.handleMarketAlert(data);
    } else if (data.type === 'position_update') {
      this.handlePositionUpdate(data);
    }
  }

  handleTradingSignal(data) {
    const { symbol, action, price } = data;
    Alert.alert(
      'Trading Signal',
      `${symbol} juftligida ${action === 'buy' ? 'Sotib olish' : 'Sotish')} signali: ${price}`,
      [
        { text: 'Bekor qilish', style: 'cancel' },
        { text: 'Bajarish', onPress: () => this.executeTradeSignal(data) }
      ]
    );
  }

  handleMarketAlert(data) {
    const { message, severity } = data;
    Alert.alert(
      `Market Alert${severity ? ` - ${severity}` : ''}`,
      message,
      [{ text: 'OK' }]
    );
  }

  handlePositionUpdate(data) {
    const { position, pnl } = data;
    const message = `Pozitsiya ${position.symbol}: P&L ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
    
    // Vibro
    Vibration.vibrate([200, 100, 200]);
    
    Alert.alert('Position Update', message, [{ text: 'OK' }]);
  }

  async executeTradeSignal(data) {
    try {
      // Trading API ga so'rov yuborish
      await fetch(`${CONFIG.API_URL}/api/execute-trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error('Trade signal execution xatosi:', error);
    }
  }

  async sendLocalNotification(title, body, data = {}) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
        },
        trigger: null,
      });
    } catch (error) {
      console.error('Local notification xatosi:', error);
    }
  }

  async scheduleTradingReminder(tradingTime) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Trading Reminder',
          body: `Trading sessiyasi ${tradingTime} da boshlanadi`,
        },
        trigger: {
          date: new Date(tradingTime),
        },
      });
    } catch (error) {
      console.error('Trading reminder xatosi:', error);
    }
  }

  cleanup() {
    if (this.notificationListener) {
      this.notificationListener.remove();
    }
  }
}

// Offline Data Service
export class OfflineDataService {
  constructor() {
    this.maxRecords = CONFIG.MAX_OFFLINE_RECORDS;
  }

  async saveOfflineData(data, type = 'general') {
    try {
      const existingData = await this.getOfflineData();
      const newRecord = {
        id: Date.now(),
        type,
        data,
        timestamp: Date.now(),
      };

      const updatedData = [...existingData, newRecord];

      // Maksimum rekordlar sonini cheklash
      if (updatedData.length > this.maxRecords) {
        updatedData.splice(0, updatedData.length - this.maxRecords);
      }

      await AsyncStorage.setItem(
        CONFIG.OFFLINE_DATA_KEY,
        JSON.stringify(updatedData)
      );

      return true;
    } catch (error) {
      console.error('Offline data saqlash xatosi:', error);
      return false;
    }
  }

  async getOfflineData() {
    try {
      const data = await AsyncStorage.getItem(CONFIG.OFFLINE_DATA_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Offline data olish xatosi:', error);
      return [];
    }
  }

  async clearOfflineData() {
    try {
      await AsyncStorage.removeItem(CONFIG.OFFLINE_DATA_KEY);
      return true;
    } catch (error) {
      console.error('Offline data tozalash xatosi:', error);
      return false;
    }
  }

  async syncOfflineData() {
    try {
      const offlineData = await this.getOfflineData();
      const unsyncedData = offlineData.filter(item => !item.synced);

      if (unsyncedData.length === 0) return { success: true, synced: 0 };

      // API ga sync so'rovi
      const response = await fetch(`${CONFIG.API_URL}/api/sync-offline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: unsyncedData }),
      });

      const result = await response.json();

      if (result.success) {
        // Synced ma'lumotlarni belgilash
        const updatedData = offlineData.map(item => 
          item.synced ? item : { ...item, synced: true }
        );

        await AsyncStorage.setItem(
          CONFIG.OFFLINE_DATA_KEY,
          JSON.stringify(updatedData)
        );

        return { success: true, synced: unsyncedData.length };
      }

      return { success: false, error: result.message };
    } catch (error) {
      console.error('Offline sync xatosi:', error);
      return { success: false, error: error.message };
    }
  }
}

// Location Service
export class LocationService {
  constructor() {
    this.location = null;
    this.watchId = null;
  }

  async getCurrentLocation() {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        throw new Error('Location permission denied');
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
        timeout: CONFIG.LOCATION_TIMEOUT,
      });

      this.location = location;
      return location;
    } catch (error) {
      console.error('Location olish xatosi:', error);
      throw error;
    }
  }

  startWatchingLocation(callback) {
    try {
      this.watchId = Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 10000,
          distanceInterval: 100,
        },
        (location) => {
          this.location = location;
          callback(location);
        }
      );
    } catch (error) {
      console.error('Location watching xatosi:', error);
    }
  }

  stopWatchingLocation() {
    if (this.watchId) {
      this.watchId.remove();
      this.watchId = null;
    }
  }

  async reverseGeocode(latitude, longitude) {
    try {
      const addresses = await Location.reverseGeocodeAsync({
        latitude,
        longitude,
      });
      return addresses[0] || null;
    } catch (error) {
      console.error('Reverse geocode xatosi:', error);
      return null;
    }
  }
}

// Device Info Service
export class DeviceInfoService {
  constructor() {
    this.deviceInfo = {};
    this.init();
  }

  async init() {
    try {
      const deviceInfo = {
        platform: Platform.OS,
        version: Platform.Version,
        model: Platform.OS === 'ios' ? 'iOS Device' : 'Android Device',
        isTablet: width >= 768,
        screenWidth: width,
        screenHeight: height,
        scale: Platform.OS === 'ios' ? 1 : 1,
      };

      this.deviceInfo = deviceInfo;
    } catch (error) {
      console.error('Device info init xatosi:', error);
    }
  }

  getDeviceInfo() {
    return this.deviceInfo;
  }

  isTablet() {
    return this.deviceInfo.isTablet || false;
  }

  getScreenDimensions() {
    return {
      width: this.deviceInfo.screenWidth,
      height: this.deviceInfo.screenHeight,
    };
  }

  isPortrait() {
    return height > width;
  }

  isLandscape() {
    return width > height;
  }
}

// Screenshot Detection Service
export class ScreenshotDetectionService {
  constructor() {
    this.isMonitoring = false;
    this.callback = null;
  }

  startMonitoring(callback) {
    this.callback = callback;
    
    DeviceEventEmitter.addListener('screenshotTaken', () => {
      if (this.callback) {
        this.callback();
      }
    });

    this.isMonitoring = true;
  }

  stopMonitoring() {
    this.isMonitoring = false;
    this.callback = null;
  }
}

// File Management Service
export class FileService {
  constructor() {
    this.baseDirectory = FileSystem.documentDirectory;
  }

  async saveScreenshot(imageUri) {
    try {
      const fileName = `screenshot_${Date.now()}.png`;
      const destination = `${this.baseDirectory}${fileName}`;
      
      await FileSystem.moveAsync({
        from: imageUri,
        to: destination,
      });

      return destination;
    } catch (error) {
      console.error('Screenshot saqlash xatosi:', error);
      throw error;
    }
  }

  async saveDocument(content, fileName, mimeType = 'text/plain') {
    try {
      const destination = `${this.baseDirectory}${fileName}`;
      
      await FileSystem.writeAsStringAsync(destination, content, {
        encoding: FileSystem.EncodingType.UTF8,
      });

      return destination;
    } catch (error) {
      console.error('Document saqlash xatosi:', error);
      throw error;
    }
  }

  async shareFile(fileUri, title = 'Share File') {
    try {
      if (!(await Sharing.isAvailableAsync())) {
        throw new Error('Sharing mavjud emas');
      }

      await Sharing.shareAsync(fileUri, {
        mimeType,
        dialogTitle: title,
      });
    } catch (error) {
      console.error('File sharing xatosi:', error);
      throw error;
    }
  }

  async deleteFile(fileUri) {
    try {
      await FileSystem.deleteAsync(fileUri);
      return true;
    } catch (error) {
      console.error('File o\'chirish xatosi:', error);
      return false;
    }
  }

  async getFileInfo(fileUri) {
    try {
      const info = await FileSystem.getInfoAsync(fileUri);
      return info;
    } catch (error) {
      console.error('File info olish xatosi:', error);
      return null;
    }
  }

  async listFiles() {
    try {
      const files = await FileSystem.readDirectoryAsync(this.baseDirectory);
      return files;
    } catch (error) {
      console.error('File list olish xatosi:', error);
      return [];
    }
  }
}

// QR Code Scanner Component
export const QRCodeScanner = ({ onScan, onError }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    const getCameraPermissions = async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    };

    getCameraPermissions();
  }, []);

  const handleBarCodeScanned = ({ type, data }) => {
    setScanned(true);
    onScan && onScan({ type, data });
    
    // Vibrate
    Vibration.vibrate(200);
  };

  if (hasPermission === null) {
    return <Text>Kamera ruxsati so'ralmoqda...</Text>;
  }

  if (hasPermission === false) {
    return <Text>Kamera ruxsati berilmagan</Text>;
  }

  return (
    <View style={styles.scannerContainer}>
      <BarCodeScanner
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={styles.scanner}
      />
      {scanned && (
        <TouchableOpacity
          style={styles.rescanButton}
          onPress={() => setScanned(false)}
        >
          <Text style={styles.rescanButtonText}>Qayta skaner qilish</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

// Accelerometer Monitor Component
export const AccelerometerMonitor = ({ onMovement, threshold = 0.5 }) => {
  const [accelerometerData, setAccelerometerData] = useState({});

  useEffect(() => {
    const subscription = Accelerometer.addListener((data) => {
      setAccelerometerData(data);
      
      // Harakatni aniqlash
      const magnitude = Math.sqrt(
        data.x * data.x + data.y * data.y + data.z * data.z
      );

      if (magnitude > threshold && onMovement) {
        onMovement(data);
      }
    });

    return () => subscription && subscription.remove();
  }, [onMovement, threshold]);

  return (
    <View style={styles.accelerometerContainer}>
      <Text style={styles.accelerometerText}>
        X: {accelerometerData.x?.toFixed(2) || '0.00'}
      </Text>
      <Text style={styles.accelerometerText}>
        Y: {accelerometerData.y?.toFixed(2) || '0.00'}
      </Text>
      <Text style={styles.accelerometerText}>
        Z: {accelerometerData.z?.toFixed(2) || '0.00'}
      </Text>
    </View>
  );
};

// Trading Performance Chart Component
export const TradingPerformanceChart = ({ data, type = 'line' }) => {
  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 2,
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
    },
  };

  const screenWidth = width - 32;

  if (type === 'line') {
    return (
      <LineChart
        data={data}
        width={screenWidth}
        height={220}
        chartConfig={chartConfig}
        bezier
        style={styles.chart}
      />
    );
  } else if (type === 'bar') {
    return (
      <BarChart
        data={data}
        width={screenWidth}
        height={220}
        chartConfig={chartConfig}
        style={styles.chart}
      />
    );
  } else if (type === 'pie') {
    return (
      <PieChart
        data={data}
        width={screenWidth}
        height={220}
        chartConfig={chartConfig}
        accessor={'population'}
        backgroundColor={'transparent'}
        paddingLeft={'15'}
        style={styles.chart}
      />
    );
  }

  return null;
};

// Web Browser Component
export const WebBrowserComponent = ({ 
  url, 
  onNavigationStateChange,
  onLoadStart,
  onLoadEnd,
  onError 
}) => {
  const [canGoBack, setCanGoBack] = useState(false);

  const handleNavigationStateChange = (navState) => {
    setCanGoBack(navState.canGoBack);
    onNavigationStateChange && onNavigationStateChange(navState);
  };

  return (
    <View style={styles.webBrowserContainer}>
      <View style={styles.webBrowserHeader}>
        <TouchableOpacity
          style={styles.webBrowserButton}
          onPress={() => {
            if (canGoBack) {
              // WebView goBack logic
            }
          }}
        >
          <Icon name="arrow-back" size={24} color="#3b82f6" />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.webBrowserButton}
          onPress={() => WebBrowser.openBrowserAsync(url)}
        >
          <Icon name="open" size={24} color="#3b82f6" />
        </TouchableOpacity>
      </View>

      <WebView
        source={{ uri: url }}
        onNavigationStateChange={handleNavigationStateChange}
        onLoadStart={onLoadStart}
        onLoadEnd={onLoadEnd}
        onError={onError}
        style={styles.webView}
      />
    </View>
  );
};

// Biometric Settings Component
export const BiometricSettings = ({ 
  enabled, 
  onToggle,
  onTest,
  biometricAvailable 
}) => {
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    setTesting(true);
    try {
      await onTest();
    } finally {
      setTesting(false);
    }
  };

  if (!biometricAvailable) {
    return (
      <View style={styles.biometricUnavailable}>
        <Icon name="finger-print-outline" size={48} color="#ccc" />
        <Text style={styles.biometricUnavailableText}>
          Biometrik autentifikatsiya qo'llab-quvvatlanmaydi
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.biometricSettings}>
      <View style={styles.biometricInfo}>
        <Icon name="finger-print" size={24} color="#3b82f6" />
        <View style={styles.biometricDetails}>
          <Text style={styles.biometricTitle}>Biometrik autentifikatsiya</Text>
          <Text style={styles.biometricSubtitle}>
            Touch ID yoki Face ID yordamida kiring
          </Text>
        </View>
      </View>

      <View style={styles.biometricControls}>
        <TouchableOpacity
          style={[styles.biometricButton, testing && styles.biometricButtonDisabled]}
          onPress={handleTest}
          disabled={testing}
        >
          <Text style={styles.biometricButtonText}>
            {testing ? 'Test qilish...' : 'Test qilish'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.biometricToggle}
          onPress={onToggle}
        >
          <Text style={[
            styles.biometricToggleText,
            enabled ? styles.biometricToggleEnabled : styles.biometricToggleDisabled
          ]}>
            {enabled ? 'Yoqilgan' : 'O\'chirilgan'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// Trading Signals Component
export const TradingSignals = ({ signals, onExecuteSignal, onDismissSignal }) => {
  const renderSignal = (signal) => (
    <View key={signal.id} style={styles.tradingSignal}>
      <View style={styles.signalHeader}>
        <Text style={styles.signalPair}>{signal.pair}</Text>
        <View style={[
          styles.signalType,
          signal.action === 'buy' ? styles.signalBuy : styles.signalSell
        ]}>
          <Text style={styles.signalTypeText}>
            {signal.action === 'buy' ? 'SOTIB OLISH' : 'SOTISH'}
          </Text>
        </View>
      </View>

      <View style={styles.signalDetails}>
        <Text style={styles.signalPrice}>Narx: ${signal.price}</Text>
        <Text style={styles.signalConfidence}>Ishonch: {signal.confidence}%</Text>
      </View>

      <View style={styles.signalReason}>
        <Text style={styles.signalReasonText}>{signal.reason}</Text>
      </View>

      <View style={styles.signalActions}>
        <TouchableOpacity
          style={styles.signalExecuteButton}
          onPress={() => onExecuteSignal(signal)}
        >
          <Text style={styles.signalExecuteText}>Bajarish</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.signalDismissButton}
          onPress={() => onDismissSignal(signal.id)}
        >
          <Text style={styles.signalDismissText}>Rad etish</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.tradingSignalsContainer}>
      <Text style={styles.signalsTitle}>Trading Signallari</Text>
      
      {signals.length === 0 ? (
        <Text style={styles.noSignalsText}>
          Yangi trading signallar yo'q
        </Text>
      ) : (
        <ScrollView style={styles.signalsList}>
          {signals.map(renderSignal)}
        </ScrollView>
      )}
    </View>
  );
};

// Market Analysis Component
export const MarketAnalysis = ({ marketData, timeframe = '1D' }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);
  
  const timeframes = ['1H', '4H', '1D', '1W', '1M'];
  
  const getMarketSentiment = (data) => {
    const bulls = data.bullish_signals || 0;
    const bears = data.bearish_signals || 0;
    const total = bulls + bears;
    
    if (total === 0) return { sentiment: 'Neutral', color: '#6b7280' };
    
    const bullishRatio = bulls / total;
    if (bullishRatio > 0.6) {
      return { sentiment: 'Bullish', color: '#10b981' };
    } else if (bullishRatio < 0.4) {
      return { sentiment: 'Bearish', color: '#ef4444' };
    } else {
      return { sentiment: 'Neutral', color: '#6b7280' };
    }
  };

  const sentiment = getMarketSentiment(marketData);

  return (
    <View style={styles.marketAnalysis}>
      <View style={styles.analysisHeader}>
        <Text style={styles.analysisTitle}>Market Analysis</Text>
        <View style={styles.timeframeSelector}>
          {timeframes.map((tf) => (
            <TouchableOpacity
              key={tf}
              style={[
                styles.timeframeButton,
                selectedTimeframe === tf && styles.timeframeButtonActive
              ]}
              onPress={() => setSelectedTimeframe(tf)}
            >
              <Text style={[
                styles.timeframeText,
                selectedTimeframe === tf && styles.timeframeTextActive
              ]}>
                {tf}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.sentimentContainer}>
        <Text style={styles.sentimentLabel}>Market Sentiment</Text>
        <View style={styles.sentimentIndicator}>
          <View style={[
            styles.sentimentColor,
            { backgroundColor: sentiment.color }
          ]} />
          <Text style={[
            styles.sentimentText,
            { color: sentiment.color }
          ]}>
            {sentiment.sentiment}
          </Text>
        </View>
      </View>

      <View style={styles.analysisStats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Volatility</Text>
          <Text style={styles.statValue}>
            {marketData.volatility?.toFixed(2) || '0.00'}%
          </Text>
        </View>
        
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Volume</Text>
          <Text style={styles.statValue}>
            {marketData.volume ? marketData.volume.toLocaleString() : '0'}
          </Text>
        </View>
        
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>RSI</Text>
          <Text style={styles.statValue}>
            {marketData.rsi?.toFixed(1) || '0.0'}
          </Text>
        </View>
      </View>
    </View>
  );
};

// Risk Management Component
export const RiskManagement = ({ 
  portfolioValue, 
  maxRisk, 
  currentRisk, 
  onUpdateRisk 
}) => {
  const riskPercentage = (currentRisk / maxRisk) * 100;
  const isHighRisk = currentRisk > maxRisk * 0.8;

  return (
    <View style={styles.riskManagement}>
      <View style={styles.riskHeader}>
        <Text style={styles.riskTitle}>Risk Management</Text>
        {isHighRisk && (
          <View style={styles.highRiskAlert}>
            <Icon name="warning" size={16} color="#ef4444" />
            <Text style={styles.highRiskText}>Yuqori Risk</Text>
          </View>
        )}
      </View>

      <View style={styles.riskMetrics}>
        <View style={styles.riskMetric}>
          <Text style={styles.riskMetricLabel}>Portfolio Value</Text>
          <Text style={styles.riskMetricValue}>
            ${portfolioValue.toLocaleString()}
          </Text>
        </View>
        
        <View style={styles.riskMetric}>
          <Text style={styles.riskMetricLabel}>Current Risk</Text>
          <Text style={[
            styles.riskMetricValue,
            isHighRisk && styles.highRiskValue
          ]}>
            ${currentRisk.toLocaleString()}
          </Text>
        </View>
        
        <View style={styles.riskMetric}>
          <Text style={styles.riskMetricLabel}>Max Risk</Text>
          <Text style={styles.riskMetricValue}>
            ${maxRisk.toLocaleString()}
          </Text>
        </View>
      </View>

      <View style={styles.riskProgress}>
        <Text style={styles.riskProgressLabel}>
          Risk Usage: {riskPercentage.toFixed(1)}%
        </Text>
        <View style={styles.riskProgressBar}>
          <View style={[
            styles.riskProgressFill,
            {
              width: `${Math.min(riskPercentage, 100)}%`,
              backgroundColor: isHighRisk ? '#ef4444' : '#10b981'
            }
          ]} />
        </View>
      </View>
    </View>
  );
};

// Utility Hooks
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected);
    });

    return unsubscribe;
  }, []);

  return isOnline;
};

export const useAppState = () => {
  const [appState, setAppState] = useState(AppState.currentState);

  useEffect(() => {
    const subscription = AppState.addEventListener('change', nextAppState => {
      setAppState(nextAppState);
    });

    return () => {
      subscription.remove();
    };
  }, []);

  return appState;
};

export const useBackHandler = (callback) => {
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', callback);
    return () => backHandler.remove();
  }, [callback]);
};

// Uslub
const styles = StyleSheet.create({
  // QR Scanner styles
  scannerContainer: {
    flex: 1,
  },
  scanner: {
    flex: 1,
  },
  rescanButton: {
    position: 'absolute',
    bottom: 50,
    left: width / 2 - 75,
    width: 150,
    height: 40,
    backgroundColor: '#3b82f6',
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rescanButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },

  // Accelerometer styles
  accelerometerContainer: {
    padding: 16,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
  },
  accelerometerText: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4,
  },

  // Chart styles
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },

  // Web Browser styles
  webBrowserContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  webBrowserHeader: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
    backgroundColor: 'white',
  },
  webBrowserButton: {
    padding: 8,
    marginRight: 16,
  },
  webView: {
    flex: 1,
  },

  // Biometric styles
  biometricUnavailable: {
    alignItems: 'center',
    padding: 32,
  },
  biometricUnavailableText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 16,
    textAlign: 'center',
  },
  biometricSettings: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  biometricInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  biometricDetails: {
    marginLeft: 12,
  },
  biometricTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  biometricSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  biometricControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  biometricButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  biometricButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  biometricButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  biometricToggle: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  biometricToggleEnabled: {
    color: '#10b981',
  },
  biometricToggleDisabled: {
    color: '#ef4444',
  },
  biometricToggleText: {
    fontSize: 12,
    fontWeight: '600',
  },

  // Trading Signals styles
  tradingSignalsContainer: {
    flex: 1,
    padding: 16,
  },
  signalsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  noSignalsText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 32,
  },
  signalsList: {
    flex: 1,
  },
  tradingSignal: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  signalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  signalPair: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  signalType: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  signalBuy: {
    backgroundColor: '#dcfce7',
  },
  signalSell: {
    backgroundColor: '#fef2f2',
  },
  signalTypeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  signalDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  signalPrice: {
    fontSize: 14,
    color: '#374151',
  },
  signalConfidence: {
    fontSize: 14,
    color: '#6b7280',
  },
  signalReason: {
    marginBottom: 12,
  },
  signalReasonText: {
    fontSize: 14,
    color: '#4b5563',
    fontStyle: 'italic',
  },
  signalActions: {
    flexDirection: 'row',
    gap: 8,
  },
  signalExecuteButton: {
    flex: 1,
    backgroundColor: '#10b981',
    paddingVertical: 8,
    borderRadius: 4,
    alignItems: 'center',
  },
  signalExecuteText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  signalDismissButton: {
    flex: 1,
    backgroundColor: '#ef4444',
    paddingVertical: 8,
    borderRadius: 4,
    alignItems: 'center',
  },
  signalDismissText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },

  // Market Analysis styles
  marketAnalysis: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  analysisHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  analysisTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  timeframeSelector: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    borderRadius: 6,
  },
  timeframeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  timeframeButtonActive: {
    backgroundColor: 'white',
  },
  timeframeText: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '600',
  },
  timeframeTextActive: {
    color: '#1f2937',
  },
  sentimentContainer: {
    marginBottom: 16,
  },
  sentimentLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  sentimentIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sentimentColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  sentimentText: {
    fontSize: 14,
    fontWeight: '600',
  },
  analysisStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
  },

  // Risk Management styles
  riskManagement: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  riskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  riskTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  highRiskAlert: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  highRiskText: {
    fontSize: 12,
    color: '#ef4444',
    fontWeight: '600',
    marginLeft: 4,
  },
  riskMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  riskMetric: {
    alignItems: 'center',
  },
  riskMetricLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  riskMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
  },
  highRiskValue: {
    color: '#ef4444',
  },
  riskProgress: {
    marginBottom: 8,
  },
  riskProgressLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 8,
  },
  riskProgressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  riskProgressFill: {
    height: '100%',
    borderRadius: 4,
  },
});

// Service instances
export const authService = new AuthenticationService();
export const notificationService = new NotificationService();
export const offlineDataService = new OfflineDataService();
export const locationService = new LocationService();
export const deviceInfoService = new DeviceInfoService();
export const screenshotService = new ScreenshotDetectionService();
export const fileService = new FileService();

export default {
  AuthenticationService,
  NotificationService,
  OfflineDataService,
  LocationService,
  DeviceInfoService,
  ScreenshotDetectionService,
  FileService,
  QRCodeScanner,
  AccelerometerMonitor,
  TradingPerformanceChart,
  WebBrowserComponent,
  BiometricSettings,
  TradingSignals,
  MarketAnalysis,
  RiskManagement,
  useOnlineStatus,
  useAppState,
  useBackHandler,
};