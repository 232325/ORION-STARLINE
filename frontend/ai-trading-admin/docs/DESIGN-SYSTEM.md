# AI Trading Platform - Zamonaviy Dizayn Tizimi 2025

## Dizayn Falsafasi

### Asosiy Tamoyillar
- **Zamonaviylik**: 2025 yilgi eng so'nggi UI/UX trendlari
- **Professionallik**: Enterprise-darajadagi sifat va ishonchlilik
- **Foydalanuvchi Tajribasi**: Intuitiv va qulay interfeys
- **Performance**: Tez yuklanish va silliq animatsiyalar
- **Accessibility**: WCAG 2.1 AA standartlariga muvofiq

### Vizual Yo'nalish
- Modern glassmorphism va neumorphism elementlari
- Gradient va depth effektlari
- Micro-interactions va smooth transitions
- Dark/Light theme qo'llab-quvvatlash
- Data-driven interactive visualizations

---

## Rang Palitras

### Light Theme

#### Primary Colors
```css
--primary-50: #f0f9ff
--primary-100: #e0f2fe
--primary-200: #bae6fd
--primary-300: #7dd3fc
--primary-400: #38bdf8
--primary-500: #0ea5e9  /* Asosiy */
--primary-600: #0284c7
--primary-700: #0369a1
--primary-800: #075985
--primary-900: #0c4a6e
```

#### Success Colors (Trading Profit)
```css
--success-50: #f0fdf4
--success-100: #dcfce7
--success-200: #bbf7d0
--success-300: #86efac
--success-400: #4ade80
--success-500: #22c55e  /* Asosiy */
--success-600: #16a34a
--success-700: #15803d
--success-800: #166534
--success-900: #14532d
```

#### Danger Colors (Trading Loss)
```css
--danger-50: #fef2f2
--danger-100: #fee2e2
--danger-200: #fecaca
--danger-300: #fca5a5
--danger-400: #f87171
--danger-500: #ef4444  /* Asosiy */
--danger-600: #dc2626
--danger-700: #b91c1c
--danger-800: #991b1b
--danger-900: #7f1d1d
```

#### Neutral Colors
```css
--neutral-50: #fafafa
--neutral-100: #f4f4f5
--neutral-200: #e4e4e7
--neutral-300: #d4d4d8
--neutral-400: #a1a1aa
--neutral-500: #71717a
--neutral-600: #52525b
--neutral-700: #3f3f46
--neutral-800: #27272a
--neutral-900: #18181b
```

### Dark Theme

#### Background Colors
```css
--dark-bg-primary: #0a0e1a
--dark-bg-secondary: #131826
--dark-bg-tertiary: #1a2332
--dark-bg-elevated: #222b3d
```

#### Surface Colors
```css
--dark-surface-50: rgba(255, 255, 255, 0.05)
--dark-surface-100: rgba(255, 255, 255, 0.08)
--dark-surface-200: rgba(255, 255, 255, 0.12)
```

#### Text Colors
```css
--dark-text-primary: #f8fafc
--dark-text-secondary: #cbd5e1
--dark-text-tertiary: #94a3b8
--dark-text-disabled: #64748b
```

### Gradient Palitra
```css
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
--gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%)
--gradient-danger: linear-gradient(135deg, #ef4444 0%, #dc2626 100%)
--gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%)
--gradient-info: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)
--gradient-purple: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)
--gradient-blue: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)
```

---

## Tipografiya

