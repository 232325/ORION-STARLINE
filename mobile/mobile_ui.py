"""
React Native Mobile UI Komponentlari - Orion Starline
Mobile UI komponentlari, responsive design, iOS va Android uchun optimallash

Author: Orion Starline AI Trading System
Date: 2025-11-05
"""

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  Modal,
  TextInput,
  ScrollView,
  Alert,
  Platform,
  Image,
  FlatList,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from 'react-native-vector-icons/Ionicons';
import { WebView } from 'react-native-webview';
import { PieChart, BarChart, LineChart } from 'react-native-chart-kit';

const { width, height } = Dimensions.get('window');

// Responsive design helper
const scale = width / 375;
const normalize = (size) => {
  const newSize = size * scale;
  if (Platform.OS === 'ios') {
    return Math.round(newSize);
  }
  return Math.round(newSize);
};

// Ranglar palitrasi
const COLORS = {
  primary: '#1e3a8a',
  secondary: '#3b82f6',
  success: '#10b981',
  danger: '#ef4444',
  warning: '#f59e0b',
  info: '#06b6d4',
  light: '#f8fafc',
  dark: '#1f2937',
  white: '#ffffff',
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
};

// Asosiy Card komponenti
export const Card = ({ 
  children, 
  style, 
  onPress, 
  gradient = false,
  colors = [COLORS.white, COLORS.white],
  borderRadius = 12,
  elevation = 2,
  padding = 16,
  margin = 0,
}) => {
  const cardStyle = [
    styles.card,
    {
      borderRadius: normalize(borderRadius),
      padding: normalize(padding),
      margin: normalize(margin),
      elevation: elevation,
    },
    style,
  ];

  if (gradient && onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.9}>
        <LinearGradient colors={colors} style={cardStyle}>
          {children}
        </LinearGradient>
      </TouchableOpacity>
    );
  }

  if (gradient) {
    return (
      <LinearGradient colors={colors} style={cardStyle}>
        {children}
      </LinearGradient>
    );
  }

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.9} style={cardStyle}>
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={cardStyle}>{children}</View>;
};

// Button komponenti
export const Button = ({
  children,
  onPress,
  style,
  textStyle,
  variant = 'primary', // primary, secondary, outline, ghost
  size = 'medium', // small, medium, large
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
}) => {
  const buttonStyle = [
    styles.button,
    styles[`button_${variant}`],
    styles[`button_${size}`],
    disabled && styles.button_disabled,
    loading && styles.button_loading,
    fullWidth && styles.button_fullWidth,
    style,
  ];

  const textStyleCombined = [
    styles[`button_text_${variant}`],
    styles[`button_text_${size}`],
    disabled && styles.button_text_disabled,
    textStyle,
  ];

  const renderContent = () => {
    if (loading) {
      return (
        <View style={styles.buttonContent}>
          <Icon 
            name="refresh" 
            size={16} 
            color={variant === 'primary' ? 'white' : COLORS.primary}
            style={styles.buttonIcon}
          />
          <Text style={textStyleCombined}>Yuklanmoqda...</Text>
        </View>
      );
    }

    if (icon && iconPosition === 'left') {
      return (
        <View style={styles.buttonContent}>
          <Icon name={icon} size={16} color={variant === 'primary' ? 'white' : COLORS.primary} style={styles.buttonIcon} />
          <Text style={textStyleCombined}>{children}</Text>
        </View>
      );
    }

    if (icon && iconPosition === 'right') {
      return (
        <View style={styles.buttonContent}>
          <Text style={textStyleCombined}>{children}</Text>
          <Icon name={icon} size={16} color={variant === 'primary' ? 'white' : COLORS.primary} style={styles.buttonIcon} />
        </View>
      );
    }

    return (
      <Text style={textStyleCombined}>{children}</Text>
    );
  };

  return (
    <TouchableOpacity 
      onPress={onPress} 
      disabled={disabled || loading} 
      style={buttonStyle} 
      activeOpacity={0.8}
    >
      {renderContent()}
    </TouchableOpacity>
  );
};

