import adsk.core, adsk.fusion, traceback, json, datetime
import sys, os
import webbrowser 
import tempfile
import time 
import re 
from pathlib import Path

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import config
from lib import fusionAddInUtils as futil

app = adsk.core.Application.get()
ui = app.userInterface

_palette = None
_handlers = []

def _read_manifest_version():
    manifest_path = os.path.join(root_dir, 'ChangelogSidecar.manifest')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('version', '')
    except Exception:
        return ''

ADDIN_VERSION = _read_manifest_version()

# Host-side store for user-imported themes -- separate from the built-in
# Light/Dark/Sepia themes baked into changelog_ui.html. Per-machine, gitignored
# (same pattern as LiveUtilities/GridfinityGeneratorPlus's imported_themes.json):
# survives a restart or a localStorage wipe.
IMPORTED_THEMES_PATH = os.path.join(root_dir, 'imported_themes.json')

def load_imported_themes():
    if not os.path.exists(IMPORTED_THEMES_PATH):
        return {}
    try:
        with open(IMPORTED_THEMES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_imported_theme(theme_id, theme_vars):
    themes = load_imported_themes()
    themes[theme_id] = theme_vars
    with open(IMPORTED_THEMES_PATH, 'w', encoding='utf-8') as f:
        json.dump(themes, f, indent=2)

def delete_imported_theme(theme_id):
    themes = load_imported_themes()
    if theme_id in themes:
        del themes[theme_id]
        with open(IMPORTED_THEMES_PATH, 'w', encoding='utf-8') as f:
            json.dump(themes, f, indent=2)

def clear_imported_themes():
    """Used by Factory Reset Theme Cache -- wipes every host-persisted
    imported theme, not just localStorage, so a reset actually resets."""
    if os.path.exists(IMPORTED_THEMES_PATH):
        os.remove(IMPORTED_THEMES_PATH)

def _themes_dialog_dir():
    themes_dir = os.path.join(root_dir, 'resources', 'themes')
    return themes_dir if os.path.isdir(themes_dir) else os.path.join(root_dir, 'resources')

# General-purpose host-side settings file (palette geometry, and anything
# else added later). Per-machine, gitignored -- separate from
# imported_themes.json, which is theme-import-specific.
CONFIG_PATH = os.path.join(root_dir, 'config.json')

def _load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

def _save_config(updates):
    config_data = _load_config()
    config_data.update(updates)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    except OSError:
        pass

def _save_palette_geometry(palette):
    # Fusion's Palette has no resize/move event -- width/height/left/top/
    # dockingState are only readable on demand, so this is called at the two
    # points the palette's lifecycle actually gives us: the user closing it
    # and the add-in being stopped (right before palette.deleteMe()).
    try:
        _save_config({'palette_geometry': {
            'width': palette.width,
            'height': palette.height,
            'left': palette.left,
            'top': palette.top,
            'docking_state': int(palette.dockingState),
        }})
    except RuntimeError:
        pass

def _restore_palette_geometry(palette):
    geometry = _load_config().get('palette_geometry', {})
    try:
        if 'left' in geometry:
            palette.left = geometry['left']
        if 'top' in geometry:
            palette.top = geometry['top']
        if 'docking_state' in geometry:
            palette.dockingState = geometry['docking_state']
    except RuntimeError:
        pass

def export_theme_logic(content, default_name):
    fileDialog = ui.createFileDialog()
    fileDialog.title = 'Export Theme'
    fileDialog.filter = 'JSON Files (*.json);;All Files (*.*)'
    fileDialog.initialDirectory = _themes_dialog_dir()
    fileDialog.initialFilename = default_name
    if fileDialog.showSave() == adsk.core.DialogResults.DialogOK:
        try:
            with open(fileDialog.filename, 'w', encoding='utf-8') as f:
                f.write(content)
            ui.messageBox(f'Theme exported to {fileDialog.filename}')
        except Exception as e:
            ui.messageBox(f'Failed to save theme:\n{str(e)}')

def import_theme_logic():
    fileDialog = ui.createFileDialog()
    fileDialog.title = 'Import Theme'
    fileDialog.filter = 'JSON Files (*.json);;All Files (*.*)'
    fileDialog.initialDirectory = _themes_dialog_dir()
    if fileDialog.showOpen() == adsk.core.DialogResults.DialogOK:
        try:
            with open(fileDialog.filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            ui.messageBox(f'Failed to read theme:\n{str(e)}')
    return None

def log_to_console(msg):
    try:
        console = ui.palettes.itemById('TextCommands')
        if console:
            console.writeText(str(msg))
    except: pass

def start():
    cmdDef = ui.commandDefinitions.itemById(config.SHOW_EDIT_COMMAND_ID)
    if not cmdDef:
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            config.SHOW_EDIT_COMMAND_ID,
            config.SHOW_EDIT_COMMAND_NAME,
            config.SHOW_EDIT_COMMAND_TOOLTIP,
            config.SHOW_EDIT_RESOURCE_FOLDER
        )
    # Set the advanced tooltip as a property. Non-fatal: a bad/incompatible
    # toolclip image shouldn't take the whole command (and thus the palette)
    # down with it.
    try:
        cmdDef.toolClipFilename = config.SHOW_EDIT_TOOLCLIP_FILENAME
    except RuntimeError:
        log_to_console('Failed to set toolClipFilename:\n{}'.format(traceback.format_exc()))

    futil.add_handler(cmdDef.commandCreated, ShowPaletteHandler)
    
    # REGISTER DOCUMENT SWITCH LISTENER
    doc_handler = DocEventsHandler()
    app.documentActivated.add(doc_handler)
    _handlers.append(doc_handler)

def stop():
    global _palette
    palette = ui.palettes.itemById(config.PALETTE_ID)
    if palette:
        _save_palette_geometry(palette)
        palette.deleteMe()
        _palette = None
    cmdDef = ui.commandDefinitions.itemById(config.SHOW_EDIT_COMMAND_ID)
    if cmdDef:
        cmdDef.deleteMe()

# --- DOCUMENT SWITCH HANDLER ---
class DocEventsHandler(adsk.core.DocumentEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            #log_to_console(f"Switched to: {args.document.name}")
            generate_and_open_report(open_browser=False)
        except:
            pass

class PaletteClosedHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        palette = ui.palettes.itemById(config.PALETTE_ID)
        if palette:
            _save_palette_geometry(palette)

# --- 1. SHOW PALETTE HANDLER ---
class ShowPaletteHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _palette, _handlers
            
            cmd_path = Path(__file__).resolve().parent
            root_path = cmd_path.parent
            html_file = root_path / 'resources' / 'changelog_ui.html'
            
            if not html_file.exists():
                 html_file = root_path / 'resources' / 'palette.html'

            url = html_file.as_uri()

            _palette = ui.palettes.itemById(config.PALETTE_ID)

            if not _palette:
                geometry = _load_config().get('palette_geometry', {})
                width = geometry.get('width', 300)
                height = geometry.get('height', 350)

                _palette = ui.palettes.add(
                    config.PALETTE_ID,
                    config.PALETTE_NAME,
                    url,
                    True, True, True, width, height
                )
                _palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight
                _restore_palette_geometry(_palette)
                onHtmlEvent = PaletteHtmlEventHandler()
                _palette.incomingFromHTML.add(onHtmlEvent)
                _handlers.append(onHtmlEvent)

                onClose = PaletteClosedHandler()
                _palette.closed.add(onClose)
                _handlers.append(onClose)
            else:
                _palette.htmlFileURL = url

            _palette.isVisible = True

        except:
            if ui:
                ui.messageBox('ShowPalette Failed:\n{}'.format(traceback.format_exc()))

# --- 2. HTML EVENT HANDLER ---
class PaletteHtmlEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.doEvents()
            htmlArgs = json.loads(args.data)
            action = htmlArgs.get('action', '')
            
            if action == 'refresh':
                generate_and_open_report(open_browser=True)
            elif action == 'add_entry':
                add_entry_logic(htmlArgs.get('note'), htmlArgs.get('autosave'))
                adsk.doEvents()
                generate_and_open_report(open_browser=False)
            elif action == 'create_milestone':
                create_milestone_logic(htmlArgs.get('reason'))
                adsk.doEvents()
                generate_and_open_report(open_browser=False)
            elif action == 'export_log':
                export_log_logic()

            elif action == 'get_init_data':
                if _palette:
                    _palette.sendInfoToHTML('init_data', json.dumps({
                        'addin_version': ADDIN_VERSION,
                        'imported_themes': load_imported_themes()
                    }))

            elif action == 'export_theme':
                export_theme_logic(htmlArgs.get('content'), htmlArgs.get('default_name'))

            elif action == 'import_theme':
                content = import_theme_logic()
                if content and _palette:
                    _palette.sendInfoToHTML('theme_imported', json.dumps({'content': content}))

            elif action == 'save_imported_theme':
                theme_id = htmlArgs.get('id')
                theme_vars = htmlArgs.get('vars')
                if theme_id and isinstance(theme_vars, dict):
                    save_imported_theme(theme_id, theme_vars)

            elif action == 'remove_imported_theme':
                theme_id = htmlArgs.get('id')
                if theme_id:
                    delete_imported_theme(theme_id)

            elif action == 'reset_imported_themes':
                clear_imported_themes()
        except:
            log_to_console('Handler Error:\n{}'.format(traceback.format_exc()))

# --- 3. THE SIDECAR GENERATOR (Styled Header) ---
def generate_and_open_report(open_browser=True):
    # log_to_console("Sidecar: Generating report...")
    design = app.activeProduct
    if not design: return
    root = design.rootComponent
    
    full_name = app.activeDocument.name
    stable_name = re.sub(r'\s+v\d+$', '', full_name)

    # Styles
    css = """
    <style>
        :root {
            --bg-body: #f4f6f8;
            --row-bg: #ffffff;
            --text-main: #333333;
            --text-sub: #6b778c;
            --header-border: #0052cc;
            --header-text: #172b4d;
            --milestone-bg: #ebecf0;
            --milestone-text: #172b4d;
            --row-border: #ebecf0;
            --tag-bg: #e3fcef;
            --tag-text: #006644;
            --meta-text: #999999;
            --shadow: 0 4px 12px rgba(0,0,0,0.1);
            --toggle-bg: #ccc;
            --btn-primary: #007bff;
            --status-error-text: #c0392b;
        }

        html[data-theme="dark"] {
            --bg-body: #1e1e1e;
            --row-bg: #2d2d2d;
            --text-main: #e0e0e0;
            --text-sub: #a0a0a0;
            --header-border: #4cc9f0;
            --header-text: #ffffff;
            --milestone-bg: #3d3d3d;
            --milestone-text: #ffffff;
            --row-border: #444444;
            --tag-bg: #0f352e;
            --tag-text: #4cc9f0;
            --meta-text: #666666;
            --shadow: 0 4px 12px rgba(0,0,0,0.4);
            --toggle-bg: #555;
            --btn-primary: #0069d9;
            --status-error-text: #ff6b6b;
        }

        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px; background-color: var(--bg-body); color: var(--text-main); line-height: 1.6; transition: background-color 0.3s; }
        .container { max-width: 850px; margin: 0 auto; background: var(--row-bg); padding: 30px; border-radius: 8px; box-shadow: var(--shadow); position: relative; }

        .header-row { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 15px; border-bottom: 3px solid var(--header-border); margin-bottom: 20px; }
        .title-block h1 { margin: 0; padding: 0; color: var(--header-text); font-size: 24px; border: none; }

        .controls { display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }

        /* --- STYLED ACTIVE HEADER (NEW) --- */
        h2 {
            background-color: var(--tag-bg);
            color: var(--tag-text);
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 5px solid var(--tag-text);
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: bold;
        }

        .milestone-header { background-color: var(--milestone-bg); padding: 10px 15px; border-radius: 4px; margin-top: 30px; border-left: 5px solid var(--header-border); color: var(--milestone-text); font-weight: bold; }
        .entry { padding: 12px 0; border-bottom: 1px solid var(--row-border); }
        .entry:last-child { border-bottom: none; }
        .timestamp { font-size: 0.85em; color: var(--text-sub); font-weight: 600; margin-bottom: 4px; }
        .note { white-space: pre-wrap; color: var(--text-main); }
        .meta-info { font-size: 12px; color: var(--meta-text); text-align: right; margin-top: 20px; border-top: 1px solid var(--row-border); padding-top: 10px; }
        .refresh-tag { display: inline-block; background: var(--tag-bg); color: var(--tag-text); padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; vertical-align: middle; margin-left: 10px;}
        .sync-time { font-size: 12px; color: var(--text-sub); display: block; margin-top: 4px; }

        .theme-switch-wrapper { display: flex; align-items: center; }
        .theme-switch { display: inline-block; height: 20px; position: relative; width: 40px; margin-right: 8px;}
        .theme-switch input { display:none; }
        .slider { background-color: var(--toggle-bg); bottom: 0; cursor: pointer; left: 0; position: absolute; right: 0; top: 0; transition: .4s; border-radius: 34px; }
        .slider:before { background-color: #fff; bottom: 3px; content: ""; height: 14px; left: 3px; position: absolute; transition: .4s; width: 14px; border-radius: 50%; }
        input:checked + .slider { background-color: var(--btn-primary); }
        input:checked + .slider:before { transform: translateX(20px); }
        .switch-label { font-size: 12px; color: var(--text-sub); font-weight: bold; min-width: 70px; text-align: right;}

        input[type=range] { width: 100px; margin-right: 8px; cursor: pointer; }
    </style>
    """

    # READ ACTIVE
    active_html = ""
    attr = root.attributes.itemByName(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY)
    if attr:
        try:
            entries = json.loads(attr.value)
            for entry in reversed(entries):
                ts = str(entry.get('timestamp',''))
                user = str(entry.get('user',''))
                note = str(entry.get('note','')).replace('\n', '<br>')
                active_html += f"<div class='entry'><div class='timestamp'>{ts} • {user}</div><div class='note'>{note}</div></div>"
        except: active_html = "<p style='color:var(--status-error-text)'>Error reading active log.</p>"
    else: active_html = "<p style='font-style:italic; color:var(--meta-text)'>No active entries. Add one to start tracking.</p>"

    # READ ARCHIVES
    archive_html = ""
    all_attrs = root.attributes.itemsByGroup(config.CHANGELOG_GROUP_KEY)
    archive_list = [a for a in all_attrs if a.name.startswith(config.ARCHIVE_LOG_PREFIX)]
    archive_list.sort(key=lambda x: x.name, reverse=True)
    
    for attr in archive_list:
        try:
            ts_str = attr.name.replace(config.ARCHIVE_LOG_PREFIX, "")
            dt = datetime.datetime.strptime(ts_str, '%Y-%m-%dT%H%M%S')
            friendly = dt.strftime('%Y-%m-%d %H:%M')
        except: friendly = attr.name
        
        archive_html += f"<div class='milestone-header'>MILESTONE: {friendly}</div>"
        try:
            entries = json.loads(attr.value)
            for entry in reversed(entries):
                 ts = str(entry.get('timestamp',''))
                 user = str(entry.get('user',''))
                 note = str(entry.get('note','')).replace('\n', '<br>')
                 archive_html += f"<div class='entry'><div class='timestamp'>{ts} • {user}</div><div class='note'>{note}</div></div>"
        except: pass

    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    # BUILD HTML
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Changelog: {stable_name}</title>
        <meta charset="UTF-8">
        <script>
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);

            if ('scrollRestoration' in history) {{
                history.scrollRestoration = 'manual';
            }}

            window.addEventListener('DOMContentLoaded', () => {{
                const contentNode = document.getElementById('log-payload');
                const currentLen = contentNode ? contentNode.innerHTML.length : 0;
                const lastLen = parseInt(sessionStorage.getItem('contentLen')) || 0;
                const scrollPos = sessionStorage.getItem('scrollPos');

                if (currentLen !== lastLen) {{
                    window.scrollTo(0, 0);
                    sessionStorage.setItem('contentLen', currentLen);
                }} else if (scrollPos) {{
                    window.scrollTo(0, parseInt(scrollPos));
                }}
            }});

            function doReload() {{
                const stored = localStorage.getItem('syncInterval');
                const interval = stored !== null ? parseInt(stored) : 2;

                if (interval > 0) {{
                    sessionStorage.setItem('scrollPos', window.scrollY);
                    var currentUrl = window.location.href.split('?')[0];
                    var newUrl = currentUrl + '?t=' + new Date().getTime();
                    window.location.replace(newUrl);
                }} else {{
                    console.log("Sync paused.");
                }}
            }}
            
            window.addEventListener('load', () => {{
                const stored = localStorage.getItem('syncInterval');
                const interval = stored !== null ? parseInt(stored) : 2;
                if (interval > 0) {{
                    setTimeout(doReload, interval * 1000);
                }}
            }});
        </script>
        {css}
    </head>
    <body>
        <div class="container">
            <div class="header-row">
                <div class="title-block">
                    <h1>{stable_name} <span class="refresh-tag">LIVE SYNC</span></h1>
                    <span class="sync-time">Last Synced: {now_str}</span>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label class="theme-switch" for="theme-checkbox">
                            <input type="checkbox" id="theme-checkbox" />
                            <div class="slider"></div>
                        </label>
                        <span class="switch-label">Dark Mode</span>
                    </div>

                    <div class="control-group">
                        <input type="range" id="sync-slider" min="0" max="10" step="1" value="2">
                        <span id="sync-label" class="switch-label">Sync: 2s</span>
                    </div>
                </div>
            </div>
            
            <div id="log-payload">
                <h2>Active Workspace</h2>
                {active_html}
                {archive_html}
            </div>
            
            <div class="meta-info">Generated by Changelog With An EdJ • Auto-refresh active</div>
        </div>

        <script>
            const toggleSwitch = document.getElementById('theme-checkbox');
            const currentTheme = localStorage.getItem('theme');
            if (currentTheme === 'dark') {{ toggleSwitch.checked = true; }}

            toggleSwitch.addEventListener('change', function(e) {{
                const theme = e.target.checked ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', theme);
                localStorage.setItem('theme', theme);
            }});

            const syncSlider = document.getElementById('sync-slider');
            const syncLabel = document.getElementById('sync-label');
            const savedInterval = localStorage.getItem('syncInterval');
            if (savedInterval !== null) {{
                syncSlider.value = savedInterval;
                updateLabel(savedInterval);
            }}

            function updateLabel(val) {{
                syncLabel.textContent = (val == 0) ? "Sync: Paused" : "Sync: " + val + "s";
            }}

            syncSlider.addEventListener('input', function(e) {{
                updateLabel(e.target.value);
            }});

            syncSlider.addEventListener('change', function(e) {{
                const newVal = parseInt(e.target.value);
                localStorage.setItem('syncInterval', newVal);
                if (newVal > 0) {{ doReload(); }}
            }});
        </script>
    </body>
    </html>
    """

    temp_dir = tempfile.gettempdir()
    
    # Universal Filename
    file_path = os.path.join(temp_dir, "FusionLog_Live_Dashboard.html")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            #log_to_console(f"Sidecar: Write success to {file_path}")
            break 
        except Exception as e:
            if i == max_retries - 1:
                log_to_console(f"Sidecar: FAILED to write. {e}")
            else:
                log_to_console(f"Sidecar: Locked? Retrying... ({i+1})")
                time.sleep(0.2)
        
    if open_browser:
        webbrowser.open_new('file://' + file_path)

# --- HELPERS (unchanged) ---
def get_timestamp_and_user():
    try:
        username = app.currentUser.displayName
    except:
        username = 'Unknown'
    now = datetime.datetime.now().astimezone()
    tz_name = now.tzname()
    if tz_name and any(x.islower() for x in tz_name):
            tz_abbr = ''.join([word[0] for word in tz_name.split() if word])
    else:
            tz_abbr = tz_name if tz_name else ''
    return now.strftime(f'%Y-%m-%d - %H:%M:%S {tz_abbr}'), username

def add_entry_logic(note_text, autosave):
    design = app.activeProduct
    if not design: return
    root = design.rootComponent
    
    timestamp, user = get_timestamp_and_user()
    current_list = []
    attr = root.attributes.itemByName(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY)
    if attr: current_list = json.loads(attr.value)
    
    current_list.append({'timestamp': timestamp, 'user': user, 'note': note_text})
    root.attributes.add(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY, json.dumps(current_list, indent=4))
    
    if autosave:
        doc = app.activeDocument
        if doc.isSaved:
            try: doc.save(f'C-log: {note_text[:50]}')
            except: pass

def create_milestone_logic(reason):
    design = app.activeProduct
    root = design.rootComponent
    
    current_list = []
    attr = root.attributes.itemByName(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY)
    if attr: current_list = json.loads(attr.value)
    
    timestamp, user = get_timestamp_and_user()
    milestone_entry = {'timestamp': timestamp, 'user': user, 'note': f"--- MILESTONE CREATED ---\nReason: {reason}"}
    current_list.append(milestone_entry)
    
    archive_name = f"{config.ARCHIVE_LOG_PREFIX}{datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')}"
    root.attributes.add(config.CHANGELOG_GROUP_KEY, archive_name, json.dumps(current_list, indent=4))
    
    new_log = [milestone_entry]
    root.attributes.add(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY, json.dumps(new_log, indent=4))
    
    doc = app.activeDocument
    if doc.isSaved:
        try: doc.save(f'C-log Milestone: {reason[:50]}')
        except: pass

def export_log_logic():
    design = app.activeProduct
    doc = app.activeDocument
    root = design.rootComponent
    
    export_str = f"DESIGN: {doc.name}\n\n"
    all_attrs = root.attributes.itemsByGroup(config.CHANGELOG_GROUP_KEY)
    archive_list = [a for a in all_attrs if a.name.startswith(config.ARCHIVE_LOG_PREFIX)]
    archive_list.sort(key=lambda x: x.name)
    
    for attr in archive_list:
        export_str += f"--- ARCHIVE {attr.name} ---\n"
        try:
            for entry in json.loads(attr.value):
                export_str += f"[{entry['timestamp']}] {entry['user']}: {entry['note']}\n"
        except: pass
        export_str += "\n"

    attr = root.attributes.itemByName(config.CHANGELOG_GROUP_KEY, config.CHANGELOG_NAME_KEY)
    if attr:
        export_str += "--- ACTIVE LOG ---\n"
        try:
            for entry in json.loads(attr.value):
                export_str += f"[{entry['timestamp']}] {entry['user']}: {entry['note']}\n"
        except: pass

    fileDialog = ui.createFileDialog()
    fileDialog.title = 'Export Changelog'
    fileDialog.filter = 'Text Files (*.txt);;All Files (*.*)'
    fileDialog.initialFilename = f"{doc.name}_changelog.txt"
    if fileDialog.showSave() == adsk.core.DialogResults.DialogOK:
        with open(fileDialog.filename, 'w', encoding='utf-8') as f:
            f.write(export_str)
        ui.messageBox(f'Exported to {fileDialog.filename}')