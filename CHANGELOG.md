# Changelog

## [1.3.0] - 2026-08-01

### Added
- **Themes tab:** the palette now has two tabs, **Changelog** and **Themes** — Theme Manager moved into its own tab instead of living at the top of the palette.
- **Font controls:** choose a Font Family (sans-serif, serif, or monospace) and Base Font Size, per theme, from the Themes tab.
- **Full `style.css`-bundle import/export**, alongside the existing single-theme `.theme.json` import/export — share a complete set of themes (built-ins plus customs) in one file.

### Changed
- Redesigned palette header: title and version number now stack, with the theme dropdown moved to the top-right corner.
- Added a version footer at the bottom of the palette, visible on both tabs.

## [1.2.0] - 2026-07-31

### Added
- **Theme Manager:** the light/dark toggle is now a full Light/Dark/Sepia dropdown with `.theme.json` import/export, Remove Selected Theme, and Factory Reset Theme Cache. Six ready-made presets (Classic Light/Dark, EdJ Dark, Gruvbox Light, Hacker, Hot Pink) ship in `resources/themes/`.
- The palette window now remembers its size, position, and docking state across Fusion restarts.

### Changed
- Palette UI code moved from inline `<style>`/`<script>` blocks into standalone `changelog_ui.css` / `changelog_ui.js` files; the palette header now shows the installed version number.
- Switched from built installer packages (`.exe` / `.msi` / `.pkg`) to simple zip-file distribution. See **Installation** in the README.

### Fixed
- Corrected a README typo that referenced the wrong add-in name in the support section.
- The Sidecar Dashboard's dark-mode toggle and a couple of styles used hardcoded colors instead of the theme system; now consistent with the palette.
- The header version number could fail to appear if Fusion's HTML bridge wasn't ready the instant the palette script ran — there was no retry, so a slow-to-initialize bridge meant the tag stayed blank for the rest of that session. The startup request now retries until the bridge is actually available.

## [1.0.0] - 2025-11-25
Initial release.
