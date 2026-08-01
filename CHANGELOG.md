# Changelog

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

## [1.0.0] - 2025-11-25
Initial release.
