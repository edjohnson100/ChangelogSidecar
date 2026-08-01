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
// Known CSS vars this UI themes -- used to snapshot the currently
// active theme's resolved values for JSON export. Kept in sync with the
// standardized schema used across EdJ's palette-based add-ins and with
// resources/themes/*.theme.json, so imported/exported themes are portable.
const THEME_VARS = [
    '--font-family', '--font-size-base',
    '--bg-body', '--text-main', '--text-sub', '--border-color',
    '--row-bg', '--row-border', '--row-hover',
    '--input-bg', '--input-border', '--input-text', '--input-placeholder',
    '--toggle-bg', '--header-hover',
    '--tab-bg', '--tab-active-bg', '--tab-text', '--tab-active-text',
    '--btn-primary', '--btn-primary-hover',
    '--btn-success', '--btn-success-hover',
    '--btn-secondary', '--btn-secondary-hover', '--btn-secondary-text',
    '--status-success-bg', '--status-success-text',
    '--status-error-bg', '--status-error-text',
    '--status-info-bg', '--status-info-text'
];
const builtInThemeIds = new Set(['light', 'dark', 'sepia']);
let customThemes = JSON.parse(localStorage.getItem('cls_custom_themes') || '{}');
let _importedThemesLoaded = false;

const themeSelector = document.getElementById('themeSelector');
const themeRemoveBtn = document.getElementById('themeRemoveBtn');

function applyThemeVars(id, vars) {
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
}

function removeSelectedTheme() {
    const id = themeSelector.value;
    if (builtInThemeIds.has(id) || !(id in customThemes)) return;
    if (!confirm(`Permanently remove the "${id}" theme? Re-import its .theme.json to bring it back.`)) return;
    delete customThemes[id];
    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
    sendToFusion('remove_imported_theme', { id: id });
    const opt = themeSelector.querySelector(`option[value="${id}"]`);
    if (opt) opt.remove();
    applyThemeVars();
    themeSelector.value = 'light';
    changeTheme();
}

function requestImportTheme() { sendToFusion('import_theme'); }

function requestExportTheme() {
    const id = themeSelector.value;
    const computed = getComputedStyle(document.documentElement);
    const vars = {};
    THEME_VARS.forEach(v => { vars[v] = computed.getPropertyValue(v).trim(); });
    const content = JSON.stringify({ id: id, vars: vars }, null, 2);
    sendToFusion('export_theme', { content: content, default_name: `${id}.theme.json` });
}

function resetThemeCache() {
    if (!confirm('This will permanently delete all custom imported themes. Continue?')) return;
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
    themeSelector.value = 'light';
    changeTheme();
}

// --- INIT ---
const savedTheme = localStorage.getItem('cls_theme') || 'light';
for (const id in customThemes) addCustomOption(id);
applyThemeVars();
themeSelector.value = builtInThemeIds.has(savedTheme) || (savedTheme in customThemes) ? savedTheme : 'light';
changeTheme();
sendToFusion('get_init_data');

window.fusionJavaScriptHandler = {
    handle: function(action, data) {
        try {
            const parsed = JSON.parse(data);
            if (action === 'init_data') {
                if (parsed.addin_version) {
                    document.getElementById('versionTag').textContent = 'v' + parsed.addin_version;
                }
                mergeImportedThemes(parsed.imported_themes);
            } else if (action === 'theme_imported') {
                const themeData = JSON.parse(parsed.content);
                if (themeData.vars && themeData.id !== undefined) {
                    customThemes[themeData.id] = themeData.vars;
                    localStorage.setItem('cls_custom_themes', JSON.stringify(customThemes));
                    sendToFusion('save_imported_theme', { id: themeData.id, vars: themeData.vars });
                    addCustomOption(themeData.id);
                    applyThemeVars();
                    themeSelector.value = themeData.id;
                    changeTheme();
                }
            }
        } catch (e) { console.log('Handler error', e); }
        return '';
    }
};