// Input komponenti
export const Input = ({
  value,
  onChangeText,
  placeholder,
  style,
  inputStyle,
  label,
  error,
  icon,
  iconPosition = 'left',
  secureTextEntry = false,
  keyboardType = 'default',
  multiline = false,
  numberOfLines = 1,
  maxLength,
  editable = true,
  onFocus,
  onBlur,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const inputContainerStyle = [
    styles.inputContainer,
    isFocused && styles.inputContainer_focused,
    error && styles.inputContainer_error,
    style,
  ];

  const inputTextStyle = [
    styles.input,
    styles[`input_${icon ? 'with_icon' : 'without_icon'}`],
    inputStyle,
  ];

  const renderIcon = () => {
    if (icon) {
      return (
        <Icon 
          name={icon} 
          size={20} 
          color={error ? COLORS.danger : isFocused ? COLORS.primary : COLORS.gray[500]}
          style={[
            styles.inputIcon,
            iconPosition === 'right' && styles.inputIcon_right
          ]}
        />
      );
    }
    return null;
  };

  return (
    <View style={inputContainerStyle}>
      {label && <Text style={styles.inputLabel}>{label}</Text>}
      
      <View style={styles.inputWrapper}>
        {iconPosition === 'left' && renderIcon()}
        
        <TextInput
          style={inputTextStyle}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={COLORS.gray[400]}
          secureTextEntry={secureTextEntry}
          keyboardType={keyboardType}
          multiline={multiline}
          numberOfLines={numberOfLines}
          maxLength={maxLength}
          editable={editable}
          onFocus={() => {
            setIsFocused(true);
            onFocus && onFocus();
          }}
          onBlur={() => {
            setIsFocused(false);
            onBlur && onBlur();
          }}
        />
        
        {iconPosition === 'right' && renderIcon()}
      </View>
      
      {error && <Text style={styles.inputError}>{error}</Text>}
    </View>
  );
};

// Modal komponenti
export const ModalComponent = ({
  visible,
  onClose,
  title,
  children,
  style,
  animationType = 'slide',
  transparent = true,
  fullScreen = false,
}) => {
  const modalStyle = [
    styles.modal,
    transparent && styles.modal_transparent,
    fullScreen && styles.modal_fullScreen,
    style,
  ];

  return (
    <Modal
      visible={visible}
      animationType={animationType}
      transparent={transparent}
      onRequestClose={onClose}
    >
      <View style={modalStyle}>
        <View style={styles.modalContent}>
          {title && (
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{title}</Text>
              <TouchableOpacity onPress={onClose} style={styles.modalCloseButton}>
                <Icon name="close" size={24} color={COLORS.gray[600]} />
              </TouchableOpacity>
            </View>
          )}
          <ScrollView style={styles.modalBody}>
            {children}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

// Loader komponenti
export const Loader = ({
  size = 'medium',
  color = COLORS.primary,
  text,
  overlay = false,
}) => {
  const loaderStyle = [
    styles.loader,
    styles[`loader_${size}`],
    overlay && styles.loader_overlay,
  ];

  return (
    <View style={loaderStyle}>
      <Icon 
        name="refresh" 
        size={size === 'small' ? 16 : size === 'large' ? 32 : 24} 
        color={color} 
        style={styles.loaderIcon}
      />
      {text && <Text style={[styles.loaderText, { color }]}>{text}</Text>}
    </View>
  );
};

// List komponenti
export const List = ({
  data,
  renderItem,
  keyExtractor,
  style,
  ItemSeparatorComponent,
  ListEmptyComponent,
  refreshing,
  onRefresh,
  scrollEnabled = true,
  horizontal = false,
  numColumns = 1,
}) => {
  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      style={[styles.list, style]}
      ItemSeparatorComponent={ItemSeparatorComponent}
      ListEmptyComponent={ListEmptyComponent}
      refreshing={refreshing}
      onRefresh={onRefresh}
      scrollEnabled={scrollEnabled}
      horizontal={horizontal}
      numColumns={numColumns}
      showsVerticalScrollIndicator={false}
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.listContent}
    />
  );
};

// List item komponenti
export const ListItem = ({
  title,
  subtitle,
  onPress,
  leftIcon,
  rightIcon,
  rightComponent,
  style,
  titleStyle,
  subtitleStyle,
  avatar,
  badge,
  switch: SwitchComponent,
  chevron = false,
  disabled = false,
}) => {
  const itemStyle = [
    styles.listItem,
    disabled && styles.listItem_disabled,
    style,
  ];

  return (
    <TouchableOpacity 
      onPress={onPress} 
      disabled={disabled || !onPress}
      style={itemStyle}
      activeOpacity={0.7}
    >
      {leftIcon && (
        <View style={styles.listItemLeft}>
          {typeof leftIcon === 'string' ? (
            <Icon name={leftIcon} size={24} color={COLORS.gray[600]} />
          ) : (
            leftIcon
          )}
          {badge && <View style={styles.badge}>{badge}</View>}
        </View>
      )}
      
      {avatar && <View style={styles.listItemAvatar}>{avatar}</View>}
      
      <View style={styles.listItemContent}>
        {title && <Text style={[styles.listItemTitle, titleStyle]}>{title}</Text>}
        {subtitle && <Text style={[styles.listItemSubtitle, subtitleStyle]}>{subtitle}</Text>}
      </View>
      
      {rightComponent && <View style={styles.listItemRight}>{rightComponent}</View>}
      
      {rightIcon && (
        <View style={styles.listItemRight}>
          {typeof rightIcon === 'string' ? (
            <Icon name={rightIcon} size={24} color={COLORS.gray[400]} />
          ) : (
            rightIcon
          )}
        </View>
      )}
      
      {SwitchComponent && <View style={styles.listItemRight}>{SwitchComponent}</View>}
      
      {chevron && (
        <View style={styles.listItemRight}>
          <Icon name="chevron-forward" size={20} color={COLORS.gray[400]} />
        </View>
      )}
    </TouchableOpacity>
  );
};

// Header komponenti
export const Header = ({
  title,
  leftIcon,
  rightIcon,
  onLeftPress,
  onRightPress,
  style,
  titleStyle,
  transparent = false,
  gradient = false,
  colors = [COLORS.primary, COLORS.secondary],
  centerComponent,
  rightComponent,
}) => {
  const headerStyle = [
    styles.header,
    transparent && styles.header_transparent,
    gradient && { backgroundColor: 'transparent' },
    style,
  ];

  const renderLeft = () => {
    if (leftIcon) {
      return (
        <TouchableOpacity onPress={onLeftPress} style={styles.headerLeft}>
          {typeof leftIcon === 'string' ? (
            <Icon name={leftIcon} size={24} color="white" />
          ) : (
            leftIcon
          )}
        </TouchableOpacity>
      );
    }
    return <View style={styles.headerLeft} />;
  };

  const renderCenter = () => {
    if (centerComponent) return centerComponent;
    
    return (
      <Text style={[styles.headerTitle, titleStyle]}>
        {title}
      </Text>
    );
  };

  const renderRight = () => {
    if (rightComponent) return rightComponent;
    
    if (rightIcon) {
      return (
        <TouchableOpacity onPress={onRightPress} style={styles.headerRight}>
          {typeof rightIcon === 'string' ? (
            <Icon name={rightIcon} size={24} color="white" />
          ) : (
            rightIcon
          )}
        </TouchableOpacity>
      );
    }
    return <View style={styles.headerRight} />;
  };

  return (
    <View style={headerStyle}>
      {gradient ? (
        <LinearGradient colors={colors} style={styles.headerGradient}>
          {renderLeft()}
          {renderCenter()}
          {renderRight()}
        </LinearGradient>
      ) : (
        <>
          {renderLeft()}
          {renderCenter()}
          {renderRight()}
        </>
      )}
    </View>
  );
};

// Tab bar komponenti
export const TabBar = ({
  tabs,
  activeTab,
  onTabPress,
  style,
  activeColor = COLORS.primary,
  inactiveColor = COLORS.gray[500],
}) => {
  return (
    <View style={[styles.tabBar, style]}>
      {tabs.map((tab, index) => (
        <TouchableOpacity
          key={index}
          style={styles.tabBarItem}
          onPress={() => onTabPress(index)}
          activeOpacity={0.7}
        >
          <Icon
            name={activeTab === index ? tab.activeIcon : tab.icon}
            size={24}
            color={activeTab === index ? activeColor : inactiveColor}
          />
          {tab.label && (
            <Text
              style={[
                styles.tabBarLabel,
                { color: activeTab === index ? activeColor : inactiveColor }
              ]}
            >
              {tab.label}
            </Text>
          )}
        </TouchableOpacity>
      ))}
    </View>
  );
};

// Floating Action Button
export const FAB = ({
  onPress,
  icon,
  style,
  size = 'medium', // small, medium, large
  color = COLORS.primary,
  position = 'bottom-right', // bottom-right, bottom-left, top-right, top-left
}) => {
  const fabStyle = [
    styles.fab,
    styles[`fab_${size}`],
    styles[`fab_${position}`],
    { backgroundColor: color },
    style,
  ];

  return (
    <TouchableOpacity onPress={onPress} style={fabStyle} activeOpacity={0.8}>
      <Icon name={icon} size={size === 'small' ? 16 : size === 'large' ? 28 : 20} color="white" />
    </TouchableOpacity>
  );
};

// Avatar komponenti
export const Avatar = ({
  source,
  size = 'medium', // small, medium, large
  style,
  children,
  rounded = true,
  backgroundColor = COLORS.gray[200],
  borderColor,
  borderWidth = 0,
}) => {
  const avatarSize = size === 'small' ? 32 : size === 'large' ? 80 : 48;
  
  const avatarStyle = [
    styles.avatar,
    {
      width: avatarSize,
      height: avatarSize,
      borderRadius: rounded ? avatarSize / 2 : 8,
      backgroundColor,
      borderColor,
      borderWidth,
    },
    style,
  ];

  if (source) {
    return (
      <View style={avatarStyle}>
        <Image source={{ uri: source }} style={[styles.avatarImage, { borderRadius: rounded ? avatarSize / 2 : 8 }]} />
        {children}
      </View>
    );
  }

  return (
    <View style={avatarStyle}>
      {children}
    </View>
  );
};

// Progress bar komponenti
export const ProgressBar = ({
  progress = 0,
  style,
  barStyle,
  fillStyle,
  showPercentage = false,
  color = COLORS.primary,
  backgroundColor = COLORS.gray[200],
  height = 8,
}) => {
  const progressStyle = [
    styles.progressBar,
    { height, backgroundColor },
    barStyle,
  ];

  const fillStyleCombined = [
    styles.progressBarFill,
    {
      width: `${Math.min(Math.max(progress, 0), 1) * 100}%`,
      backgroundColor: color,
    },
    fillStyle,
  ];

  return (
    <View style={style}>
      <View style={progressStyle}>
        <View style={fillStyleCombined} />
      </View>
      {showPercentage && (
        <Text style={styles.progressBarText}>
          {Math.round(progress * 100)}%
        </Text>
      )}
    </View>
  );
};

// Badge komponenti
export const Badge = ({
  children,
  variant = 'primary', // primary, secondary, success, danger, warning, info
  size = 'medium', // small, medium, large
  style,
  textStyle,
}) => {
  const badgeStyle = [
    styles.badge,
    styles[`badge_${variant}`],
    styles[`badge_${size}`],
    style,
  ];

  const textStyleCombined = [
    styles[`badge_text_${size}`],
    textStyle,
  ];

  return (
    <View style={badgeStyle}>
      <Text style={textStyleCombined}>{children}</Text>
    </View>
  );
};

// Skeleton loader komponenti
export const SkeletonLoader = ({ 
  width = '100%', 
  height = 20, 
  style, 
  borderRadius = 4,
  colors = [COLORS.gray[200], COLORS.gray[100], COLORS.gray[200]]
}) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.timing(animatedValue, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: false,
      })
    );
    animation.start();
    return () => animation.stop();
  }, []);

  const translateX = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [-100, 100],
  });

  return (
    <View style={[styles.skeletonContainer, { height }, style]}>
      <Animated.View
        style={[
          styles.skeleton,
          {
            width,
            height,
            borderRadius,
            backgroundColor: colors[0],
            transform: [{ translateX }],
          },
        ]}
      />
    </View>
  );
};