### Font Oilasi
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace
--font-display: 'Plus Jakarta Sans', 'Inter', sans-serif
```

### Font O'lchamlari
```css
--text-xs: 0.75rem      /* 12px */
--text-sm: 0.875rem     /* 14px */
--text-base: 1rem       /* 16px */
--text-lg: 1.125rem     /* 18px */
--text-xl: 1.25rem      /* 20px */
--text-2xl: 1.5rem      /* 24px */
--text-3xl: 1.875rem    /* 30px */
--text-4xl: 2.25rem     /* 36px */
--text-5xl: 3rem        /* 48px */
--text-6xl: 3.75rem     /* 60px */
```

### Font Og'irliklari
```css
--font-light: 300
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
--font-extrabold: 800
```

### Line Heights
```css
--leading-tight: 1.25
--leading-normal: 1.5
--leading-relaxed: 1.75
```

---

## Spacing System

### Spacing Scale (Tailwind asosida)
```css
--spacing-0: 0px
--spacing-1: 0.25rem   /* 4px */
--spacing-2: 0.5rem    /* 8px */
--spacing-3: 0.75rem   /* 12px */
--spacing-4: 1rem      /* 16px */
--spacing-5: 1.25rem   /* 20px */
--spacing-6: 1.5rem    /* 24px */
--spacing-8: 2rem      /* 32px */
--spacing-10: 2.5rem   /* 40px */
--spacing-12: 3rem     /* 48px */
--spacing-16: 4rem     /* 64px */
--spacing-20: 5rem     /* 80px */
--spacing-24: 6rem     /* 96px */
```

---

## Border Radius

```css
--radius-none: 0px
--radius-sm: 0.375rem   /* 6px */
--radius-md: 0.5rem     /* 8px */
--radius-lg: 0.75rem    /* 12px */
--radius-xl: 1rem       /* 16px */
--radius-2xl: 1.5rem    /* 24px */
--radius-full: 9999px
```

---

## Soyalar (Shadows)

### Light Theme Shadows
```css
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25)
```

### Dark Theme Shadows
```css
--shadow-dark-sm: 0 2px 4px 0 rgba(0, 0, 0, 0.3)
--shadow-dark-md: 0 4px 8px 0 rgba(0, 0, 0, 0.4)
--shadow-dark-lg: 0 8px 16px 0 rgba(0, 0, 0, 0.5)
--shadow-dark-xl: 0 16px 32px 0 rgba(0, 0, 0, 0.6)
```

### Glassmorphism Shadow
```css
--shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.37)
```

---

## Animatsiyalar

### Timing Functions
```css
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1)
--ease-in: cubic-bezier(0.4, 0, 1, 1)
--ease-out: cubic-bezier(0, 0, 0.2, 1)
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)
```

### Duration
```css
--duration-fast: 150ms
--duration-normal: 250ms
--duration-slow: 350ms
--duration-slower: 500ms
```

### Keyframe Animations
- **fadeIn**: Opacity 0 → 1
- **slideUp**: Transform translateY(20px) → 0
- **slideDown**: Transform translateY(-20px) → 0
- **slideLeft**: Transform translateX(20px) → 0
- **slideRight**: Transform translateX(-20px) → 0
- **scaleIn**: Transform scale(0.95) → 1
- **pulse**: Opacity va scale animation
- **shimmer**: Loading skeleton animation

---

## Glassmorphism Effektlar

### Glass Card
```css
background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.2);
box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
```

### Glass Card Dark
```css
background: rgba(17, 25, 40, 0.75);
backdrop-filter: blur(16px) saturate(180%);
-webkit-backdrop-filter: blur(16px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.125);
```

---

## Komponent Spetsifikatsiyalari

### Button

#### Primary Button
- **Background**: Gradient primary
- **Padding**: 0.75rem 1.5rem
- **Border Radius**: --radius-lg
- **Font Weight**: --font-semibold
- **Hover**: Scale 1.02, brightness 110%
- **Active**: Scale 0.98
- **Transition**: --duration-normal --ease-smooth

#### Secondary Button
- **Background**: Transparent
- **Border**: 2px solid primary
- **Hover**: Background primary-50 (light) / primary-900 (dark)

#### Ghost Button
- **Background**: Transparent
- **Hover**: Background neutral-100 (light) / neutral-800 (dark)

### Card

#### Standard Card
- **Background**: White (light) / --dark-bg-secondary (dark)
- **Border Radius**: --radius-xl
- **Shadow**: --shadow-md
- **Padding**: 1.5rem
- **Border**: 1px solid neutral-200 (light) / transparent (dark)

#### Glass Card
- **Background**: Glassmorphism effect
- **Border Radius**: --radius-2xl
- **Shadow**: --shadow-glass
- **Padding**: 1.5rem

### Input

#### Text Input
- **Height**: 2.75rem (44px)
- **Padding**: 0.75rem 1rem
- **Border**: 1px solid neutral-300
- **Border Radius**: --radius-lg
- **Focus**: Ring 2px primary-500
- **Transition**: --duration-normal

### Badge

#### Sizes
- **Small**: text-xs, px-2, py-0.5
- **Medium**: text-sm, px-2.5, py-1
- **Large**: text-base, px-3, py-1.5

#### Variants
- **Success**: Green background
- **Danger**: Red background
- **Warning**: Yellow background
- **Info**: Blue background
- **Neutral**: Gray background

---

## Layout Patterns

### Container
- **Max Width**: 1400px
- **Padding**: 1rem (mobile), 2rem (desktop)
- **Margin**: 0 auto

### Grid System
- **Gap**: 1.5rem
- **Columns**: 12-column grid
- **Responsive**: Mobile-first approach

### Navigation
- **Height**: 4rem (64px)
- **Background**: Glass effect
- **Position**: Fixed top
- **Z-index**: 50

---

## Responsive Breakpoints

```css
--screen-sm: 640px
--screen-md: 768px
--screen-lg: 1024px
--screen-xl: 1280px
--screen-2xl: 1536px
```

---

## Accessibility

### Focus States
- **Outline**: 2px solid primary-500
- **Offset**: 2px
- **Border Radius**: Inherit from element

### Color Contrast
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text
- Minimum 3:1 for UI components

---

## Dark Mode Implementation

### Theme Switching
- Automatic system preference detection
- Manual toggle with persistence (localStorage)
- Smooth transition between themes

### CSS Variables Approach
```css
:root {
  /* Light theme variables */
}

