"""
React Native Mobile App - Orion Starline
iOS va Android uchun to'liq support, offline rejim, push bildirishnomalar,
Touch ID/Face ID, mobile trading interface, responsive design

Author: Orion Starline AI Trading System
Date: 2025-11-05
"""

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  StatusBar,
  Platform,
  Dimensions,
  Modal,
  ScrollView,
  Switch,
  Vibration,
  Animated,
  RefreshControl,
  NetInfo,
  AsyncStorage,
  PushNotificationIOS,
  AppState,
  Linking,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/Ionicons';
import { LinearGradient } from 'expo-linear-gradient';
import { WebView } from 'react-native-webview';
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as LocalAuthentication from 'expo-local-authentication';
import * as Notifications from 'expo-notifications';
import * as SecureStore from 'expo-secure-store';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width, height } = Dimensions.get('window');

// Konfiguratsiya
const CONFIG = {
  API_URL: 'https://api.orionstarline.com',
  WS_URL: 'wss://ws.orionstarline.com',
  BIOMETRIC_ENABLED: true,
  OFFLINE_CACHE_DURATION: 24 * 60 * 60 * 1000, // 24 soat
  REFRESH_INTERVAL: 5000, // 5 soniya
  PUSH_NOTIFICATION_CHANNEL_ID: 'orion-starline-trading',
};