// Toast komponenti
export const Toast = ({
  visible,
  message,
  type = 'info', // success, error, warning, info
  duration = 3000,
  onHide,
}) => {
  const translateY = useRef(new Animated.Value(100)).current;

  useEffect(() => {
    if (visible) {
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
      }).start();

      const timer = setTimeout(() => {
        hideToast();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [visible, duration]);

  const hideToast = () => {
    Animated.timing(translateY, {
      toValue: 100,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      onHide && onHide();
    });
  };

  if (!visible) return null;

  const toastStyle = [
    styles.toast,
    styles[`toast_${type}`],
    {
      transform: [{ translateY }],
    },
  ];

  const iconName = {
    success: 'checkmark-circle',
    error: 'alert-circle',
    warning: 'warning',
    info: 'information-circle',
  }[type];

  return (
    <View style={styles.toastContainer}>
      <Animated.View style={toastStyle}>
        <Icon name={iconName} size={20} color="white" />
        <Text style={styles.toastText}>{message}</Text>
        <TouchableOpacity onPress={hideToast}>
          <Icon name="close" size={16} color="white" />
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
};

// Uslub
const styles = StyleSheet.create({
  // Card styles
  card: {
    backgroundColor: COLORS.white,
    borderRadius: normalize(12),
    padding: normalize(16),
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },

  // Button styles
  button: {
    borderRadius: normalize(8),
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
  },
  button_primary: {
    backgroundColor: COLORS.primary,
  },
  button_secondary: {
    backgroundColor: COLORS.gray[100],
  },
  button_outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  button_ghost: {
    backgroundColor: 'transparent',
  },
  button_small: {
    height: normalize(32),
    paddingHorizontal: normalize(12),
  },
  button_medium: {
    height: normalize(44),
    paddingHorizontal: normalize(16),
  },
  button_large: {
    height: normalize(52),
    paddingHorizontal: normalize(20),
  },
  button_disabled: {
    backgroundColor: COLORS.gray[300],
  },
  button_loading: {
    opacity: 0.8,
  },
  button_fullWidth: {
    width: '100%',
  },
  button_content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  buttonIcon: {
    marginRight: normalize(8),
  },
  button_text_primary: {
    color: COLORS.white,
    fontWeight: '600',
  },
  button_text_secondary: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  button_text_outline: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  button_text_ghost: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  button_text_small: {
    fontSize: normalize(12),
  },
  button_text_medium: {
    fontSize: normalize(14),
  },
  button_text_large: {
    fontSize: normalize(16),
  },
  button_text_disabled: {
    color: COLORS.gray[500],
  },

  // Input styles
  inputContainer: {
    marginBottom: normalize(16),
  },
  inputContainer_focused: {
    borderColor: COLORS.primary,
  },
  inputContainer_error: {
    borderColor: COLORS.danger,
  },
  inputLabel: {
    fontSize: normalize(14),
    fontWeight: '600',
    color: COLORS.gray[700],
    marginBottom: normalize(6),
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.gray[300],
    borderRadius: normalize(8),
    backgroundColor: COLORS.white,
  },
  input: {
    flex: 1,
    height: normalize(44),
    paddingHorizontal: normalize(12),
    fontSize: normalize(14),
    color: COLORS.gray[900],
  },
  input_with_icon: {
    paddingLeft: 0,
  },
  input_without_icon: {
    paddingHorizontal: normalize(12),
  },
  inputIcon: {
    paddingLeft: normalize(12),
  },
  inputIcon_right: {
    paddingRight: normalize(12),
    paddingLeft: 0,
  },
  inputError: {
    fontSize: normalize(12),
    color: COLORS.danger,
    marginTop: normalize(4),
  },

  // Modal styles
  modal: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modal_transparent: {
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modal_fullScreen: {
    width: width,
    height: height,
  },
  modalContent: {
    backgroundColor: COLORS.white,
    borderRadius: normalize(12),
    width: width * 0.9,
    maxHeight: height * 0.8,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: normalize(16),
    borderBottomWidth: 1,
    borderBottomColor: COLORS.gray[200],
  },
  modalTitle: {
    fontSize: normalize(18),
    fontWeight: 'bold',
    color: COLORS.gray[900],
  },
  modalCloseButton: {
    padding: normalize(4),
  },
  modalBody: {
    padding: normalize(16),
    maxHeight: height * 0.6,
  },

  // Loader styles
  loader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loader_small: {
    padding: normalize(8),
  },
  loader_medium: {
    padding: normalize(16),
  },
  loader_large: {
    padding: normalize(24),
  },
  loader_overlay: {
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 999,
  },
  loaderIcon: {
    marginRight: normalize(8),
  },
  loaderText: {
    fontSize: normalize(14),
    marginLeft: normalize(8),
  },

  // List styles
  list: {
    flex: 1,
  },
  listContent: {
    paddingVertical: normalize(8),
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: normalize(16),
    paddingVertical: normalize(12),
    backgroundColor: COLORS.white,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.gray[100],
  },
  listItem_disabled: {
    opacity: 0.6,
  },
  listItemLeft: {
    marginRight: normalize(12),
    position: 'relative',
  },
  listItemAvatar: {
    marginRight: normalize(12),
  },
  listItemContent: {
    flex: 1,
  },
  listItemTitle: {
    fontSize: normalize(16),
    fontWeight: '500',
    color: COLORS.gray[900],
  },
  listItemSubtitle: {
    fontSize: normalize(14),
    color: COLORS.gray[600],
    marginTop: normalize(2),
  },
  listItemRight: {
    marginLeft: normalize(12),
  },

  // Header styles
  header: {
    height: normalize(60),
    backgroundColor: COLORS.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: normalize(16),
  },
  header_transparent: {
    backgroundColor: 'transparent',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
  },
  headerGradient: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: normalize(16),
  },
  headerLeft: {
    width: normalize(40),
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: normalize(18),
    fontWeight: 'bold',
    color: COLORS.white,
    textAlign: 'center',
  },
  headerRight: {
    width: normalize(40),
    alignItems: 'flex-end',
  },

  // Tab bar styles
  tabBar: {
    flexDirection: 'row',
    backgroundColor: COLORS.white,
    borderTopWidth: 1,
    borderTopColor: COLORS.gray[200],
    paddingBottom: Platform.OS === 'ios' ? normalize(20) : normalize(8),
    height: Platform.OS === 'ios' ? normalize(80) : normalize(60),
  },
  tabBarItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: normalize(8),
  },
  tabBarLabel: {
    fontSize: normalize(12),
    marginTop: normalize(2),
  },

  // FAB styles
  fab: {
    position: 'absolute',
    borderRadius: normalize(28),
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  fab_small: {
    width: normalize(40),
    height: normalize(40),
  },
  fab_medium: {
    width: normalize(56),
    height: normalize(56),
  },
  fab_large: {
    width: normalize(64),
    height: normalize(64),
  },
  fab_bottom_right: {
    bottom: normalize(16),
    right: normalize(16),
  },
  fab_bottom_left: {
    bottom: normalize(16),
    left: normalize(16),
  },
  fab_top_right: {
    top: normalize(80),
    right: normalize(16),
  },
  fab_top_left: {
    top: normalize(80),
    left: normalize(16),
  },

  // Avatar styles
  avatar: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarImage: {
    width: '100%',
    height: '100%',
  },

  // Progress bar styles
  progressBar: {
    width: '100%',
    borderRadius: normalize(4),
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: normalize(4),
  },
  progressBarText: {
    fontSize: normalize(12),
    color: COLORS.gray[600],
    marginTop: normalize(4),
    textAlign: 'right',
  },

  // Badge styles
  badge: {
    borderRadius: normalize(12),
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge_primary: {
    backgroundColor: COLORS.primary,
  },
  badge_secondary: {
    backgroundColor: COLORS.gray[100],
  },
  badge_success: {
    backgroundColor: COLORS.success,
  },
  badge_danger: {
    backgroundColor: COLORS.danger,
  },
  badge_warning: {
    backgroundColor: COLORS.warning,
  },
  badge_info: {
    backgroundColor: COLORS.info,
  },
  badge_small: {
    paddingHorizontal: normalize(6),
    paddingVertical: normalize(2),
    minWidth: normalize(16),
    height: normalize(16),
  },
  badge_medium: {
    paddingHorizontal: normalize(8),
    paddingVertical: normalize(4),
    minWidth: normalize(20),
    height: normalize(20),
  },
  badge_large: {
    paddingHorizontal: normalize(12),
    paddingVertical: normalize(6),
    minWidth: normalize(24),
    height: normalize(24),
  },
  badge_text_small: {
    fontSize: normalize(10),
    color: COLORS.white,
  },
  badge_text_medium: {
    fontSize: normalize(12),
    color: COLORS.white,
  },
  badge_text_large: {
    fontSize: normalize(14),
    color: COLORS.white,
  },

  // Skeleton styles
  skeletonContainer: {
    overflow: 'hidden',
    backgroundColor: COLORS.gray[200],
  },
  skeleton: {
    backgroundColor: COLORS.gray[200],
  },

  // Toast styles
  toastContainer: {
    position: 'absolute',
    bottom: normalize(20),
    left: normalize(16),
    right: normalize(16),
    zIndex: 9999,
  },
  toast: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: normalize(16),
    paddingVertical: normalize(12),
    borderRadius: normalize(8),
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  toast_success: {
    backgroundColor: COLORS.success,
  },
  toast_error: {
    backgroundColor: COLORS.danger,
  },
  toast_warning: {
    backgroundColor: COLORS.warning,
  },
  toast_info: {
    backgroundColor: COLORS.info,
  },
  toastText: {
    flex: 1,
    color: COLORS.white,
    fontSize: normalize(14),
    marginLeft: normalize(8),
    marginRight: normalize(8),
  },
});

export default {
  Card,
  Button,
  Input,
  ModalComponent,
  Loader,
  List,
  ListItem,
  Header,
  TabBar,
  FAB,
  Avatar,
  ProgressBar,
  Badge,
  SkeletonLoader,
  Toast,
  COLORS,
};