# AI Trading Platform - Modern Design System 2025

## 1. COLOR PALETTE

### Dark Theme (Default)
```css
/* Primary Colors */
--primary-50: #e6f2ff
--primary-100: #bae0ff
--primary-200: #8dceff
--primary-300: #61bcff
--primary-400: #34aaff
--primary-500: #0898ff  /* Main Brand */
--primary-600: #0679cc
--primary-700: #055a99
--primary-800: #033b66
--primary-900: #021c33

/* Accent Colors */
--accent-cyan: #00d4ff
--accent-purple: #a855f7
--accent-pink: #ec4899
--accent-green: #10b981
--accent-orange: #f97316

/* Neutral Colors */
--neutral-50: #f8fafc
--neutral-100: #f1f5f9
--neutral-200: #e2e8f0
--neutral-300: #cbd5e1
--neutral-400: #94a3b8
--neutral-500: #64748b
--neutral-600: #475569
--neutral-700: #334155
--neutral-800: #1e293b
--neutral-900: #0f172a
--neutral-950: #020617

/* Background */
--bg-primary: #0a0e1a
--bg-secondary: #111827
--bg-tertiary: #1e293b
--bg-glass: rgba(15, 23, 42, 0.7)

/* Text */
--text-primary: #f1f5f9
--text-secondary: #cbd5e1
--text-tertiary: #94a3b8
```

### Light Theme
```css
/* Background */
--bg-primary-light: #ffffff
--bg-secondary-light: #f8fafc
--bg-tertiary-light: #f1f5f9
--bg-glass-light: rgba(255, 255, 255, 0.7)

/* Text */
--text-primary-light: #0f172a
--text-secondary-light: #334155
--text-tertiary-light: #64748b
```

## 2. TYPOGRAPHY

### Font Families
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-display: 'Cal Sans', 'Inter', sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', monospace
```

### Font Sizes
```css
--text-xs: 0.75rem     /* 12px */
--text-sm: 0.875rem    /* 14px */
--text-base: 1rem      /* 16px */
--text-lg: 1.125rem    /* 18px */
--text-xl: 1.25rem     /* 20px */
--text-2xl: 1.5rem     /* 24px */
--text-3xl: 1.875rem   /* 30px */
--text-4xl: 2.25rem    /* 36px */
--text-5xl: 3rem       /* 48px */
--text-6xl: 3.75rem    /* 60px */
```

### Font Weights
```css
--font-light: 300
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
--font-extrabold: 800
```

## 3. SPACING SYSTEM

```css
--space-1: 0.25rem    /* 4px */
--space-2: 0.5rem     /* 8px */
--space-3: 0.75rem    /* 12px */
--space-4: 1rem       /* 16px */
--space-5: 1.25rem    /* 20px */
--space-6: 1.5rem     /* 24px */
--space-8: 2rem       /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
```

## 4. BORDER RADIUS

```css
--radius-sm: 0.375rem   /* 6px */
--radius-md: 0.5rem     /* 8px */
--radius-lg: 0.75rem    /* 12px */
--radius-xl: 1rem       /* 16px */
--radius-2xl: 1.5rem    /* 24px */
--radius-3xl: 2rem      /* 32px */
--radius-full: 9999px
```

## 5. SHADOWS

```css
/* Elevation Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25)

/* Colored Shadows */
--shadow-primary: 0 10px 40px -10px rgba(8, 152, 255, 0.3)
--shadow-success: 0 10px 40px -10px rgba(16, 185, 129, 0.3)
--shadow-danger: 0 10px 40px -10px rgba(239, 68, 68, 0.3)
--shadow-warning: 0 10px 40px -10px rgba(249, 115, 22, 0.3)

