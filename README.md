# Changelog Sidecar
**A persistent design journal for Autodesk Fusion.**

![Changelog Sidecar Icon](resources/AppIconHorizontal.png)

## Introduction: The "Why" and "What"

We’ve all been there: you open a Fusion design you haven't touched in six months. It’s named `MyWidget_Final_v42`. You stare at the browser tree and wonder: *"Why did I add that chamfer? Did I finish the tolerance adjustments? Is this actually the final version?"*

Fusion’s built-in version comments are great for the "What," but they don't give you much space for the "Why."

**Changelog Sidecar** is a simple, lightweight utility designed to solve this problem. It provides a dedicated space to log your thoughts, decisions, and milestones directly inside your design file.

* **Persistent Interface:** A non-intrusive palette window stays open while you work.
* **Live Dashboard (The Sidecar):** View your entire project history in a clean, auto-refreshing web dashboard on your second monitor.
* **Data Locality:** Your logs are stored as attributes *inside* the Fusion design file. If you share the file, the history travels with it. *(Note: The recipient must also have Changelog Sidecar installed to view the history).*

## Installation

### Windows Users
1.  **Download:** Download the latest installer (`ChangelogSidecar_Win.exe` or `.msi`).
2.  **Install:** Double-click the installer to run it.
    * *Note: If Windows protects your PC saying "Unknown Publisher," click **More Info** → **Run Anyway**. (I'm an indie developer, not a giant corporation!)*
3.  **Restart:** If Fusion is open, restart it to load the new add-in.

### Mac Users
1.  **Download:** Download the latest package (`ChangelogSidecar_Mac.pkg`).
2.  **Install:** Double-click the package to run the installer.
    * *Note: If macOS prevents the install, Right-Click the file and choose **Open**, then click **Open** again in the dialog box.*
3.  **Restart:** If Fusion is open, restart it to load the new add-in.

### Verify Installation
Once installed, **Changelog Sidecar** should start automatically.

1.  Open Fusion.
2.  Look for the **Changelog Sidecar** icon in the **Utilities** tab or the **Solid > Insert** panel.
3.  If you don't see it:
    * Press `Shift+S` to open **Scripts and Add-Ins**.
    * Make sure the **Add-Ins** box is checked.
    * Find "Changelog Sidecar" in the list and ensure **Run on Startup** is checked.
    * Click **Run**.

## Using Changelog Sidecar

### The Input Palette (Controller)
When you click the **Changelog Sidecar** command, a palette window opens. This is your "Controller." You can dock it to the side of your screen or leave it floating.

* **Open Log Dashboard:** Launches the "Sidecar"—a browser window that displays your full history.
* **Dark Mode Toggle:** Located in the top-right corner. Use this to switch the palette interface between light and dark themes to match your Fusion environment.
* **New Entry:** Type your notes here. Be verbose! Explain *why* you are making changes.
    * **Autosave Design Checkbox:** Checked by default. When checked, adding an entry will automatically save the current Fusion design (creating a new version) to ensure the log is permanently attached.
    * *Bypassing Autosave:* Uncheck this box if you want to log a note without triggering a version save immediately. Your note is still attached to the file session and will be permanently committed the next time you save the design manually or loag another entry with autosave turned on.
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
* **
* **Icons:** "Lucy in the Sidecar" artwork generated via [Artistly](https://artistly.ai/).
* **Installers:** Built using the **WiX Toolset** (Windows) and standard **macOS Packaging Tools**.
* **Lucy (The Cavachon Puppy):**  
***Chief Wellness Officer & Director of Mandatory Breaks***
    * Thank you for ensuring I maintained healthy circulation by interrupting my deep coding sessions with urgent requests for play.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

***

*Happy Making!*
*— EdJ*