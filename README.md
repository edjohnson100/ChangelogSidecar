# Changelog Sidecar
**Version:** 1.3.0

**Author:** Ed Johnson (Making With An EdJ)

**Persistent changelog and milestone utility for tracking design history. Includes a live 'Sidecar' browser dashboard with auto-refresh, milestone creation, and text export.**

<img src="ChangelogSidecarAppIcon.png" alt="App Icon" width="300">

## Introduction: The "Why" and "What"

We’ve all been there: you open a Fusion design you haven't touched in six months. It’s named `MyWidget_Final_v42`. You stare at the browser tree and wonder: *"Why did I add that chamfer? Did I finish the tolerance adjustments? Is this actually the final version?"*

Fusion’s built-in version comments are great for the "What," but they don't give you much space for the "Why."

**Changelog Sidecar** is a simple, lightweight utility designed to solve this problem. It provides a dedicated space to log your thoughts, decisions, and milestones directly inside your design file.

* **Persistent Interface:** A non-intrusive palette window stays open while you work, and now remembers its size, position, and docking state between Fusion sessions.
* **Live Dashboard (The Sidecar):** View your entire project history in a clean, auto-refreshing web dashboard on your second monitor.
* **Data Locality:** Your logs are stored as attributes *inside* the Fusion design file. If you share the file, the history travels with it. *(Note: The recipient must also have Changelog Sidecar installed to view the history).*

---
## ✨ What's New in v1.3.0

* **Themes tab:** The palette is now split into two tabs — **Changelog** (your entries and utilities) and **Themes** (the full Theme Manager).
* **Font controls:** Pick a Font Family and Base Font Size for the palette, right from the Themes tab.
* **Full theme-bundle import/export:** Share a complete `style.css` of built-in and custom themes at once, in addition to the existing single-theme `.theme.json` import/export.

*For older release notes, please see the **[CHANGELOG](CHANGELOG.md)**.*

## Installation

### Manual Installation Options

This add-in requires a quick manual installation. You can choose to install it in Fusion's default directory or a custom folder of your choice.