// Push bildirishnomalar konfiguratsiyasi
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Bosh sahifa komponenti
const HomeScreen = ({ navigation }) => {
  const [marketData, setMarketData] = useState([]);
  const [userBalance, setUserBalance] = useState(0);
  const [isOffline, setIsOffline] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);

  useEffect(() => {
    loadUserData();
    checkBiometricAuth();
    subscribeToNetworkStatus();
    subscribeToPushNotifications();
    
    const interval = setInterval(loadMarketData, CONFIG.REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const parsed = JSON.parse(userData);
        setUserBalance(parsed.balance || 0);
      }
    } catch (error) {
      console.error('Foydalanuvchi ma\'lumotlarini yuklashda xatolik:', error);
    }
  };

  const checkBiometricAuth = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (hasHardware && isEnrolled) {
        setBiometricEnabled(true);
      }
    } catch (error) {
      console.error('Biometrik autentifikatsiyani tekshirishda xatolik:', error);
    }
  };

  const subscribeToNetworkStatus = () => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOffline(!state.isConnected);
    });
    return unsubscribe;
  };

  const subscribeToPushNotifications = async () => {
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== 'granted') {
        Alert.alert('Xatolik', 'Push bildirishnomalar uchun ruxsat kerak');
        return;
      }
      const token = await Notifications.getExpoPushTokenAsync();
      console.log('Push token:', token.data);
    } catch (error) {
      console.error('Push bildirishnomalar ruxsatini olishda xatolik:', error);
    }
  };

  const loadMarketData = async () => {
    try {
      if (isOffline) {
        const cachedData = await AsyncStorage.getItem('cached_market_data');
        if (cachedData) {
          setMarketData(JSON.parse(cachedData));
        }
        return;
      }

      // API dan ma'lumotlarni olish
      const response = await fetch(`${CONFIG.API_URL}/api/market-data`);
      const data = await response.json();
      setMarketData(data);
      
      // Offline rejim uchun saqlash
      await AsyncStorage.setItem('cached_market_data', JSON.stringify(data));
      await AsyncStorage.setItem('cache_timestamp', Date.now().toString());
    } catch (error) {
      console.error('Bozor ma\'lumotlarini yuklashda xatolik:', error);
      // Offline data ni yuklash
      const cachedData = await AsyncStorage.getItem('cached_market_data');
      if (cachedData) {
        setMarketData(JSON.parse(cachedData));
      }
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadMarketData().then(() => setRefreshing(false));
  }, []);

  const handleBiometricLogin = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Biometrik autentifikatsiya',
        fallbackLabel: 'Alternativ kirish usulini tanlang',
        disableDeviceFallback: false,
      });

      if (result.success) {
        navigation.navigate('Trading');
      } else {
        Alert.alert('Xatolik', 'Biometrik autentifikatsiya muvaffaqiyatsiz');
      }
    } catch (error) {
      console.error('Biometrik login xatosi:', error);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#1e3a8a" />
      
      {/* Header */}
      <LinearGradient colors={['#1e3a8a', '#3b82f6']} style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Orion Starline</Text>
          <View style={styles.headerRight}>
            <Icon 
              name={isOffline ? "cloud-offline" : "cloud-outline"} 
              size={24} 
              color={isOffline ? "#fbbf24" : "#10b981"} 
            />
            {biometricEnabled && (
              <TouchableOpacity onPress={handleBiometricLogin} style={styles.bioButton}>
                <Icon name="finger-print" size={24} color="white" />
              </TouchableOpacity>
            )}
          </View>
        </View>
        
        {/* Balans */}
        <View style={styles.balanceContainer}>
          <Text style={styles.balanceLabel}>Umumiy Balans</Text>
          <Text style={styles.balanceAmount}>
            ${userBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </Text>
        </View>
      </LinearGradient>

      {/* Market Data */}
      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {isOffline && (
          <View style={styles.offlineBanner}>
            <Icon name="cloud-offline" size={16} color="#fbbf24" />
            <Text style={styles.offlineText}>Offline rejim - so'nggi ma'lumotlar</Text>
          </View>
        )}

        {/* Bozorchilik jadvallari */}
        <View style={styles.marketSection}>
          <Text style={styles.sectionTitle}>Bozor Ma'lumotlari</Text>
          {marketData.map((item, index) => (
            <View key={index} style={styles.marketItem}>
              <View style={styles.marketItemLeft}>
                <Text style={styles.currencyPair}>{item.symbol}</Text>
                <Text style={styles.currencyName}>{item.name}</Text>
              </View>
              <View style={styles.marketItemRight}>
                <Text style={styles.price}>${item.price.toFixed(5)}</Text>
                <Text style={[
                  styles.change,
                  item.change >= 0 ? styles.positive : styles.negative
                ]}>
                  {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
                </Text>
              </View>
            </View>
          ))}
        </View>

        {/* Tez harakatlar */}
        <View style={styles.quickActions}>
          <TouchableOpacity 
            style={[styles.actionButton, styles.buyButton]}
            onPress={() => navigation.navigate('Trading', { action: 'buy' })}
          >
            <Icon name="trending-up" size={20} color="white" />
            <Text style={styles.actionButtonText}>Sotib Olish</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionButton, styles.sellButton]}
            onPress={() => navigation.navigate('Trading', { action: 'sell' })}
          >
            <Icon name="trending-down" size={20} color="white" />
            <Text style={styles.actionButtonText}>Sotish</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// Trading komponenti
const TradingScreen = ({ route, navigation }) => {
  const [selectedPair, setSelectedPair] = useState('EUR/USD');
  const [amount, setAmount] = useState('');
  const [action, setAction] = useState('buy');
  const [currentPrice, setCurrentPrice] = useState(1.0987);
  const [isExecuting, setIsExecuting] = useState(false);

  useEffect(() => {
    if (route.params?.action) {
      setAction(route.params.action);
    }
    loadCurrentPrice();
  }, []);

  const loadCurrentPrice = async () => {
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/price/${selectedPair}`);
      const data = await response.json();
      setCurrentPrice(data.price);
    } catch (error) {
      console.error('Narxni yuklashda xatolik:', error);
    }
  };

  const executeTrade = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('Xatolik', 'Miqdorni kiriting');
      return;
    }

    setIsExecuting(true);
    try {
      const tradeData = {
        pair: selectedPair,
        action: action,
        amount: parseFloat(amount),
        price: currentPrice,
      };

      const response = await fetch(`${CONFIG.API_URL}/api/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tradeData),
      });

      const result = await response.json();
      
      if (result.success) {
        Vibration.vibrate();
        Alert.alert(
          'Muvaffaqiyat', 
          `${action === 'buy' ? 'Sotib olish' : 'Sotish')} buyurtmasi bajarildi`,
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack()
            }
          ]
        );
      } else {
        Alert.alert('Xatolik', result.message || 'Buyurtma bajarilmadi');
      }
    } catch (error) {
      console.error('Trading xatosi:', error);
      Alert.alert('Xatolik', 'Internet aloqasi tekshiring');
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#1e3a8a" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Bozorchilik</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Valyuta jufti tanlash */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Valyuta Jufti</Text>
          <TouchableOpacity style={styles.pickerButton}>
            <Text style={styles.pickerText}>{selectedPair}</Text>
            <Icon name="chevron-down" size={20} color="#666" />
          </TouchableOpacity>
        </View>

        {/* Joriy narx */}
        <View style={styles.priceInfo}>
          <Text style={styles.priceLabel}>Joriy Narx</Text>
          <Text style={styles.priceValue}>${currentPrice.toFixed(5)}</Text>
        </View>

        {/* Miqdor kiritish */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Miqdor (USD)</Text>
          <TextInput
            style={styles.textInput}
            value={amount}
            onChangeText={setAmount}
            placeholder="Miqdorni kiriting"
            keyboardType="numeric"
          />
        </View>

        {/* Amal tanlash */}
        <View style={styles.actionSelector}>
          <TouchableOpacity 
            style={[styles.actionTab, action === 'buy' && styles.actionTabActive]}
            onPress={() => setAction('buy')}
          >
            <Text style={[styles.actionTabText, action === 'buy' && styles.actionTabTextActive]}>
              Sotib Olish
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionTab, action === 'sell' && styles.actionTabActive]}
            onPress={() => setAction('sell')}
          >
            <Text style={[styles.actionTabText, action === 'sell' && styles.actionTabTextActive]}>
              Sotish
            </Text>
          </TouchableOpacity>
        </View>

        {/* Hisoblash natijasi */}
        {amount && (
          <View style={styles.calculationResult}>
            <Text style={styles.calcText}>
              {action === 'buy' ? 'Olinadigan' : 'Beriladigan'}: {(parseFloat(amount) / currentPrice).toFixed(2)} {selectedPair.split('/')[0]}
            </Text>
          </View>
        )}

        {/* Bajarish tugmasi */}
        <TouchableOpacity 
          style={[styles.executeButton, action === 'buy' ? styles.buyButton : styles.sellButton, isExecuting && styles.executeButtonDisabled]}
          onPress={executeTrade}
          disabled={isExecuting}
        >
          <Text style={styles.executeButtonText}>
            {isExecuting ? 'Bajarilmoqda...' : `Bajarish ${action === 'buy' ? 'Sotib Olish' : 'Sotish'}`}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