/* Glassmorphism */
--shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.37)
```

## 6. GRADIENTS

```css
/* Brand Gradients */
--gradient-primary: linear-gradient(135deg, #0898ff 0%, #00d4ff 100%)
--gradient-success: linear-gradient(135deg, #10b981 0%, #34d399 100%)
--gradient-danger: linear-gradient(135deg, #ef4444 0%, #f87171 100%)
--gradient-warning: linear-gradient(135deg, #f97316 0%, #fb923c 100%)
--gradient-purple: linear-gradient(135deg, #a855f7 0%, #c084fc 100%)

/* Special Gradients */
--gradient-rainbow: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)
--gradient-ocean: linear-gradient(135deg, #667eea 0%, #0898ff 100%)
--gradient-sunset: linear-gradient(135deg, #f97316 0%, #ec4899 100%)
--gradient-forest: linear-gradient(135deg, #10b981 0%, #34d399 100%)

/* Glass Effect */
--gradient-glass-dark: linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.5) 100%)
--gradient-glass-light: linear-gradient(135deg, rgba(255, 255, 255, 0.7) 0%, rgba(248, 250, 252, 0.5) 100%)
```

## 7. ANIMATIONS

### Keyframes
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(8, 152, 255, 0.5); }
  50% { box-shadow: 0 0 40px rgba(8, 152, 255, 0.8); }
}
```

### Transition Durations
```css
--duration-fast: 150ms
--duration-normal: 300ms
--duration-slow: 500ms
--duration-slower: 700ms
```

### Easing Functions
```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
--ease-out: cubic-bezier(0, 0, 0.2, 1)
--ease-in: cubic-bezier(0.4, 0, 1, 1)
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)
```

## 8. GLASSMORPHISM EFFECTS

```css
.glass-card {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.125);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

.glass-card-light {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(209, 213, 219, 0.3);
  box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.1);
}
```

## 9. NEUMORPHISM EFFECTS

```css
.neumorphism-dark {
  background: #1e293b;
  box-shadow: 
    20px 20px 60px #0f172a,
    -20px -20px 60px #2d3a4c;
}

.neumorphism-light {
  background: #f1f5f9;
  box-shadow: 
    20px 20px 60px #cbd5e1,
    -20px -20px 60px #ffffff;
}

.neumorphism-inset {
  background: #1e293b;
  box-shadow: 
    inset 20px 20px 60px #0f172a,
    inset -20px -20px 60px #2d3a4c;
}
```

## 10. COMPONENT PATTERNS

### Card
```css
.modern-card {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 10px 40px -10px rgba(8, 152, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modern-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 60px -10px rgba(8, 152, 255, 0.4);
  border-color: rgba(8, 152, 255, 0.3);
}
```

### Button
```css
.modern-button {
  background: linear-gradient(135deg, #0898ff 0%, #00d4ff 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  box-shadow: 0 10px 40px -10px rgba(8, 152, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  position: relative;
  overflow: hidden;
}

.modern-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.modern-button:hover::before {
  left: 100%;
}

.modern-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 50px -10px rgba(8, 152, 255, 0.7);
}
```

### Input
```css
.modern-input {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  color: #f1f5f9;
  transition: all 0.3s;
}

.modern-input:focus {
  outline: none;
  border-color: #0898ff;
  box-shadow: 0 0 0 4px rgba(8, 152, 255, 0.1);
  background: rgba(15, 23, 42, 0.7);
}
```

## 11. BREAKPOINTS

```css
--breakpoint-sm: 640px
--breakpoint-md: 768px
--breakpoint-lg: 1024px
--breakpoint-xl: 1280px
--breakpoint-2xl: 1536px
```

## 12. Z-INDEX SCALE

```css
--z-dropdown: 1000
--z-sticky: 1020
--z-fixed: 1030
--z-modal-backdrop: 1040
--z-modal: 1050
--z-popover: 1060
--z-tooltip: 1070
```

## 13. GRID SYSTEM

```css
/* 12 Column Grid */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
}

.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}
```

## 14. ACCESSIBILITY

```css
/* Focus Styles */
:focus-visible {
  outline: 2px solid #0898ff;
  outline-offset: 2px;
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 15. DARK MODE TOGGLE

```css
/* Dark Mode Variables */
:root {
  --theme-bg: var(--bg-primary);
  --theme-text: var(--text-primary);
}

.light {
  --theme-bg: var(--bg-primary-light);
  --theme-text: var(--text-primary-light);
}
```