#### Option 1: Install in the Default Fusion Directory
1. **Download:** Download the source code as a ZIP file and extract the `ChangelogSidecar-main` folder. Rename the folder to `ChangelogSidecar` (remove the `-main` suffix) — Fusion requires the folder name to match the add-in name exactly, so it won't run correctly if you skip this step.
Download the zip file using the green `Code` button above or simply click this link: [ChangelogSidecar Main Branch](https://github.com/edjohnson100/ChangelogSidecar/archive/refs/heads/main.zip)
2. **Move the Folder:** Move the entire `ChangelogSidecar` folder into your native Fusion Add-Ins directory:
   * **Windows:** `%appdata%\Autodesk\Autodesk Fusion 360\API\Addins`
   * **Mac:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Addins`
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Run the Add-in:** Make sure the **Add-ins** filter checkbox is checked. You should see **Changelog Sidecar** in the list of add-ins. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

#### Option 2: Install in a Custom Directory
1. **Download:** Download the source code as a ZIP file and extract the `ChangelogSidecar` folder. Rename the folder to `ChangelogSidecar`.
2. **Organize:** Create a dedicated folder on your computer for your Fusion tools (e.g., `Documents\Fusion_Tools`) and move the `ChangelogSidecar` folder inside it (remove the `-main` suffix) — Fusion requires the folder name to match the add-in name exactly, so it won't run correctly if you skip this step.
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Add the Add-in:** Click the grey **"+"** icon next to the search box at the top of the dialog and select **Script or add-in from device**.
5. **Locate:** Navigate to your custom folder, select the `ChangelogSidecar` folder, and click **Select Folder**.
6. **Run the Add-in:** Make sure the **Add-ins** filter checkbox is checked. You should see **Changelog Sidecar** in the list of add-ins. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

## Using Changelog Sidecar

### The Input Palette (Controller)
When you click the **Changelog Sidecar** command, a palette window opens. This is your "Controller." You can dock it to the side of your screen or leave it floating — it'll remember where you put it.

* **Open Log Dashboard:** Launches the "Sidecar"—a browser window that displays your full history.
* **Changelog / Themes tabs:** The palette is split into two tabs. **Changelog** holds your entries and utilities (below); **Themes** holds the full Theme Manager.
* **Theme Manager (Themes tab):** Pick **Light**, **Dark**, or **Sepia** from the dropdown in the header, or build your own:
    * **Font Family / Base Font Size:** Adjust the palette's font per theme.
    * **Import style.css / Export style.css:** Load or share a full bundle of themes (built-in and custom) in one file.
    * **Import .json / Export .json:** Load a single `.theme.json` file someone shared with you, or export your current theme (built-in or custom) to share or back up.
    * **Remove Selected Theme:** Deletes an imported custom theme. Only enabled when a custom theme is selected—the built-in Light/Dark/Sepia themes can't be removed.
    * **Factory Reset Theme Cache:** Wipes all imported custom themes and font overrides, reverting to the shipped defaults, in case things get cluttered.
    * A handful of ready-made presets (Classic Light/Dark, EdJ Dark, Gruvbox Light, Hacker, Hot Pink) ship in `resources/themes/`—import any of them to try a look before designing your own.
* **New Entry:** Type your notes here. Be verbose! Explain *why* you are making changes.
    * **Autosave Design Checkbox:** Checked by default. When checked, adding an entry will automatically save the current Fusion design (creating a new version) to ensure the log is permanently attached.
    * *Bypassing Autosave:* Uncheck this box if you want to log a note without triggering a version save immediately. Your note is still attached to the file session and will be permanently committed the next time you save the design manually or log another entry with autosave turned on.
* **Utilities:**
    * **Create Milestone:** Use this when you reach a major turning point (e.g., "Prototype 1 Complete"). It archives the current active log into a history block with a ***Milestone*** header and starts a fresh active log.
    * **Export:** Saves your entire history (Active + Milestones) to a `.txt` file on your computer.

### The Sidecar Dashboard
The Dashboard is a "Live View" of your project history generated in your web browser.

* **Window Management:** The dashboard attempts to open in a new window, but modern browsers often force it into a new tab.
    * *Pro Tip:* Drag the tab out of your browser bar to create a separate floating window. You can then resize it into a narrow "Sidecar" to sit next to your Fusion window (great for single monitors) or move it to a second screen.
* **Auto-Refresh:** As you add entries in Fusion, this window updates automatically within seconds.
* **Smart Scroll:** The dashboard remembers your scroll position, so new entries appear at the top without disrupting your reading.
* **Sync Interval:** Use the slider to adjust how often the dashboard checks for updates, or set it to "0" to pause syncing.

## Tech Stack

For the fellow coders and makers out there, here is how Changelog Sidecar was built:

* **Language:** Python (Fusion API)
* **Interface:** HTML/CSS/JavaScript (running in a Fusion Palette)
* **Data Storage:** Custom Attributes (`Design.attributes`) stored directly on the Root Component of the active design.
* **Dashboard Engine:** A custom "Sidecar" generator that writes a localized, self-refreshing HTML file to the user's temporary directory, bypassing standard browser security restrictions for a seamless local experience.

## Acknowledgements & Credits

* **Developer:** Ed Johnson ([Making With An EdJ](https://www.youtube.com/@makingwithanedj))
* **AI Assistance:** Developed with coding assistance from Google's Gemini 3 Pro model.
* **Icons:** "Lucy in the Sidecar" artwork generated via [Artistly](https://artistly.ai/).
* **Lucy (The Cavachon Puppy):**
***Chief Wellness Officer & Director of Mandatory Breaks***
    * Thank you for ensuring I maintained healthy circulation by interrupting my deep coding sessions with urgent requests for play.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

---

## ❤️ Support the Maker (and Lucy!)

I develop these tools to improve my own workflows and love sharing them with the community. If you find Changelog Sidecar useful and want to say thanks, feel free to **[buy Lucy a dog treat on Ko-fi](https://ko-fi.com/makingwithanedj)**!

***

*Happy Making!*
*— EdJ*
