<p align="center">
  <a href="https://abdani.github.io/Android-Media-Separator/"><img src="docs/images/social-preview.png" alt="Android Media Separator — sort your phone's media on Windows"></a>
</p>

<h1 align="center">Android Media Separator</h1>

<p align="center">
  Sorts the photos, videos, audio and documents from an Android phone into neat folders on your PC,<br>
  straight over a USB cable or from a folder you already copied.
</p>

<p align="center">
  <img alt="Windows 10/11" src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?style=for-the-badge&logo=windows11&logoColor=white">
  <img alt="Python 3" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Android over USB" src="https://img.shields.io/badge/Android-USB%20(MTP)-2FBF71?style=for-the-badge&logo=android&logoColor=white">
  <img alt="MIT License" src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge">
</p>

<p align="center">
  <a href="https://abdani.github.io/Android-Media-Separator/"><b>🌐 Homepage</b></a> ·
  <a href="../../releases/latest/download/android_media_separator.py"><b>⬇ Download</b></a> ·
  one Python file · no packages to install
</p>

![Main window](docs/images/main.png)

## Features

| Feature | Details |
| --- | --- |
| **Two sources** | A folder on your PC, or an Android phone over USB (MTP) directly. A phone has no drive letter, so the app reaches it through the Windows Shell, the same way Explorer does. |
| **Categories** | Photos, Videos, Audio, Documents, Archives, Code and Other, with 145 known file extensions (RAW/HEIC photos, Office and OpenDocument files, e-books, …). |
| **Android subfolders** | Recognises where a file came from by its name and folder: Camera, Screenshots, Screen Recordings, WhatsApp, Telegram, Instagram and call/voice Recordings. `IMG-20260901-WA0004.jpg` goes to `Images\WhatsApp`, `Screenshot_….png` to `Images\Screenshots`. |
| **Move or copy** | Move to clean up, or copy to leave the source untouched. From a phone, a move deletes each file on the phone only after it has arrived on the PC. |
| **Preview / dry run** | Shows where every file will go before anything is touched. |
| **Name clashes** | Never overwrites by default: `photo.jpg` becomes `photo (1).jpg`. You can choose *skip* or *overwrite* instead. |
| **Duplicate finder** | Compares size, then the first 64 KB, then a full SHA-256 hash, so only truly identical files match. The oldest copy stays; the others move to a `Duplicates` folder. Nothing is deleted. |
| **Protects app data** | WhatsApp backups and databases, encrypted `.crypt` backups, `.db` files and `.nomedia` markers are never moved, so chats can still be restored. Moving WhatsApp media shows a warning and offers to copy instead. |
| **Skips system folders** | `Android/data`, `Android/obb` and hidden folders (`.thumbnails`, …) are left out of the scan. |
| **Filters and search** | Category chips, name search, extensions, size range and date range. Sort by any column. |
| **Exclusions** | Right-click to exclude a file or a whole folder. Exclusions are remembered between runs. |
| **Log** | Every action is written to `_AndroidMediaSeparator_Logs.csv` as it happens, so the log survives even if the PC crashes mid-run. |
| **Stop at any time** | Cancel a long run; files already done stay done. A phone that drops off USB is retried, then reported. |
| **English or Indonesian** | English by default; switch to Bahasa Indonesia under **⚙ Options → 🌐 Language / Bahasa**. |

## Screenshots

| Start | Filter by category |
| --- | --- |
| ![Start screen](docs/images/start.png) | ![Photos only](docs/images/filter-images.png) |

| Preview (dry run) | Duplicates |
| --- | --- |
| ![Preview](docs/images/preview.png) | ![Duplicates](docs/images/duplicates.png) |

<details>
<summary>Bahasa Indonesia</summary>

![Main window in Indonesian](docs/images/main-id.png)

</details>

## Result

The category folders are created inside the source folder, or inside the PC folder you pick when the source is a phone:

```
Phone Backup\
├─ Images\
│  ├─ Camera\
│  ├─ Screenshots\
│  ├─ Telegram\
│  └─ WhatsApp\
├─ Videos\
│  ├─ Camera\
│  ├─ Screen Recordings\
│  └─ WhatsApp\
├─ Audio\
│  ├─ Recordings\
│  └─ WhatsApp\
├─ Documents\
├─ Archives\
├─ Code\
├─ Other\
├─ Duplicates\
└─ _AndroidMediaSeparator_Logs.csv
```

Turn off **⚙ Options → Android subfolders** to get only the category folders.

## Usage

You need Windows 10 or 11 and [Python](https://www.python.org/downloads/) (tested on 3.12). Tkinter comes with the standard Windows installer, so there is nothing else to install.

```powershell
pythonw android_media_separator.py   # start the app (no console window)
python android_media_separator.py --self-test
```

**From a PC folder**

1. Click **PC Folder** and choose the folder.
2. Check the table, then press **Preview** to see where each file will go.
3. Choose **Move** or **Copy** and press **Organize all**.

**From a phone**

1. Connect the phone with a USB cable and choose **File transfer** on the phone.
2. Click **Phone / OTG** and pick the phone's storage (e.g. *Internal shared storage*).
3. Pick the PC folder to save into, then continue as above. Keep the phone's screen on while it is being read.

To organize only some files, select them in the table (<kbd>Ctrl</kbd>/<kbd>Shift</kbd>+click) and right-click → **Organize selected**.

| Shortcut | Action |
| --- | --- |
| <kbd>Ctrl</kbd>+<kbd>O</kbd> | Choose a PC folder |
| <kbd>F5</kbd> | Scan again |
| <kbd>Ctrl</kbd>+<kbd>F</kbd> | Search |
| <kbd>Ctrl</kbd>+<kbd>A</kbd> | Select all rows |
| Double-click | Show the file in Explorer |

## Settings and files

- **⚙ Options**: what to do when a name exists, include subfolders, skip system folders, Android subfolders, protect app data, manual exclusions, the log and the language.
- **Language** and **exclusions** are saved in `%APPDATA%\AndroidMediaSeparator\` (`settings.json`, `exclusions.json`). Set `AMS_CONFIG_DIR` to keep them elsewhere. A language change applies the next time the app starts.
- **Phone imports** pass through a temporary `.ams_staging` folder inside the destination, which is cleaned up after the run. A file that did not arrive completely stays there and is reported.

## Platform support

| Platform | Status |
| --- | --- |
| Windows 10 / 11 | Supported |
| Linux | Not yet. The sorting engine passes its self-test on Ubuntu 24.04, but phone access (MTP), *show in folder* and *open log* use Windows-only APIs. |
| macOS | Untested |

## Built with

| Component | Purpose | License |
| --- | --- | --- |
| [Python](https://www.python.org) + Tkinter ([Tcl/Tk](https://www.tcl-lang.org)) | The app and its interface (standard library only) | PSF-2.0, Tcl/Tk license (BSD-style) |
| Windows Shell (`Shell.Application`, `CopyHere` / `MoveHere`) | Reading an Android phone over USB (MTP) and copying or moving its files, the same way Explorer does | Windows API |
| Windows PowerShell 5.1 | Runs the Shell bridge that talks to the phone (comes with Windows) | Part of Windows 10/11 (Microsoft) |
| `hashlib` SHA-256 (Python standard library) | Duplicate finder: matches only truly identical files | PSF-2.0 |

No third-party packages: everything above comes with Python or with Windows, so there is nothing to install.

## License

[MIT](LICENSE) © 2026 Dani Abdani
