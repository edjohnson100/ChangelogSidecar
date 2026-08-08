# Changelog

## [1.3.2] - 2026-08-08

### Fixed
- **Accessibility: Font Family / Base Font Size controls weren't reaching every element.** Buttons, text inputs, the header theme dropdown, the Theme Manager's own Font Family/Base Font Size selectors, and the footer kept their hardcoded font instead of tracking the Theme Manager's Font Family/Base Font Size choices — a browser default where form controls don't inherit font settings from the page. Added explicit `font-family`/`font-size` inheritance to every affected element, and converted a few remaining hardcoded pixel sizes (including one inline style that was silently overriding the stylesheet) to scale relative to the Base Font Size setting.

## [1.3.1] - 2026-08-07

### Fixed
- **Accessibility: button text contrast.** Button foreground colors were hardcoded to white; several theme/button combinations (e.g. the default Light theme's blue "Save Entry" button, the green "Open Log Dashboard" button, and the Hot Pink preset) failed WCAG AA contrast. Button text now goes through a `--btn-primary-text`/`--btn-success-text` variable computed per theme, so it switches to dark text where the background is too light for white to stay readable.
- **Accessibility: keyboard focus.** Every interactive control in the palette (buttons, the theme dropdown, inputs, the Theme Manager's collapsible header) now shows a visible focus ring when navigated to with the keyboard, and the Theme Manager section header — previously mouse-only — can now be opened and closed with Enter/Space.
- Added the underlying `--focus-ring`, `--text-danger`, and `--overlay-bg` variables (and the two button-text variables above) to all three built-in themes and all six shipped `.theme.json` presets, so imported themes carry correct, theme-specific contrast values instead of silently falling back to a default that may not fit their accent color.

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