// Portfolio komponenti
const PortfolioScreen = ({ navigation }) => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPositions();
  }, []);

  const loadPositions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${CONFIG.API_URL}/api/positions`);
      const data = await response.json();
      setPositions(data.positions || []);
    } catch (error) {
      console.error('Pozitsiyalarni yuklashda xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const closePosition = async (positionId) => {
    Alert.alert(
      'Pozitsiyani yopish',
      'Ushbu pozitsiyani yopmoqchimisiz?',
      [
        { text: 'Bekor qilish', style: 'cancel' },
        {
          text: 'Yopish',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(`${CONFIG.API_URL}/api/close-position`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ positionId }),
              });
              
              const result = await response.json();
              if (result.success) {
                loadPositions(); // Ro'yxatni qayta yuklash
                Alert.alert('Muvaffaqiyat', 'Pozitsiya yopildi');
              }
            } catch (error) {
              console.error('Pozitsiyani yopishda xatolik:', error);
              Alert.alert('Xatolik', 'Pozitsiyani yopishda xatolik yuz berdi');
            }
          }
        }
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Yuklanmoqda...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#1e3a8a" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Portfolio</Text>
      </View>

      <ScrollView style={styles.content}>
        {positions.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="folder-open-outline" size={64} color="#ccc" />
            <Text style={styles.emptyStateText}>Hech qanday pozitsiya yo'q</Text>
          </View>
        ) : (
          positions.map((position, index) => (
            <View key={index} style={styles.positionCard}>
              <View style={styles.positionHeader}>
                <Text style={styles.positionSymbol}>{position.symbol}</Text>
                <Text style={[
                  styles.positionType,
                  position.type === 'buy' ? styles.buyType : styles.sellType
                ]}>
                  {position.type === 'buy' ? 'LONG' : 'SHORT'}
                </Text>
              </View>
              
              <View style={styles.positionInfo}>
                <View style={styles.positionRow}>
                  <Text style={styles.positionLabel}>Miqdor:</Text>
                  <Text style={styles.positionValue}>{position.amount}</Text>
                </View>
                <View style={styles.positionRow}>
                  <Text style={styles.positionLabel}>Kirish narxi:</Text>
                  <Text style={styles.positionValue}>${position.entryPrice.toFixed(5)}</Text>
                </View>
                <View style={styles.positionRow}>
                  <Text style={styles.positionLabel}>Joriy P&L:</Text>
                  <Text style={[
                    styles.positionValue,
                    position.pnl >= 0 ? styles.positive : styles.negative
                  ]}>
                    ${position.pnl.toFixed(2)} ({position.pnlPercent.toFixed(2)}%)
                  </Text>
                </View>
              </View>

              <TouchableOpacity 
                style={styles.closeButton}
                onPress={() => closePosition(position.id)}
              >
                <Text style={styles.closeButtonText}>Yopish</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

// Sozlamalar komponenti
const SettingsScreen = ({ navigation }) => {
  const [settings, setSettings] = useState({
    notificationsEnabled: true,
    biometricEnabled: false,
    soundEnabled: true,
    vibrationEnabled: true,
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const savedSettings = await AsyncStorage.getItem('app_settings');
      if (savedSettings) {
        setSettings(JSON.parse(savedSettings));
      }
    } catch (error) {
      console.error('Sozlamalarni yuklashda xatolik:', error);
    }
  };

  const saveSettings = async (newSettings) => {
    try {
      setSettings(newSettings);
      await AsyncStorage.setItem('app_settings', JSON.stringify(newSettings));
    } catch (error) {
      console.error('Sozlamalarni saqlashda xatolik:', error);
    }
  };

  const toggleBiometric = async (value) => {
    if (value) {
      try {
        const result = await LocalAuthentication.authenticateAsync({
          promptMessage: 'Biometrik autentifikatsiyani yoqish',
        });
        
        if (result.success) {
          saveSettings({ ...settings, biometricEnabled: value });
          Alert.alert('Muvaffaqiyat', 'Biometrik autentifikatsiya yoqildi');
        }
      } catch (error) {
        console.error('Biometrik sozlashda xatolik:', error);
        Alert.alert('Xatolik', 'Biometrik autentifikatsiya yoqilmadi');
      }
    } else {
      saveSettings({ ...settings, biometricEnabled: value });
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#1e3a8a" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Sozlamalar</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Bildirishnomalar */}
        <View style={styles.settingSection}>
          <Text style={styles.sectionTitle}>Bildirishnomalar</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="notifications-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Push bildirishnomalar</Text>
            </View>
            <Switch
              value={settings.notificationsEnabled}
              onValueChange={(value) => saveSettings({ ...settings, notificationsEnabled: value })}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="musical-notes-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Ovozli bildirishnomalar</Text>
            </View>
            <Switch
              value={settings.soundEnabled}
              onValueChange={(value) => saveSettings({ ...settings, soundEnabled: value })}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="vibrate-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Titreşim</Text>
            </View>
            <Switch
              value={settings.vibrationEnabled}
              onValueChange={(value) => saveSettings({ ...settings, vibrationEnabled: value })}
            />
          </View>
        </View>

        {/* Xavfsizlik */}
        <View style={styles.settingSection}>
          <Text style={styles.sectionTitle}>Xavfsizlik</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="finger-print-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Biometrik autentifikatsiya</Text>
            </View>
            <Switch
              value={settings.biometricEnabled}
              onValueChange={toggleBiometric}
            />
          </View>
        </View>

        {/* Ma'lumot */}
        <View style={styles.settingSection}>
          <Text style={styles.sectionTitle}>Ilova ma'lumotlari</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="information-circle-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Versiya</Text>
            </View>
            <Text style={styles.settingItemValue}>1.0.0</Text>
          </View>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingItemLeft}>
              <Icon name="shield-checkmark-outline" size={24} color="#666" />
              <Text style={styles.settingItemText}>Maxfiylik siyosati</Text>
            </View>
            <Icon name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// Asosiy Tab Navigator
const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Home':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Trading':
              iconName = focused ? 'trending-up' : 'trending-up-outline';
              break;
            case 'Portfolio':
              iconName = focused ? 'folder' : 'folder-outline';
              break;
            case 'Settings':
              iconName = focused ? 'settings' : 'settings-outline';
              break;
            default:
              iconName = 'home-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#666',
        tabBarStyle: styles.tabBar,
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
};

// Login komponenti
const LoginScreen = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      setBiometricAvailable(hasHardware && isEnrolled);
    } catch (error) {
      console.error('Biometrik tekshirishda xatolik:', error);
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Xatolik', 'Foydalanuvchi nomi va parolni kiriting');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      
      if (data.success) {
        await AsyncStorage.setItem('user_token', data.token);
        await AsyncStorage.setItem('user_data', JSON.stringify(data.user));
        onLogin();
      } else {
        Alert.alert('Xatolik', data.message || 'Kirish ma\'lumotlari noto\'g\'ri');
      }
    } catch (error) {
      console.error('Login xatosi:', error);
      Alert.alert('Xatolik', 'Internet aloqasi tekshiring');
    } finally {
      setLoading(false);
    }
  };

  const handleBiometricLogin = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Biometrik autentifikatsiya',
        fallbackLabel: 'Alternativ kirish usulini tanlang',
      });

      if (result.success) {
        // Biometrik autentifikatsiya muvaffaqiyatli - keyingi bosqichda
        const savedCredentials = await SecureStore.getItemAsync('biometric_credentials');
        if (savedCredentials) {
          const { username: savedUsername, password: savedPassword } = JSON.parse(savedCredentials);
          setUsername(savedUsername);
          setPassword(savedPassword);
          handleLogin();
        }
      }
    } catch (error) {
      console.error('Biometrik login xatosi:', error);
    }
  };

  return (
    <SafeAreaView style={styles.loginContainer}>
      <StatusBar barStyle="light-content" backgroundColor="#1e3a8a" />
      
      <LinearGradient colors={['#1e3a8a', '#3b82f6']} style={styles.loginHeader}>
        <View style={styles.logoContainer}>
          <Text style={styles.appTitle}>Orion Starline</Text>
          <Text style={styles.appSubtitle}>AI Trading Platform</Text>
        </View>
      </LinearGradient>

      <View style={styles.loginForm}>
        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>Foydalanuvchi nomi</Text>
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            placeholder="Foydalanuvchi nomini kiriting"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>Parol</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="Parolni kiriting"
            secureTextEntry
          />
        </View>

        <TouchableOpacity 
          style={[styles.loginButton, loading && styles.loginButtonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={styles.loginButtonText}>
            {loading ? 'Kirish...' : 'Kirish'}
          </Text>
        </TouchableOpacity>

        {biometricAvailable && (
          <TouchableOpacity 
            style={styles.biometricButton}
            onPress={handleBiometricLogin}
          >
            <Icon name="finger-print" size={24} color="#3b82f6" />
            <Text style={styles.biometricButtonText}>Biometrik autentifikatsiya</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.forgotPassword}>
          <Text style={styles.forgotPasswordText}>Parolni unutdingizmi?</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

// Asosiy App komponenti
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [appState, setAppState] = useState(AppState.currentState);

  useEffect(() => {
    checkAuthStatus();
    setupAppStateListener();
    setupPushNotifications();
    setupOfflineHandling();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('user_token');
      setIsLoggedIn(!!token);
    } catch (error) {
      console.error('Auth statusni tekshirishda xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupAppStateListener = () => {
    const subscription = AppState.addEventListener('change', nextAppState => {
      setAppState(nextAppState);
      if (nextAppState === 'background') {
        // Ilova fon режимига o'tdi
        console.log('Ilova fon режимига o\'tdi');
      } else if (nextAppState === 'active') {
        // Ilova aktiv bo'ldi
        checkAuthStatus();
        // Offline ma'lumotlarni yangilash
        syncOfflineData();
      }
    });

    return () => {
      subscription.remove();
    };
  };

  const setupPushNotifications = () => {
    // Push bildirishnomalar sozlamasi
    Notifications.scheduleNotificationAsync({
      content: {
        title: 'Orion Starline',
        body: 'Bozor ma\'lumotlari yangilandi!',
      },
      trigger: null, // Darhol yuborish
    });
  };

  const setupOfflineHandling = () => {
    NetInfo.addEventListener(state => {
      if (!state.isConnected) {
        // Offline rejim - ma'lumotlarni local cache dan yuklash
        console.log('Offline rejim aktiv');
      } else {
        // Online rejim - ma'lumotlarni server dan sinxronlash
        syncOfflineData();
      }
    });
  };

  const syncOfflineData = async () => {
    try {
      // Offline rejimda yaratilgan ma'lumotlarni server ga yuborish
      const offlineTrades = await AsyncStorage.getItem('offline_trades');
      if (offlineTrades) {
        const trades = JSON.parse(offlineTrades);
        // Trades ni server ga yuborish
        await fetch(`${CONFIG.API_URL}/api/sync-offline-trades`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ trades }),
        });
        // Sync qilingan trade larni o'chirish
        await AsyncStorage.removeItem('offline_trades');
      }
    } catch (error) {
      console.error('Offline data sync xatosi:', error);
    }
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('user_token');
      await AsyncStorage.removeItem('user_data');
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Logout xatosi:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <StatusBar barStyle="dark-content" backgroundColor="#1e3a8a" />
        <LinearGradient colors={['#1e3a8a', '#3b82f6']} style={styles.loadingGradient}>
          <Icon name="trending-up" size={64} color="white" />
          <Text style={styles.loadingTitle}>Orion Starline</Text>
          <Text style={styles.loadingSubtitle}>Yuklanmoqda...</Text>
        </LinearGradient>
      </View>
    );
  }

  return (
    <NavigationContainer>
      {isLoggedIn ? (
        <MainTabs />
      ) : (
        <LoginScreen onLogin={handleLogin} />
      )}
    </NavigationContainer>
  );
};

// Uslub
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingGradient: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 16,
  },
  loadingSubtitle: {
    fontSize: 16,
    color: 'white',
    marginTop: 8,
  },
  loadingText: {
    fontSize: 18,
    color: '#666',
  },
  loginContainer: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loginHeader: {
    height: height * 0.4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    alignItems: 'center',
  },
  appTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  appSubtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  loginForm: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
  },
  loginButton: {
    height: 50,
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
  },
  loginButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  loginButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 50,
    borderWidth: 1,
    borderColor: '#3b82f6',
    borderRadius: 8,
    marginTop: 16,
  },
  biometricButtonText: {
    fontSize: 16,
    color: '#3b82f6',
    marginLeft: 8,
  },
  forgotPassword: {
    marginTop: 24,
    alignItems: 'center',
  },
  forgotPasswordText: {
    fontSize: 16,
    color: '#3b82f6',
  },
  header: {
    backgroundColor: '#1e3a8a',
    padding: 16,
    paddingTop: 8,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  bioButton: {
    marginLeft: 16,
  },
  balanceContainer: {
    marginTop: 16,
  },
  balanceLabel: {
    fontSize: 14,
    color: '#cbd5e1',
    marginBottom: 4,
  },
  balanceAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  offlineBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef3c7',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  offlineText: {
    fontSize: 14,
    color: '#92400e',
    marginLeft: 8,
  },
  marketSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  marketItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  marketItemLeft: {
    flex: 1,
  },
  currencyPair: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  currencyName: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  marketItemRight: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  change: {
    fontSize: 14,
    marginTop: 2,
  },
  positive: {
    color: '#10b981',
  },
  negative: {
    color: '#ef4444',
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
  },
  buyButton: {
    backgroundColor: '#10b981',
  },
  sellButton: {
    backgroundColor: '#ef4444',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
    marginLeft: 8,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  pickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 50,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    backgroundColor: 'white',
  },
  pickerText: {
    fontSize: 16,
    color: '#1f2937',
  },
  priceInfo: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  textInput: {
    height: 50,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
  },
  actionSelector: {
    flexDirection: 'row',
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    marginBottom: 20,
  },
  actionTab: {
    flex: 1,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8,
  },
  actionTabActive: {
    backgroundColor: 'white',
  },
  actionTabText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6b7280',
  },
  actionTabTextActive: {
    color: '#1f2937',
  },
  calculationResult: {
    backgroundColor: '#f8fafc',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    alignItems: 'center',
  },
  calcText: {
    fontSize: 16,
    color: '#1f2937',
  },
  executeButton: {
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  executeButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  executeButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 16,
  },
  positionCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  positionSymbol: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  positionType: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  buyType: {
    backgroundColor: '#dcfce7',
    color: '#166534',
  },
  sellType: {
    backgroundColor: '#fef2f2',
    color: '#dc2626',
  },
  positionInfo: {
    marginBottom: 12,
  },
  positionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  positionLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  positionValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1f2937',
  },
  closeButton: {
    backgroundColor: '#ef4444',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
    alignSelf: 'flex-end',
  },
  closeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: 'white',
  },
  settingSection: {
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 16,
    padding: 16,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  settingItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingItemText: {
    fontSize: 16,
    color: '#1f2937',
    marginLeft: 12,
  },
  settingItemValue: {
    fontSize: 16,
    color: '#6b7280',
  },
  tabBar: {
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingBottom: Platform.OS === 'ios' ? 20 : 5,
    height: Platform.OS === 'ios' ? 80 : 60,
  },
});

export default App;