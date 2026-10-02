# Platforms: web, iOS, Android, Flutter, desktop, and beyond

Rule of thumb: **Persuade surfaces** (landing pages, store pages, marketing) carry the bold direction.
**Operate surfaces** (the app itself) follow platform conventions and carry the brand in details: color,
display type, iconography, illustration, empty states, motion character, sound and haptics.
Tokens live once in DESIGN.md and are emitted per platform (systems-and-handoff.md).

## Contents
Web · iOS / iPadOS · Android · Flutter · Desktop · CLI/TUI · Games · Email · Store presence

## Web
- Fluid type with `clamp()`, container queries for components, `text-wrap: balance` on headings, `pretty` on paragraphs.
- Tailwind v4: tokens in `@theme`; shadcn/ui only when re-themed from tokens (never the stock look).
- Dark mode by design (scene-driven), not inversion; `color-scheme` set; focus-visible rings in brand color.
- Performance: LCP image preloaded, fonts subset + `font-display: swap`, JS for motion loaded after content.
- Browser surfaces count: `::selection`, caret color, scrollbars, favicon set, OG image, 404 page.

## iOS / iPadOS (iOS 27, released Sept 2026)
- **Liquid Glass is the system material.** Apps built with Xcode 27 can no longer opt native components out of it.
  iOS 27 refined it (more defined borders, a lighter look in dark mode) and added a system setting that lets users
  choose how transparent or tinted it appears. Design must hold up across that range.
- Glass belongs to the **control/navigation layer** floating above content (tab bars, toolbars, sheets, buttons).
  Do not put custom glass on content cards or long text. Keep content legible underneath; test with Reduce
  Transparency and Increase Contrast.
- Use system components first; brand through accent color, a display face for large titles, SF Symbols in matching
  weights, illustrations in empty states and onboarding, and haptics (`sensoryFeedback`).
- Dynamic Type for all text; minimum 44×44pt targets; safe areas; respect Dark Mode and tinted/clear icon variants.
- App icon: layered icon (Icon Composer) with light, dark, tinted and clear variants; test at small sizes.
- Motion: SwiftUI springs by default, `PhaseAnimator`, `KeyframeAnimator`, `matchedGeometryEffect`,
  `symbolEffect`; honor `accessibilityReduceMotion`.
- UIScene lifecycle is required when building with the iOS 27 SDK (relevant for Flutter and older apps).

## Android
- Material 3 with the **Expressive** update: richer shape morphing, spring-based motion physics, emphasized type.
- Decide **dynamic color** (Material You, wallpaper-derived) vs **brand color**; many brands use brand color for key
  surfaces and allow dynamic color elsewhere. Write the decision in DESIGN.md.
- Compose theming: custom `ColorScheme`, `Typography`, `Shapes` from tokens (never the template Purple40/80).
- Edge-to-edge is the default on recent Android versions: handle insets; predictive back animations.
- 48×48dp targets; adaptive icons with a monochrome layer for themed icons.

## Flutter
- `ThemeData(useMaterial3: true, colorScheme: ColorScheme(...from tokens...))`, never the starter `deepPurple` seed.
  Custom tokens through `ThemeExtension`.
- Platform-adaptive: `.adaptive` constructors, Cupertino widgets where iOS users expect them. Flutter's Cupertino
  library is still catching up with Liquid Glass; community packages emulate it. Decide per project whether to
  emulate glass on iOS, and keep it on the control layer if you do.
- Flutter 3.41+ auto-migrates unmodified AppDelegates to UIScene for iOS 27; custom AppDelegates need manual work.
- Motion: implicit `Animated*` widgets for state, explicit `AnimationController` for choreography,
  `flutter_animate` for sequences, `Hero` for shared elements, Rive/Lottie packages for characters,
  fragment shaders (`FragmentProgram`) for generative effects. Check `MediaQuery.disableAnimations`.
- Bundle fonts locally for production (not runtime `google_fonts` fetching).

## Desktop
- **macOS**: sidebars and toolbars use the system materials (Liquid Glass on macOS 27), menu bar with full
  commands and shortcuts, window chrome conventions, higher density, keyboard-first, Settings window.
- **Windows 11**: Fluent 2, Mica/Acrylic materials, Segoe UI Variable, title bar integration, snap layouts.
- **Linux**: follow GTK/libadwaita or KDE conventions per target.
- **Electron/Tauri**: avoid the "website in a window": native or custom drag-region title bar, real menus,
  context menus, shortcuts, system font option, dense layouts, OS dark mode and accent color, no marketing hero inside the app.

## CLI / TUI (developer tools)
- Color is a highlight, not a theme: 16-color-safe palette, respect `NO_COLOR`, readable on light and dark terminals.
- Hierarchy with bold/dim and spacing; tables aligned; progress bars/spinners for anything > 1s.
- Errors: what happened, why, the exact fix command. Help text with examples first.

## Games
- HUD readability over decoration; integer scaling for pixel art; nine-slice UI panels; controller and keyboard focus.
- "Juice" (screen shake, hit-stop, particles) budgeted and toggleable; accessibility options (reduce flashing, remap, text size).

## Email
- ~600px single column, table-based layout, live text (not images of text), bulletproof buttons,
  dark-mode-safe logos, alt text, plain-text part.

## Store presence (verify current specs before export)
- App Store: first 2-3 screenshots sell; real UI + a short benefit caption; sizes per current device classes;
  optional 15-30s app preview (video-remotion.md).
- Google Play: 1024×500 feature graphic, 512×512 icon, phone/tablet screenshots, optional promo video.
- Render store assets from HTML templates + `capture.py` so they stay consistent and editable.
