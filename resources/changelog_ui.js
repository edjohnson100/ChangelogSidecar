// --- BRIDGE LOGIC ---
function sendToFusion(action, data = {}) {
    const args = { action: action, ...data };
    if (window.adsk) {
        window.adsk.fusionSendData('message', JSON.stringify(args));
    }
}

function openDashboard() { sendToFusion('refresh'); }

function sendEntry() {
    const text = document.getElementById('newEntryText').value;
    const autosave = document.getElementById('autosaveCheck').checked;
    if(!text) return;
    sendToFusion('add_entry', { note: text, autosave: autosave });
    document.getElementById('newEntryText').value = "";
}

function createMilestone() {
    const reason = document.getElementById('milestoneReason').value;
    if(!reason) return alert("Please enter a reason.");
    sendToFusion('create_milestone', { reason: reason });
    document.getElementById('milestoneReason').value = "";
}

function exportLog() { sendToFusion('export_log'); }

// --- THEME MANAGER ---
// Known CSS vars this UI themes -- used to snapshot theme values for JSON/CSS
// export and to parse them back out of an imported style.css bundle. Kept in
// sync with the standardized schema used across EdJ's palette-based add-ins
// and with resources/themes/*.theme.json, so imported/exported themes are
// portable.
const THEME_VARS = [
    '--font-family', '--font-size-base',
    '--bg-body', '--text-main', '--text-sub', '--border-color',
    '--row-bg', '--row-border', '--row-hover',
    '--input-bg', '--input-border', '--input-text', '--input-placeholder',
    '--toggle-bg', '--header-hover',
    '--tab-bg', '--tab-active-bg', '--tab-text', '--tab-active-text',
    '--btn-primary', '--btn-primary-hover', '--btn-primary-text',
    '--btn-success', '--btn-success-hover', '--btn-success-text',
    '--btn-secondary', '--btn-secondary-hover', '--btn-secondary-text',
    '--status-success-bg', '--status-success-text',
    '--status-error-bg', '--status-error-text',
    '--status-info-bg', '--status-info-text',
    '--focus-ring', '--text-danger', '--overlay-bg'
];
const builtInThemeIds = new Set(['light', 'dark', 'sepia']);
let customThemes = JSON.parse(localStorage.getItem('cls_custom_themes') || '{}');
let _importedThemesLoaded = false;

// Parsed straight out of changelog_ui.css at load time (:root -> 'light',
// [data-theme="X"] -> 'X'), then overlaid with customThemes overrides
// (font tweaks and full imported themes). Used to generate a full CSS
// bundle export and to seed the font-control dropdowns per theme.
let themes = {};
let baseCSS = '';

const themeSelector = document.getElementById('themeSelector');
const themeRemoveBtn = document.getElementById('themeRemoveBtn');

function applyThemeVars() {
    let styleTag = document.getElementById('dynamic-theme-overrides');
    if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = 'dynamic-theme-overrides';
        document.head.appendChild(styleTag);
    }
    let out = '';
    for (const [themeId, themeVars] of Object.entries(customThemes)) {
        const decls = Object.entries(themeVars).map(([k, v]) => `${k}: ${v};`).join(' ');
        out += `[data-theme="${themeId}"] { ${decls} }\n`;
    }
    styleTag.textContent = out;
}

// Parses :root / [data-theme="X"] blocks out of a stylesheet's text into a
// {id: {var: value}} map (ported from LiveUtilities' liveutils_script.js,
// adapted so :root maps to this app's 'light' id rather than 'Default Light'
// -- this app already has three named built-ins, not a bare default).
function parseStyleCSS(cssText) {
    const themeRegex = /(?:\/\*[\s\S]*?\*\/\s*)?(?:(:root)|\[data-theme=["']?([^"']+)["']?\])\s*\{([^}]+)\}/g;
    let match;
    const parsedThemes = {};
    while ((match = themeRegex.exec(cssText)) !== null) {
        const themeId = match[1] ? 'light' : match[2];
        const content = match[3];
        const vars = {};
        const varRegex = /(--[\w-]+)\s*:\s*([^;]+?)(?=\s*;|\s*$)/g;
        let vMatch;
        while ((vMatch = varRegex.exec(content)) !== null) {
            vars[vMatch[1].trim()] = vMatch[2].trim();
        }
        parsedThemes[themeId] = vars;
    }
    const cleanCSS = cssText.replace(themeRegex, '').trim();
    return { themes: parsedThemes, baseCSS: cleanCSS };
}

