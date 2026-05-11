# 负向约束

## 默认负向约束

所有 UI Prompt 必须包含以下负向约束：

```text
not dribbble
not concept art
not futuristic
not 3D UI
not abstract
not artistic poster
not liquid glass
not sci-fi
not distorted layout
```

## 工程限制

```text
avoid impossible shadows
avoid irregular layout
avoid over-designed effects
avoid complex gradients
avoid decorative-only elements
avoid non-functional animations
```

## 风格排除

### 艺术形式

- not illustration
- not hand-drawn
- not sketch
- not painting
- not watercolor

### 过度设计

- not over-designed
- not too many colors
- not cluttered
- not chaotic
- not messy

### 不可实现

- not impossible physics
- not floating elements without reason
- not broken perspective
- not unrealistic proportions

## 平台特定排除

### 移动端

```text
not desktop-only layout
not hover-dependent
not tiny touch targets
not horizontal scroll
```

### 桌面端

```text
not mobile-only layout
not oversized elements
not touch-only gestures
not phone mockup
```