.dark {
  /* Dark theme overrides */
}
```

---

## Micro-interactions

### Hover Effects
- Buttons: Scale 1.02, shadow increase
- Cards: Shadow increase, slight lift
- Links: Color change, underline animation

### Click/Tap Effects
- Scale 0.98 on active
- Ripple effect for buttons
- Haptic feedback (where supported)

### Loading States
- Skeleton screens
- Shimmer animations
- Progress indicators
- Spinner animations

---

## Voice UI Integration

### Voice Command Button
- **Position**: Fixed bottom-right
- **Size**: 3.5rem circle
- **Animation**: Pulse when listening
- **Colors**: Gradient primary

### Voice Feedback
- Visual waveform animation
- Status indicators (listening/processing/speaking)
- Transcription display

---

## AI Chatbot Widget

### Floating Button
- **Position**: Fixed bottom-right
- **Size**: 3.5rem circle
- **Offset**: 1.5rem from bottom and right
- **Animation**: Subtle bounce on page load

### Chat Window
- **Width**: 380px (desktop), 100% (mobile)
- **Height**: 600px (desktop), 100vh (mobile)
- **Position**: Fixed bottom-right
- **Animation**: Slide up from bottom
- **Background**: Glass effect

---

## Chart Specifications

### Color Scheme
- **Line Colors**: Primary palette
- **Positive**: Success green
- **Negative**: Danger red
- **Grid Lines**: Neutral-200 (light) / Neutral-700 (dark)

### Interactions
- Tooltip on hover
- Zoom capabilities
- Pan/drag for timeline
- Click for details

---

## Implementation Checklist

- [ ] ThemeContext yaratish
- [ ] CSS variables sozlash
- [ ] Tailwind config yangilash
- [ ] Base UI components yaratish
- [ ] Dark mode toggle
- [ ] Glassmorphism utilities
- [ ] Animation utilities
- [ ] Responsive utilities
- [ ] Accessibility features
- [ ] Loading states
- [ ] Voice UI components
- [ ] Chatbot widget
