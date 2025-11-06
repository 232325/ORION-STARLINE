import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // localStorage'dan oldingi tanlovni olish
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    
    // Agar saqlangan tema bo'lsa, uni ishlatish
    if (savedTheme) {
      return savedTheme;
    }
    
    // Aks holda, tizim sozlamalariga qarab aniqlash
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  });

  // Tema o'zgarganda DOM va localStorage'ni yangilash
  useEffect(() => {
    const root = document.documentElement;
    
    // Eski tema classini olib tashlash
    root.classList.remove('light', 'dark');
    
    // Yangi tema classini qo'shish
    root.classList.add(theme);
    
    // localStorage'da saqlash
    localStorage.setItem('theme', theme);
    
    // Meta theme-color'ni yangilash (mobile browsers uchun)
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute(
        'content',
        theme === 'dark' ? '#0a0e1a' : '#ffffff'
      );
    }
  }, [theme]);

  // Tizim sozlamalari o'zgarganda tinglovchi
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // Faqat foydalanuvchi o'zi tanlagan bo'lmasa, tizim sozlamalarini qo'llash
      const savedTheme = localStorage.getItem('theme');
      if (!savedTheme) {
        setThemeState(e.matches ? 'dark' : 'light');
      }
    };
    
    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, []);

  const toggleTheme = () => {
    setThemeState(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  const value: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
