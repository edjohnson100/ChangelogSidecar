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
    # Set the advanced tooltip as a property
    cmdDef.toolClipFilename = config.SHOW_EDIT_TOOLCLIP_FILENAME

    futil.add_handler(cmdDef.commandCreated, ShowPaletteHandler)
    
    # REGISTER DOCUMENT SWITCH LISTENER
    doc_handler = DocEventsHandler()
    app.documentActivated.add(doc_handler)
    _handlers.append(doc_handler)

def stop():
    global _palette
    palette = ui.palettes.itemById(config.PALETTE_ID)
    if palette:
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
                _palette = ui.palettes.add(
                    config.PALETTE_ID, 
                    config.PALETTE_NAME, 
                    url, 
                    True, True, True, 300, 350
                )
                _palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight
                onHtmlEvent = PaletteHtmlEventHandler()
                _palette.incomingFromHTML.add(onHtmlEvent)
                _handlers.append(onHtmlEvent)
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
            --bg-container: #ffffff;
            --text-primary: #333333;
            --text-secondary: #6b778c;
            --header-border: #0052cc;
            --header-text: #172b4d;
            --milestone-bg: #ebecf0;
            --milestone-text: #172b4d;
            --entry-border: #ebecf0;
            --tag-bg: #e3fcef;
            --tag-text: #006644;
            --meta-text: #999999;
            --shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        html[data-theme="dark"] {
            --bg-body: #1e1e1e;
            --bg-container: #2d2d2d;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --header-border: #4cc9f0;
            --header-text: #ffffff;
            --milestone-bg: #3d3d3d;
            --milestone-text: #ffffff;
            --entry-border: #444444;
            --tag-bg: #0f352e;
            --tag-text: #4cc9f0;
            --meta-text: #666666;
            --shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px; background-color: var(--bg-body); color: var(--text-primary); line-height: 1.6; transition: background-color 0.3s; }
        .container { max-width: 850px; margin: 0 auto; background: var(--bg-container); padding: 30px; border-radius: 8px; box-shadow: var(--shadow); position: relative; }
        
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
        .entry { padding: 12px 0; border-bottom: 1px solid var(--entry-border); }
        .entry:last-child { border-bottom: none; }
        .timestamp { font-size: 0.85em; color: var(--text-secondary); font-weight: 600; margin-bottom: 4px; }
        .note { white-space: pre-wrap; color: var(--text-primary); }
        .meta-info { font-size: 12px; color: var(--meta-text); text-align: right; margin-top: 20px; border-top: 1px solid var(--entry-border); padding-top: 10px; }
        .refresh-tag { display: inline-block; background: var(--tag-bg); color: var(--tag-text); padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; vertical-align: middle; margin-left: 10px;}
        .sync-time { font-size: 12px; color: var(--text-secondary); display: block; margin-top: 4px; }

        .theme-switch-wrapper { display: flex; align-items: center; }
        .theme-switch { display: inline-block; height: 20px; position: relative; width: 40px; margin-right: 8px;}
        .theme-switch input { display:none; }
        .slider { background-color: #ccc; bottom: 0; cursor: pointer; left: 0; position: absolute; right: 0; top: 0; transition: .4s; border-radius: 34px; }
        .slider:before { background-color: #fff; bottom: 3px; content: ""; height: 14px; left: 3px; position: absolute; transition: .4s; width: 14px; border-radius: 50%; }
        input:checked + .slider { background-color: #4cc9f0; }
        input:checked + .slider:before { transform: translateX(20px); }
        .switch-label { font-size: 12px; color: var(--text-secondary); font-weight: bold; min-width: 70px; text-align: right;}
        
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
        except: active_html = "<p style='color:red'>Error reading active log.</p>"
    else: active_html = "<p style='font-style:italic; color:#888'>No active entries. Add one to start tracking.</p>"

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