// Inverse of parseStyleCSS -- serializes the current `themes` map back into
// a full, importable style.css bundle (built-ins first, then any custom
// themes), followed by the rest of this stylesheet's rules.
function generateFullCSS() {
    let out = '';
    const order = ['light', 'dark', 'sepia'];
    const ids = [...order.filter(id => id in themes), ...Object.keys(themes).filter(id => !order.includes(id))];
    for (const id of ids) {
        const sel = id === 'light' ? ':root' : `[data-theme="${id}"]`;
        out += `/* ${id.charAt(0).toUpperCase() + id.slice(1)} */\n${sel} {\n`;
        THEME_VARS.forEach(v => { if (themes[id][v]) out += `    ${v}: ${themes[id][v]};\n`; });
        out += `}\n\n`;
    }
    return out + baseCSS;
}

function updateActiveThemeProperty(prop, value) {
    const id = themeSelector.value;
    if (!customThemes[id]) customThemes[id] = {};
    if (!themes[id]) themes[id] = {};
    customThemes[id][prop] = value;
    themes[id][prop] = value;
    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
    applyThemeVars();
}

function toggleSection(id) {
    const section = document.getElementById(id);
    section.classList.toggle('collapsed');
    const header = section.querySelector('.section-header');
    if (header) header.setAttribute('aria-expanded', !section.classList.contains('collapsed'));
}

function switchTab(tabId, event) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

function addCustomOption(id) {
    if (!themeSelector.querySelector(`option[value="${id}"]`)) {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = `${id} (custom)`;
        themeSelector.appendChild(opt);
    }
}

function mergeImportedThemes(hostThemes) {
    if (_importedThemesLoaded || !hostThemes || Object.keys(hostThemes).length === 0) return;
    _importedThemesLoaded = true;
    for (const id in hostThemes) {
        customThemes[id] = hostThemes[id];
        themes[id] = Object.assign({}, themes[id], hostThemes[id]);
        addCustomOption(id);
    }
    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
    applyThemeVars();
}

function updateRemoveButtonState() {
    const id = themeSelector.value;
    const removable = !builtInThemeIds.has(id) && (id in customThemes);
    themeRemoveBtn.disabled = !removable;
    themeRemoveBtn.title = removable ? `Remove the "${id}" theme` : 'Select a custom (imported) theme to enable';
}

function changeTheme() {
    const id = themeSelector.value;
    document.documentElement.setAttribute('data-theme', id);
    localStorage.setItem('cls_theme', id);
    updateRemoveButtonState();

    const currentVars = themes[id] || {};
    const fontFam = document.getElementById('fontFamilySelector');
    const fontSize = document.getElementById('fontSizeSelector');
    if (fontFam && currentVars['--font-family']) {
        const fam = currentVars['--font-family'].replace(/"/g, "'");
        const match = Array.from(fontFam.options).find(o => o.value === fam);
        fontFam.value = match ? match.value : fontFam.options[0].value;
    }
    if (fontSize && currentVars['--font-size-base']) {
        const match = Array.from(fontSize.options).find(o => o.value === currentVars['--font-size-base']);
        if (match) fontSize.value = match.value;
    }
}

function removeSelectedTheme() {
    const id = themeSelector.value;
    if (builtInThemeIds.has(id) || !(id in customThemes)) return;
    if (!confirm(`Permanently remove the "${id}" theme? Re-import its .theme.json to bring it back.`)) return;
    delete customThemes[id];
    delete themes[id];
    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
    sendToFusion('remove_imported_theme', { id: id });
    const opt = themeSelector.querySelector(`option[value="${id}"]`);
    if (opt) opt.remove();
    applyThemeVars();
    themeSelector.value = 'light';
    changeTheme();
}

function requestImport(type) { sendToFusion('import_theme', { file_type: type }); }

function requestExport(type) {
    const id = themeSelector.value;
    if (type === 'css') {
        sendToFusion('export_theme', { file_type: 'css', content: generateFullCSS(), default_name: 'changelog_ui.css' });
        return;
    }
    const computed = getComputedStyle(document.documentElement);
    const vars = {};
    THEME_VARS.forEach(v => { vars[v] = computed.getPropertyValue(v).trim(); });
    const content = JSON.stringify({ id: id, vars: vars }, null, 2);
    sendToFusion('export_theme', { file_type: 'json', content: content, default_name: `${id}.theme.json` });
}

function resetThemeCache() {
    if (!confirm('This will permanently delete all custom imported themes and font overrides. Continue?')) return;
    localStorage.removeItem('cls_custom_themes');
    localStorage.removeItem('cls_theme');
    customThemes = {};
    _importedThemesLoaded = false;
    sendToFusion('reset_imported_themes');
    themeSelector.querySelectorAll('option').forEach(opt => {
        if (!builtInThemeIds.has(opt.value)) opt.remove();
    });
    const styleTag = document.getElementById('dynamic-theme-overrides');
    if (styleTag) styleTag.textContent = '';
    themes = JSON.parse(JSON.stringify(baseThemes));
    themeSelector.value = 'light';
    changeTheme();
}

// --- INIT ---
// baseThemes is the pristine parse of changelog_ui.css's :root/[data-theme]
// blocks -- kept separate from `themes` (which accumulates font/import
// overrides) so Factory Reset has something to roll back to without an
// extra fetch.
let baseThemes = {};

function initThemes() {
    fetch('changelog_ui.css')
        .then(r => r.text())
        .then(css => {
            const parsed = parseStyleCSS(css);
            baseThemes = parsed.themes;
            baseCSS = parsed.baseCSS;
            themes = JSON.parse(JSON.stringify(baseThemes));
            for (const id in customThemes) {
                if (!themes[id]) themes[id] = {};
                Object.assign(themes[id], customThemes[id]);
            }
        })
        .catch(e => console.log('Theme CSS fetch failed:', e))
        .finally(() => {
            const savedTheme = localStorage.getItem('cls_theme') || 'light';
            for (const id in customThemes) addCustomOption(id);
            applyThemeVars();
            themeSelector.value = builtInThemeIds.has(savedTheme) || (savedTheme in customThemes) ? savedTheme : 'light';
            changeTheme();
        });
}
initThemes();

// window.adsk isn't guaranteed to exist the instant this script runs -- if
// sendToFusion no-ops here there is no second chance, so retry (matching the
// pattern used elsewhere in the fleet, e.g. LucysShapeForge's
// requestShapeList) until the bridge is actually ready.
function requestInitData(retriesLeft = 40) {
    if (window.adsk && typeof window.adsk.fusionSendData === 'function') {
        sendToFusion('get_init_data');
        return;
    }
    if (retriesLeft <= 0) return;
    window.setTimeout(function () {
        requestInitData(retriesLeft - 1);
    }, 250);
}
requestInitData();

window.fusionJavaScriptHandler = {
    handle: function(action, data) {
        try {
            const parsed = JSON.parse(data);
            if (action === 'init_data') {
                if (parsed.addin_version) {
                    const versionText = 'v' + parsed.addin_version;
                    document.getElementById('versionTag').textContent = versionText;
                    document.getElementById('footerVersionTag').textContent = versionText;
                }
                mergeImportedThemes(parsed.imported_themes);
            } else if (action === 'theme_imported') {
                if (parsed.file_type === 'css') {
                    const parsedCSS = parseStyleCSS(parsed.content);
                    Object.entries(parsedCSS.themes).forEach(([id, vars]) => {
                        themes[id] = Object.assign({}, themes[id], vars);
                        customThemes[id] = Object.assign({}, customThemes[id], vars);
                        if (!builtInThemeIds.has(id)) addCustomOption(id);
                        sendToFusion('save_imported_theme', { id: id, vars: vars });
                    });
                    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
                    applyThemeVars();
                    const customKeys = Object.keys(parsedCSS.themes).filter(id => !builtInThemeIds.has(id));
                    if (customKeys.length > 0) themeSelector.value = customKeys[0];
                    changeTheme();
                } else {
                    const themeData = JSON.parse(parsed.content);
                    if (themeData.vars && themeData.id !== undefined) {
                        customThemes[themeData.id] = themeData.vars;
                        themes[themeData.id] = Object.assign({}, themes[themeData.id], themeData.vars);
                        localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
                        sendToFusion('save_imported_theme', { id: themeData.id, vars: themeData.vars });
                        addCustomOption(themeData.id);
                        applyThemeVars();
                        themeSelector.value = themeData.id;
                        changeTheme();
                    }
                }
            }
        } catch (e) { console.log('Handler error', e); }
        return '';
    }
};
