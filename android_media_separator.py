from __future__ import annotations

import base64
import csv
import hashlib
import heapq
import itertools
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import NamedTuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont


VERSION = "1.1.0"
APP_TITLE = f"Android Media Separator {VERSION}"
CATEGORY_DIRS = ("Images", "Videos", "Audio", "Documents", "Archives", "Code", "Other")
CATEGORY_LABELS = {"Images": "Foto", "Videos": "Video", "Audio": "Audio", "Documents": "Dokumen",
                   "Archives": "Arsip", "Code": "Kode", "Other": "Lainnya"}
DUPLICATES_DIR = "Duplicates"
STAGING_DIR = ".ams_staging"
# Folders this app creates; they are never scanned as source material.
OWNED_DIRS = set(CATEGORY_DIRS) | {DUPLICATES_DIR, STAGING_DIR}
LOG_NAME = "_AndroidMediaSeparator_Logs.csv"
SEP = "\x1f"  # joins path parts sent to the Shell bridge; can't occur in file names
# Window icon: the Donat donut with an Android-green glaze, as PNG (Tk 8.6 reads it natively) so no asset ships.
ICON_PNG = {
    32: "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",
    64: "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",
}

IMAGE_EXT = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff",
    ".heic", ".heif", ".avif", ".raw", ".cr2", ".cr3", ".nef", ".nrw",
    ".arw", ".dng", ".orf", ".rw2", ".raf", ".psd", ".xcf"
}
VIDEO_EXT = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".3gp", ".3g2",
    ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".f4v", ".vob", ".ogv"
}
AUDIO_EXT = {
    ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma",
    ".aiff", ".aif", ".alac", ".amr", ".mid", ".midi", ".mka"
}
DOCUMENT_EXT = {
    ".pdf", ".txt", ".rtf", ".md", ".markdown", ".tex", ".log",
    ".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm",
    ".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".xltx", ".xltm",
    ".csv", ".tsv",
    ".ppt", ".pptx", ".pptm", ".pps", ".ppsx", ".ppsm", ".pot", ".potx",
    ".odt", ".ott", ".ods", ".ots", ".odp", ".otp",
    ".pages", ".numbers", ".key", ".epub", ".mobi", ".azw", ".azw3",
    ".html", ".htm", ".xml", ".json", ".yaml", ".yml"
}
ARCHIVE_EXT = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2",
    ".iso", ".img", ".cab", ".arj"
}
CODE_EXT = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".sass",
    ".less", ".php", ".java", ".kt", ".kts", ".c", ".h", ".cpp", ".hpp",
    ".cs", ".go", ".rs", ".rb", ".swift", ".sh", ".bat", ".cmd", ".ps1",
    ".sql", ".vue", ".svelte"
}

EXTENSION_GROUPS = {
    "Images": IMAGE_EXT,
    "Videos": VIDEO_EXT,
    "Audio": AUDIO_EXT,
    "Documents": DOCUMENT_EXT,
    "Archives": ARCHIVE_EXT,
    "Code": CODE_EXT,
}

# (subfolder, pattern on the path relative to source, categories it applies to).
# First match wins, so the specific names come before the generic camera rule.
ANDROID_RULES = [
    (name, re.compile(pattern, re.I), cats) for name, pattern, cats in (
        ("Screen Recordings", r"screen[ _-]?record", {"Videos"}),
        ("Screenshots", r"screenshot", {"Images"}),
        ("WhatsApp", r"whatsapp|-WA\d{4}", None),
        ("Telegram", r"telegram", None),
        ("Instagram", r"instagram", None),
        ("Recordings", r"call[ _-]?rec|recording|voice[ _-]?rec|(^|/)(call|sounds)/", {"Audio"}),
        ("Camera", r"dcim/camera|(^|/)((IMG|VID|PXL|MVIMG)_)?\d{8}_\d{6}", {"Images", "Videos"}),
    )
]

PARTIAL_HASH_BYTES = 64 * 1024
JUNK_DIR = re.compile(r"(^|/)Android/(data|obb)$", re.I)  # keep in sync with $junk in PS_BRIDGE


class Entry(NamedTuple):
    path: Path          # PurePosixPath for files on a phone (MTP)
    size: int
    mtime: float
    category: str
    sub: str            # Android subfolder ("" if none)
    protected: str = ""  # why apps need this file to stay put ("" = safe to organize)


# Files apps need where they are: moving them off a phone loses app data (a WhatsApp
# chat backup can no longer be restored, a database breaks its app). Matched against
# the path relative to the source, so they're caught in any folder.
PROTECTED_RULES = [(reason, re.compile(pattern, re.I)) for reason, pattern in (
    ("backup/database WhatsApp", r"(^|/)WhatsApp( Business)?/(Databases|Backups)/"),
    ("backup terenkripsi aplikasi", r"\.m?crypt\d*$"),             # msgstore….db.crypt14
    ("database aplikasi", r"\.db(-wal|-shm|-journal)?$"),           # wa.db, *.db-wal
    ("penanda sistem Android", r"(^|/)\.nomedia$"),
)]
# Media WhatsApp shows inside chats; moving it leaves blurry/missing media there.
WHATSAPP_MEDIA = re.compile(r"(^|/)(Android/media/com\.whatsapp(\.w4b)?|WhatsApp( Business)?/Media)/", re.I)


def protection_reason(rel_posix: str) -> str:
    return next((reason for reason, rule in PROTECTED_RULES if rule.search(rel_posix)), "")


CONFIG_DIR = Path(os.environ.get("AMS_CONFIG_DIR")
                  or Path(os.environ.get("APPDATA") or Path.home()) / "AndroidMediaSeparator")
SETTINGS_PATH = CONFIG_DIR / "settings.json"


def load_settings() -> dict:
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=1), encoding="utf-8")


# ── language ─────────────────────────────────────────────────────────────
# The UI was written in Indonesian; those strings are the keys and EN holds the English.
LANGS = ("English", "Indonesia")
LANG_NAMES = {"English": "English", "Indonesia": "Bahasa Indonesia"}
LANG = "English"  # set from settings.json in App.__init__, before any UI is built
EN = {
    # categories, table, protection reasons
    "Semua": "All", "Foto": "Photos", "Video": "Videos", "Audio": "Audio", "Dokumen": "Documents",
    "Arsip": "Archives", "Kode": "Code", "Lainnya": "Other",
    "Nama": "Name", "Tujuan": "Destination", "Ukuran": "Size", "Diubah": "Modified",
    "backup/database WhatsApp": "WhatsApp backup/database", "backup terenkripsi aplikasi": "encrypted app backup",
    "database aplikasi": "app database", "penanda sistem Android": "Android system marker", "dikecualikan": "excluded",
    # main window
    "Pilih folder di PC atau hubungkan HP untuk mulai.": "Choose a folder on the PC or connect a phone to start.",
    "📁 Folder PC": "📁 PC Folder", "📱 HP / OTG": "📱 Phone / OTG", "Simpan ke PC:": "Save to PC:", "Ubah…": "Change…",
    "⚙ Opsi ▾": "⚙ Options ▾", "Cari nama file…": "Search file names…",
    "Ekstensi": "Extensions", "Dari": "From", "Sampai": "To",
    "mis. .jpg,.pdf · tanggal YYYY-MM-DD": "e.g. .jpg,.pdf · dates as YYYY-MM-DD",
    "Cari duplikat": "Find duplicates", "Pindahkan": "Move", "Salin": "Copy",
    "⚡ Pisahkan {} dipilih": "⚡ Organize {} selected", "⚡ Pisahkan semua ({})": "⚡ Organize all ({})",
    "Pisahkan yang dipilih": "Organize selected", "Buka lokasi file": "Show file location", "Salin path": "Copy path",
    "🔒 Kecualikan file yang dipilih": "🔒 Exclude selected files",
    "🔒 Kecualikan seluruh folder ini": "🔒 Exclude this whole folder", "Batalkan pengecualian": "Remove exclusion",
    "📁 Pilih folder PC": "📁 Choose PC folder", "📱 Hubungkan HP": "📱 Connect phone", "Reset filter": "Reset filters",
    "Tidak ada file yang cocok": "No matching files",
    "Coba kategori lain, kata kunci lain, atau reset filter.": "Try another category or search term, or reset the filters.",
    "Tidak ada file di sini": "No files here",
    "Folder ini kosong atau semua file sudah dipisahkan.\n"
    "Aktifkan “Sertakan subfolder” di ⚙ Opsi untuk ikut membaca subfolder.":
        "This folder is empty, or everything in it has been organized.\n"
        "Turn on “Include subfolders” in ⚙ Options to read subfolders too.",
    "Mulai dengan memilih sumber file": "Start by choosing where your files are",
    "Pilih folder di PC, atau hubungkan HP Android lewat kabel USB/OTG.\n"
    "Ctrl+O pilih folder  ·  F5 scan ulang  ·  Ctrl+F cari":
        "Choose a folder on the PC, or connect an Android phone with a USB/OTG cable.\n"
        "Ctrl+O choose folder  ·  F5 rescan  ·  Ctrl+F search",
    "{} file · {}": "{} files · {}", "tampil {} ({})": "showing {} ({})",
    "🔒 {} dilindungi/dikecualikan, tidak akan diproses": "🔒 {} protected/excluded, will not be processed",
    # options menu
    "Jika nama file sudah ada:": "If the file name already exists:",
    "Buat nama baru": "Create a new name", "Lewati": "Skip", "Timpa": "Overwrite",
    "Sertakan subfolder": "Include subfolders",
    "Lewati folder sistem & tersembunyi (Android/data, .thumbnails, …)":
        "Skip system & hidden folders (Android/data, .thumbnails, …)",
    "Subfolder Android (WhatsApp, Kamera, Screenshot…)": "Android subfolders (WhatsApp, Camera, Screenshots…)",
    "Kecualikan folder…": "Exclude folders…",
    "🔒 Lindungi data aplikasi (backup WhatsApp, database, .nomedia)":
        "🔒 Protect app data (WhatsApp backups, databases, .nomedia)",
    "Hapus semua pengecualian manual…": "Clear all manual exclusions…", "Buka log": "Open log",
    # status line
    "Tunggu proses selesai dulu — koneksi HP sedang dipakai.":
        "Wait for the current task to finish — the phone connection is in use.",
    "Membuka lokasi {}…": "Opening the location of {}…", "Lokasi {} dibuka di Explorer.": "{} shown in Explorer.",
    "Folder {} dikecualikan (tersimpan).": "Folder {} excluded (saved).",
    "{} file dikecualikan (tersimpan).": "{} file(s) excluded (saved).",
    "Pengecualian dihapus untuk {} file.": "Exclusion removed for {} file(s).",
    "Dihentikan.": "Stopped.", "Terjadi error.": "An error occurred.", "Dihentikan paksa.": "Force-stopped.",
    "Menghentikan setelah file ini…  (klik Stop lagi untuk paksa)":
        "Stopping after this file…  (click Stop again to force)",
    "Membaca HP… {} file  ·  {}": "Reading phone… {} files  ·  {}", "Membaca folder… {} file": "Reading folder… {} files",
    "Membaca HP… (biarkan layar HP tetap menyala)": "Reading phone… (keep the phone's screen on)",
    "Membaca folder…": "Reading folder…", "Menyiapkan preview…": "Preparing preview…", "Memproses…": "Processing…",
    "{}/{}  ·  berhasil {}  ·  dilewati {}  ·  gagal {}": "{}/{}  ·  done {}  ·  skipped {}  ·  failed {}",
    "Menunggu & memeriksa transfer yang tiba terlambat…": "Waiting for and checking late transfers…",
    "Berhasil {}  ·  dilewati {}  ·  gagal {}": "Done {}  ·  skipped {}  ·  failed {}",
    "Dihentikan — ": "Stopped — ", "Selesai — ": "Finished — ",
    "Mencari duplikat — {} {}/{}": "Finding duplicates — {} {}/{}", "cek awal file": "checking file starts",
    "hash penuh": "full hash", "Mencari duplikat…": "Finding duplicates…",
    "Pencarian duplikat dihentikan.": "Duplicate search stopped.", "Tidak ada duplikat — ": "No duplicates — ",
    "{} duplikat dalam {} grup.": "{} duplicate(s) in {} group(s).",
    # filters
    "{} harus berupa angka.": "{} must be a number.", "{} tidak boleh negatif.": "{} cannot be negative.",
    "Min MB tidak boleh lebih besar dari Max MB.": "Min MB cannot be larger than Max MB.",
    "{} harus YYYY-MM-DD.": "{} must be YYYY-MM-DD.", "Tanggal Dari": "From date", "Tanggal Sampai": "To date",
    "Tanggal Dari tidak boleh lebih besar dari Tanggal Sampai.": "The From date cannot be after the To date.",
    # dialogs
    "Pilih folder sumber": "Choose the source folder",
    "belum dipilih — ditanyakan saat memisahkan": "not chosen yet — asked when organizing",
    "Pilih folder di PC untuk menyimpan file dari HP": "Choose a PC folder for the phone's files",
    'Klik "Folder PC" atau "HP / OTG" untuk memilih sumber file.':
        'Click "PC Folder" or "Phone / OTG" to choose where your files are.',
    "Folder tidak valid": "Invalid folder", "Folder tidak ditemukan:\n{}": "Folder not found:\n{}",
    "Pengecualian": "Exclusions", "Belum ada file atau folder yang dikecualikan.": "No files or folders are excluded yet.",
    "Hapus semua pengecualian": "Clear all exclusions",
    "Hapus {} pengecualian? File-file itu akan ikut diproses lagi (data aplikasi yang dilindungi tetap aman).":
        "Clear {} exclusion(s)? Those files will be processed again (protected app data stays safe).",
    "Kecualikan folder": "Exclude folders",
    "Untuk HP, pilih langsung folder yang ingin dibaca lewat 📱 HP / OTG.":
        "For a phone, choose the folder to read directly with 📱 Phone / OTG.",
    "Tidak ada yang diproses": "Nothing to process",
    "Semua {} file ini dilindungi atau dikecualikan.": "All {} of these files are protected or excluded.",
    "Konfirmasi": "Confirm", "buat nama baru": "create a new name", "lewati": "skip", "timpa": "overwrite",
    "aktif": "on", "nonaktif": "off",
    "MEMINDAHKAN {} file dari HP ke folder kategori di:\n{}":
        "MOVING {} file(s) from the phone into category folders in:\n{}",
    "MENYALIN {} file dari HP ke folder kategori di:\n{}":
        "COPYING {} file(s) from the phone into category folders in:\n{}",
    "(file di HP akan dihapus setelah tersalin)": "(the files on the phone are deleted once copied)",
    "MEMINDAHKAN {} file ke folder kategori di:\n{}": "MOVING {} file(s) into category folders in:\n{}",
    "MENYALIN {} file ke folder kategori di:\n{}": "COPYING {} file(s) into category folders in:\n{}",
    "Jika nama sudah ada: {}.": "If a name already exists: {}.", "Subfolder Android: {}.": "Android subfolders: {}.",
    "🔒 {} file dilindungi/dikecualikan tidak akan disentuh.":
        "🔒 {} protected/excluded file(s) will not be touched.",
    "Klik Preview untuk memeriksa tujuan setiap file lebih dulu.": "Click Preview to check where each file goes first.",
    "Media WhatsApp": "WhatsApp media",
    "{} file adalah media WhatsApp. Kalau dipindahkan, foto/video/dokumen itu "
    "akan tampil buram atau hilang di dalam chat WhatsApp.\n\n"
    "Ya — ganti ke SALIN (disarankan, HP tidak berubah)\n"
    "Tidak — tetap PINDAHKAN\n"
    "Batal — jangan lakukan apa pun":
        "{} file(s) are WhatsApp media. If they are moved, those photos/videos/documents "
        "show up blurry or missing inside WhatsApp chats.\n\n"
        "Yes — switch to COPY (recommended, the phone stays unchanged)\n"
        "No — MOVE anyway\n"
        "Cancel — do nothing",
    "Berhasil: {}\nDilewati: {}\nGagal: {}\n\nLog: {}": "Succeeded: {}\nSkipped: {}\nFailed: {}\n\nLog: {}",
    "Yang gagal:": "Failed files:", "… dan {} lainnya (lihat log)": "… and {} more (see the log)",
    "File yang gagal masih ada di HP — scan ulang lalu jalankan lagi untuk mencobanya.":
        "The failed files are still on the phone — rescan and run again to retry them.",
    "⚠ {} file tertahan di folder staging (sudah tersalin, belum dipindah ke kategori):\n{}":
        "⚠ {} file(s) are stuck in the staging folder (copied, not yet moved into a category):\n{}",
    "Proses dihentikan otomatis": "Stopped automatically", "Operasi dihentikan": "Stopped",
    "Operasi dihentikan dengan aman.": "The run was stopped safely.",
    "Selesai dengan masalah": "Finished with problems", "Operasi selesai, tapi ada yang gagal.": "Finished, but some files failed.",
    "Selesai": "Done", "Operasi selesai.": "Finished.",
    "Mencari duplikat perlu membaca isi setiap file — terlalu lambat lewat kabel MTP.\n\n"
    "Salin file dari HP ke PC dulu, lalu buka folder tujuan lewat 📁 Folder PC dan cari duplikat di sana.":
        "Finding duplicates means reading every file — far too slow over an MTP cable.\n\n"
        "Copy the files from the phone to the PC first, then open that folder with 📁 PC Folder "
        "and look for duplicates there.",
    "Tidak ada duplikat": "No duplicates", "Semua file yang tampil di tabel unik.": "Every file shown in the table is unique.",
    "Memindahkan {} file duplikat ke:\n{}\n\nFile yang disimpan tetap di tempatnya. Tidak ada file yang dihapus.":
        "Move {} duplicate file(s) to:\n{}\n\nThe files that are kept stay where they are. Nothing is deleted.",
    "Log belum ada": "No log yet",
    "Log dibuat setelah file dipindahkan atau disalin.": "A log is created once files have been moved or copied.",
    # preview, duplicates, exclude-folders and phone windows
    "Preview — {} file → {}": "Preview — {} file(s) → {}", "{} akan diberi nama baru": "{} will get a new name",
    "Aksi": "Action", "Sumber": "Source", "Ke": "To", "Tutup": "Close",
    "Duplikat Ditemukan": "Duplicates Found",
    "{} file duplikat dalam {} grup  ·  bisa hemat {}": "{} duplicate file(s) in {} group(s)  ·  {} can be freed",
    "Isi file identik byte-per-byte (SHA-256). File tertua di tiap grup disimpan, "
    "sisanya dipindah ke folder {}\\ — tidak ada yang dihapus. Klik dua kali untuk membuka lokasi file.":
        "Identical byte for byte (SHA-256). The oldest file in each group is kept; the others move to the "
        "{}\\ folder — nothing is deleted. Double-click to show a file's location.",
    "Lokasi": "Location", "Grup {} — {} file identik": "Group {} — {} identical files",
    "Simpan": "Keep", "Duplikat": "Duplicate", "Pindahkan {} duplikat ke {}\\": "Move {} duplicate(s) to {}\\",
    "Kecualikan Folder": "Exclude Folders",
    "Pilih folder yang tidak boleh diproses.": "Choose the folders that must not be processed.",
    "Folder buatan aplikasi (Images, Videos, Duplicates, dll.) selalu dikecualikan.":
        "Folders the app creates (Images, Videos, Duplicates, …) are always excluded.",
    "Pilih Semua": "Select All", "Batal Pilihan": "Clear Selection", "Terapkan": "Apply",
    "Pilih Folder di HP": "Choose a Folder on the Phone", "Pilih folder di HP": "Choose a folder on the phone",
    "⟳ Muat ulang": "⟳ Reload", "Pilih folder ini": "Choose this folder", "Batal": "Cancel",
    "Mencari perangkat…": "Looking for devices…", "Memuat…": "Loading…",
    "Buka perangkat lalu pilih folder, misalnya DCIM atau Android/media/com.whatsapp. Subfolder ikut dibaca.":
        "Open a device, then choose a folder, e.g. DCIM or Android/media/com.whatsapp. Subfolders are read too.",
    "Tidak ada HP terdeteksi. Hubungkan HP dengan kabel USB/OTG, buka kunci layar, lalu pilih mode USB "
    "“Transfer file / MTP”. Setelah itu klik Muat ulang.\n\nFlashdisk OTG atau HP mode penyimpanan punya "
    "huruf drive — pilih lewat 📁 Folder PC.":
        "No phone found. Connect it with a USB/OTG cable, unlock the screen and choose the USB mode "
        "“File transfer / MTP”. Then click Reload.\n\nAn OTG flash drive or a phone in storage mode has "
        "a drive letter — choose it with 📁 PC Folder.",
    # errors from file operations and the phone connection
    "Terlalu banyak nama file sama: {}": "Too many files with the same name: {}",
    "Lokasi file tidak ditemukan:\n{}": "File location not found:\n{}",
    "Explorer tidak bisa membuka lokasi:\n{}": "Explorer could not open the location:\n{}",
    "Sumber tidak ditemukan.": "Source not found.",
    "HP/Windows tidak merespons {} detik — koneksi dimulai ulang.":
        "The phone/Windows did not respond for {} s — the connection was restarted.",
    "Koneksi ke Windows Shell terputus.": "The connection to the Windows Shell was lost.",
    "dibatalkan: lebih dari {} detik belum selesai": "cancelled: not finished after {} s",
    "tidak ada aktivitas transfer selama {} detik": "no transfer activity for {} s",
    "ukuran dilaporkan HP {} B, diterima {} B": "phone reported {} B, received {} B",
    "tersalin tidak lengkap ({} dari {} B)": "copied incompletely ({} of {} B)",
    "HP tidak merespons lagi setelah {} file berturut-turut gagal, jadi proses dihentikan otomatis.\n\n"
    "Cabut-colok kabel, buka kunci layar HP, pilih “Transfer file”, lalu scan ulang dan jalankan lagi. "
    "File yang sudah berhasil tidak akan diproses ulang; file yang gagal masih ada di HP.":
        "The phone stopped responding after {} files in a row failed, so the run was stopped automatically.\n\n"
        "Unplug and replug the cable, unlock the phone, choose “File transfer”, then rescan and run again. "
        "Files that already succeeded are not processed again; the failed ones are still on the phone.",
    "dipulihkan: tiba setelah percobaannya dianggap gagal": "recovered: arrived after its attempt was written off",
    # sent by PS_BRIDGE (see bridge_message)
    "Tidak ditemukan: {}": "Not found: {}", "Folder staging tidak ada: {}": "Staging folder missing: {}",
    "File tidak mulai tersalin dalam {} detik: {}": "File did not start copying within {} s: {}",
    "Penyalinan macet: {}": "Copy stalled: {}",
    "Explorer tidak membuka folder HP dalam 15 detik.": "Explorer did not open the phone folder within 15 seconds.",
    "Perintah tidak dikenal: {}": "Unknown command: {}",
}
# Messages the PowerShell bridge writes (Indonesian, with {} for the variable part).
BRIDGE_MESSAGES = ("Tidak ditemukan: {}", "Folder staging tidak ada: {}", "File tidak mulai tersalin dalam {} detik: {}",
                   "Penyalinan macet: {}", "Explorer tidak membuka folder HP dalam 15 detik.", "Perintah tidak dikenal: {}")


def T(s: str, *args) -> str:
    """UI text in the chosen language; args fill the {} slots."""
    s = EN.get(s, s) if LANG == "English" else s
    return s.format(*args) if args else s


def bridge_message(text: str) -> str:
    """A bridge error in the UI language when it's one of ours; Windows' own text as is."""
    for template in BRIDGE_MESSAGES:
        m = re.fullmatch(re.escape(template).replace(r"\{\}", "(.*)"), text, re.S)
        if m:
            return T(template, *m.groups())
    return text


class Exclusions:
    """Files and folders the user chose never to process. Saved between runs (JSON)."""

    def __init__(self, path: Path):
        self.path = path
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        self.files: set[str] = set(data.get("files", []))
        self.folders: set[str] = set(data.get("folders", []))

    def __len__(self):
        return len(self.files) + len(self.folders)

    def match(self, path) -> bool:
        s = str(path)
        # Phone paths use "/", PC paths "\"; a folder covers everything below it.
        return s in self.files or any(s.startswith(f + "/") or s.startswith(f + "\\") for f in self.folders)

    def add_files(self, paths):
        self.files.update(str(p) for p in paths)
        self.save()

    def add_folder(self, folder):
        self.folders.add(str(folder).rstrip("/\\"))
        self.save()

    def remove(self, paths):
        """Un-exclude these files, including any excluded folder that contains them."""
        for p in paths:
            s = str(p)
            self.files.discard(s)
            self.folders -= {f for f in self.folders if s.startswith(f + "/") or s.startswith(f + "\\")}
        self.save()

    def clear(self):
        self.files.clear()
        self.folders.clear()
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"files": sorted(self.files), "folders": sorted(self.folders)},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)  # atomic: a crash mid-write never leaves a broken list


def classify(path) -> str:
    ext = path.suffix.lower()
    for category, extensions in EXTENSION_GROUPS.items():
        if ext in extensions:
            return category
    return "Other"


def rel_path(path, source) -> str:
    """Path relative to source. String slicing: Path.relative_to is ~20x slower per call."""
    s, root = str(path), str(source)
    return s[len(root):].lstrip("\\/") if s.startswith(root) else s


def android_subfolder(path, source, category: str) -> str:
    rel = rel_path(path, source).replace("\\", "/")
    for name, rule, cats in ANDROID_RULES:
        if (cats is None or category in cats) and rule.search(rel):
            return name
    return ""


def destination_label(path, source, android: bool) -> str:
    """'Images' or, with Android subfolders on, e.g. 'Images/WhatsApp'."""
    category = classify(path)
    sub = android_subfolder(path, source, category) if android else ""
    return f"{category}/{sub}" if sub else category


def make_entry(path, size: int, mtime: float, source) -> Entry:
    category = classify(path)
    return Entry(path, size, mtime, category, android_subfolder(path, source, category),
                 protection_reason(rel_path(path, source).replace("\\", "/")))


def entry_label(e: Entry, android: bool) -> str:
    return f"{e.category}/{e.sub}" if android and e.sub else e.category


def human_size(n: int) -> str:
    value = float(max(0, n))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value):,} B"
            return f"{value:,.1f} {unit}"
        value /= 1024
    return "0 B"


def fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts > 0 else "—"


def unique_destination(folder: Path, filename: str, reserved: set[Path] | None = None) -> Path:
    reserved = reserved or set()
    target = folder / filename
    if not target.exists() and target not in reserved:
        return target

    p = Path(filename)
    for n in range(1, 1_000_000):
        target = folder / f"{p.stem} ({n}){p.suffix}"
        if not target.exists() and target not in reserved:
            return target
    raise RuntimeError(T("Terlalu banyak nama file sama: {}", filename))


def normalized_path(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def parse_extensions(raw: str) -> set[str]:
    """Parse '.jpg, jpeg; PNG' into normalized suffixes."""
    result = set()
    for token in raw.replace(";", ",").split(","):
        token = token.strip().lower()
        if not token:
            continue
        if not token.startswith("."):
            token = "." + token
        result.add(token)
    return result


def parse_excluded_paths(raw: str, source: Path) -> list[Path]:
    """Parse newline/semicolon/comma separated relative folder names."""
    result = []
    for token in raw.replace(";", "\n").splitlines():
        token = token.strip().strip('"')
        if not token:
            continue
        p = Path(token)
        if p.is_absolute():
            result.append(normalized_path(p))
        else:
            result.append(normalized_path(source / p))
    return result


def is_junk_dir(name: str, rel_posix: str) -> bool:
    """Hidden folders (.thumbnails, .trashBin, …) and app-private Android/data, Android/obb.
    Skipping them is faster and keeps app data from being moved off a phone.
    Android/media (WhatsApp lives there) is kept."""
    return name.startswith(".") or bool(JUNK_DIR.search(rel_posix))


def discover_files(source: Path, include_subfolders: bool, script_name: str,
                   excluded_dirs: list[Path], progress_callback=None,
                   skip_junk: bool = False) -> list[Entry]:
    """
    Walk with os.scandir: on Windows the size/mtime come with the directory
    listing (no extra stat per file), and excluded/owned folders are pruned
    instead of being walked and filtered file by file.
    """
    excluded = set(excluded_dirs)
    found: list[Entry] = []
    stack = [source]

    while stack:
        folder = stack.pop()
        try:
            with os.scandir(folder) as it:
                for d in it:
                    try:
                        if d.is_dir(follow_symlinks=False):
                            if (include_subfolders
                                    and not (folder == source and d.name in OWNED_DIRS)
                                    and not (skip_junk and is_junk_dir(
                                        d.name, rel_path(d.path, source).replace("\\", "/")))
                                    and normalized_path(Path(d.path)) not in excluded):
                                stack.append(Path(d.path))
                        elif d.is_file() and d.name not in (script_name, LOG_NAME):
                            st = d.stat()
                            found.append(make_entry(Path(d.path), st.st_size, st.st_mtime, source))
                    except OSError:
                        continue
        except OSError:
            continue
        if progress_callback:
            progress_callback(len(found), None)

    return found


def filter_files(entries: list[Entry], min_mb: float | None, max_mb: float | None,
                 date_from, date_to, extensions: set[str],
                 category: str = "", query: str = "") -> list[Entry]:
    query = query.strip().casefold()
    result = []
    for e in entries:
        if category and e.category != category:
            continue
        size_mb = e.size / (1024 * 1024)
        if min_mb is not None and size_mb < min_mb:
            continue
        if max_mb is not None and size_mb > max_mb:
            continue

        if date_from or date_to:
            modified = datetime.fromtimestamp(max(e.mtime, 0)).date()
            if date_from and modified < date_from:
                continue
            if date_to and modified > date_to:
                continue

        if extensions and e.path.suffix.lower() not in extensions:
            continue
        if query and query not in e.path.name.casefold():
            continue

        result.append(e)
    return result


def preview_operations(paths: list, source, conflict: str, android: bool = False,
                       dest_root: Path | None = None):
    """
    Simulate the exact destination decisions without changing the filesystem.
    Returns records with action, source, destination, category. Category
    folders go under dest_root (the source folder itself unless importing
    from a phone).
    """
    dest_root = dest_root or source
    records = []
    reserved: set[Path] = set()

    for src in paths:
        category = destination_label(src, source, android)
        dest_dir = dest_root / category
        target = dest_dir / src.name

        if conflict == "skip" and target.exists():
            action = "SKIP_CONFLICT"
            destination = target
        elif conflict == "overwrite" and target.exists():
            action = "OVERWRITE"
            destination = target
        elif conflict == "unique":
            destination = unique_destination(dest_dir, src.name, reserved)
            action = "MOVE" if destination.name == src.name and not target.exists() else "RENAME"
        else:
            destination = target
            action = "MOVE"

        reserved.add(destination)
        records.append({
            "source": src,
            "destination": destination,
            "category": category,
            "action": action,
        })

    return records


def file_hash(path: Path, limit: int | None = None) -> bytes | None:
    try:
        with open(path, "rb") as f:
            if limit:
                return hashlib.sha256(f.read(limit)).digest()
            h = hashlib.sha256()
            while chunk := f.read(1 << 20):
                h.update(chunk)
            return h.digest()
    except OSError:
        return None


def find_duplicates(entries: list[Entry], stop_event: threading.Event,
                    progress_callback=None) -> list[list[Entry]]:
    """
    Group byte-identical files. Size first (free), then a hash of the first
    64 KiB, then a full hash only for files that still collide, so most files
    are never read at all. Each group is sorted so the file to keep (oldest,
    then shortest path) comes first; groups are sorted by space wasted.
    """
    by_size = defaultdict(list)
    for e in entries:
        if e.size:
            by_size[e.size].append(e)
    groups = [g for g in by_size.values() if len(g) > 1]

    # ponytail: 4 reader threads suit SSDs; drop to 1 if HDD users report thrashing.
    pool = ThreadPoolExecutor(max_workers=4)
    try:
        for limit, phase in ((PARTIAL_HASH_BYTES, "cek awal file"), (None, "hash penuh")):
            # Files no bigger than the partial window were already hashed whole.
            done = [g for g in groups if limit is None and g[0].size <= PARTIAL_HASH_BYTES]
            todo = [e for g in groups if not (limit is None and g[0].size <= PARTIAL_HASH_BYTES)
                    for e in g]
            by_hash = defaultdict(list)
            for i, (e, digest) in enumerate(
                    zip(todo, pool.map(lambda e: file_hash(e.path, limit), todo)), 1):
                if stop_event.is_set():
                    return []
                if digest:
                    by_hash[(e.size, digest)].append(e)
                if progress_callback:
                    progress_callback(i, len(todo), phase)
            groups = done + [g for g in by_hash.values() if len(g) > 1]
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    for g in groups:
        g.sort(key=lambda e: (e.mtime, len(str(e.path)), str(e.path).lower()))
    groups.sort(key=lambda g: g[0].size * (len(g) - 1), reverse=True)
    return groups


def duplicate_records(groups: list[list[Entry]], source: Path):
    """Records that move every copy except the first of each group to Duplicates/."""
    dest_dir = source / DUPLICATES_DIR
    reserved: set[Path] = set()
    records = []
    for g in groups:
        for e in g[1:]:
            destination = unique_destination(dest_dir, e.path.name, reserved)
            reserved.add(destination)
            records.append({"source": e.path, "destination": destination,
                            "category": DUPLICATES_DIR, "action": "MOVE"})
    return records


def throttled(fn, interval: float = 0.1):
    """Drop progress calls that arrive faster than `interval`, but never the final one."""
    last = float("-inf")  # monotonic() may start near 0 (fresh boot), so the first call always passes

    def wrapper(current, total, *rest):
        nonlocal last
        now = time.monotonic()
        if current == total or now - last >= interval:
            last = now
            fn(current, total, *rest)
    return wrapper


def reveal_in_explorer(target: str):
    """
    Open the containing folder in Explorer with the item selected. `target` is a
    normal path or a Shell parsing name (what files on a phone/MTP have), so this
    works for both. Safe to call off the UI thread.
    """
    import ctypes
    from ctypes import wintypes
    ole32, shell32 = ctypes.windll.ole32, ctypes.windll.shell32
    shell32.SHParseDisplayName.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_void_p), wintypes.ULONG, ctypes.c_void_p]
    shell32.SHOpenFolderAndSelectItems.argtypes = [ctypes.c_void_p, wintypes.UINT, ctypes.c_void_p, wintypes.DWORD]
    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    initialized = ole32.CoInitializeEx(None, 2) >= 0  # COINIT_APARTMENTTHREADED
    try:
        pidl = ctypes.c_void_p()
        if shell32.SHParseDisplayName(target, None, ctypes.byref(pidl), 0, None) < 0:
            raise OSError(T("Lokasi file tidak ditemukan:\n{}", target))
        try:
            # With no child items, the PIDL itself is the item to select in its parent folder.
            if shell32.SHOpenFolderAndSelectItems(pidl, 0, None, 0) < 0:
                raise OSError(T("Explorer tidak bisa membuka lokasi:\n{}", target))
        finally:
            ole32.CoTaskMemFree(pidl)
    finally:
        if initialized:
            ole32.CoUninitialize()


def _in_use(path: Path) -> bool:
    """True while another process (e.g. a Windows copy still writing) holds the file open:
    an exclusive open (share mode 0) then fails."""
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                     wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    handle = kernel32.CreateFileW(str(path), 0x80000000, 0, None, 3, 0x80, None)  # GENERIC_READ, OPEN_EXISTING
    if handle in (None, wintypes.HANDLE(-1).value):
        return path.exists()
    kernel32.CloseHandle(handle)
    return False


def remove_empty_dirs(root: Path):
    for folder, _, _ in os.walk(root, topdown=False):
        try:
            os.rmdir(folder)
        except OSError:
            pass


def transfer(src: Path, dest: Path, move: bool, overwrite: bool = False):
    if move:
        if overwrite:
            # shutil.move can overwrite on some platforms but behavior differs
            # for directories/filesystems. Explicitly remove the existing file first.
            dest.unlink()
        shutil.move(str(src), str(dest))
    else:
        shutil.copy2(str(src), str(dest))


def execute_operations(records, mode: str, conflict: str, stop_event: threading.Event,
                       progress_callback=None, fetch=None, on_record=None):
    """
    Execute previewed operations. Cancellation is checked between files.
    A single file is never intentionally interrupted halfway by this program.
    `fetch(record) -> Path | (Path, note)` first pulls a file off a phone into a
    local staging folder; that staged copy is then always moved into place.
    `on_record(log)` gets each log row the moment it exists (crash-safe logging).
    """
    success = skipped = failed = 0
    logs = []
    total = len(records)
    move = mode == "MOVE" or fetch is not None

    for index, record in enumerate(records, 1):
        if stop_event.is_set():
            break

        src = record["source"]
        category = record["category"]
        destination: Path = record["destination"]
        dest_dir = destination.parent

        status = "OK"
        error = ""
        final_dest = destination

        try:
            # Re-check conflicts at execution time because the filesystem
            # may have changed after preview. Skips are decided before a
            # phone file is ever copied.
            if conflict == "skip" and final_dest.exists():
                skipped += 1
                status = "SKIPPED_CONFLICT"
            else:
                local = fetch(record) if fetch else src
                if isinstance(local, tuple):  # (path, note) — e.g. size differs from what the phone reported
                    local, error = local
                if not local.is_file():
                    skipped += 1
                    status = "MISSING"
                    error = T("Sumber tidak ditemukan.")
                else:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    overwrite = final_dest.exists()
                    if overwrite and conflict != "overwrite":
                        final_dest = unique_destination(dest_dir, src.name)
                        overwrite = False
                    transfer(local, final_dest, move, overwrite)
                    success += 1

        except Exception as exc:
            failed += 1
            status = "ERROR"
            error = str(exc) or repr(exc)

        logs.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "action": mode,
            "status": status,
            "category": category,
            "source": str(src),
            "destination": str(final_dest),
            "error": error,
        })
        if on_record:
            on_record(logs[-1])

        if progress_callback:
            progress_callback(index, total, success, skipped, failed)

    cancelled = stop_event.is_set() and (success + skipped + failed) < total
    return success, skipped, failed, cancelled, logs


class LogWriter:
    """
    The CSV log, written and flushed row by row. It used to be written once at the
    end, so a crash, a closed window or a dropped USB connection lost the record of
    thousands of files that had already been moved.
    """
    FIELDS = ["time", "action", "status", "category", "source", "destination", "error"]

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        new = not path.exists() or path.stat().st_size == 0
        self.file = path.open("a", newline="", encoding="utf-8-sig")
        self.writer = csv.DictWriter(self.file, fieldnames=self.FIELDS)
        if new:
            self.writer.writeheader()
            self.file.flush()

    def write(self, record: dict):
        self.writer.writerow(record)
        self.file.flush()

    def close(self):
        self.file.close()


# Runs inside the PowerShell bridge. Protocol: one tab-separated command per
# line on stdin; zero or more "kind<TAB>data" lines back, then "end" (or "err").
PS_BRIDGE = r'''
$ErrorActionPreference = 'Stop'
$utf8 = [Text.UTF8Encoding]::new($false)
$in = [IO.StreamReader]::new([Console]::OpenStandardInput(), $utf8)
$out = [IO.StreamWriter]::new([Console]::OpenStandardOutput(), $utf8)
$out.AutoFlush = $true
$sh = New-Object -ComObject Shell.Application
$SEP = [string][char]0x1f
# Android file names are case-sensitive, so the caches are too.
$folders = [hashtable]::new([StringComparer]::Ordinal)
$items = [hashtable]::new([StringComparer]::Ordinal)

function NameOf($it) {
    # .Name hides extensions when Explorer is set to; System.FileName never does.
    if (-not $it.IsFolder) {
        try { $n = $it.ExtendedProperty('System.FileName'); if ($n) { return [string]$n } } catch {}
    }
    [string]$it.Name
}

function IsDir($it) {
    # A .zip is a shell folder on a normal disk; only real directories count there.
    $it.IsFolder -and (-not $it.IsFileSystem -or [IO.Directory]::Exists($it.Path))
}

function FindItem($folder, [string]$key, [string]$name) {
    $k = $key + $SEP + $name
    if (-not $items.ContainsKey($k)) {
        foreach ($it in $folder.Items()) { $items[$key + $SEP + (NameOf $it)] = $it }
    }
    $it = $items[$k]
    if ($null -eq $it) { throw "Tidak ditemukan: $name" }
    $it
}

function GetFolder([string[]]$parts) {
    $key = $parts -join $SEP
    $f = $folders[$key]
    if ($null -ne $f) { return $f }
    if ($parts.Count -eq 1) {
        if ([IO.Directory]::Exists($parts[0])) { $f = $sh.Namespace($parts[0]) }
        else {
            foreach ($it in $sh.Namespace(17).Items()) {
                if ($it.Name -eq $parts[0]) { $f = $it.GetFolder; break }
            }
        }
    } else {
        $parent = $parts[0..($parts.Count - 2)]
        $f = (FindItem (GetFolder $parent) ($parent -join $SEP) $parts[-1]).GetFolder
    }
    if ($null -eq $f) { throw "Tidak ditemukan: $($parts -join ' / ')" }
    $folders[$key] = $f
    $f
}

function ListDirs([string[]]$parts) {
    if ($parts.Count -eq 0) {
        # Phones/cameras sit under This PC as non-filesystem items (no drive letter).
        foreach ($it in $sh.Namespace(17).Items()) {
            if (-not $it.IsFileSystem) { $out.WriteLine("d`t" + $it.Name) }
        }
        return
    }
    $f = GetFolder $parts
    $key = $parts -join $SEP
    foreach ($it in $f.Items()) {
        if (IsDir $it) {
            $n = NameOf $it
            $items[$key + $SEP + $n] = $it
            $out.WriteLine("d`t$n")
        }
    }
}

function ListFiles([string[]]$root, [bool]$recursive, [bool]$skipJunk) {
    # Every property read is a round trip to the phone (~4 ms over MTP), so this
    # loop reads as few as possible and is inlined (PowerShell calls are slow too).
    $onDisk = [IO.Directory]::Exists($root[0])
    $junk = '(^|/)Android/(data|obb)$'  # keep in sync with JUNK_DIR in Python
    $stack = [Collections.Stack]::new()
    $stack.Push(@((GetFolder $root), ($root -join $SEP), ''))
    while ($stack.Count -gt 0) {
        $folder, $key, $rel = $stack.Pop()
        foreach ($it in $folder.Items()) {
            $isDir = $it.IsFolder
            # A .zip is a shell folder on a normal disk; only real directories count there.
            if ($isDir -and $onDisk) { $isDir = [IO.Directory]::Exists($it.Path) }
            if ($isDir) {
                $name = [string]$it.Name
            } else {
                # .Name hides extensions when Explorer is set to; System.FileName never does.
                $name = [string]$it.ExtendedProperty('System.FileName')
                if (-not $name) { $name = [string]$it.Name }
            }
            $k = $key + $SEP + $name
            $items[$k] = $it
            $r = if ($rel) { "$rel/$name" } else { $name }
            if ($isDir) {
                if ($recursive -and -not ($skipJunk -and ($name.StartsWith('.') -or $r -match $junk))) {
                    $sub = $it.GetFolder
                    $folders[$k] = $sub
                    $stack.Push(@($sub, $k, $r))
                }
            } else {
                # On MTP FolderItem.Size reads 0 and ModifyDate 1899; these two are right (date in UTC).
                $size = $it.ExtendedProperty('System.Size')
                if ($null -eq $size) { $size = 0 }
                $m = 0
                $d = $it.ExtendedProperty('System.DateModified')
                if ($d) { $m = [DateTimeOffset]::new([DateTime]::SpecifyKind($d, 'Utc')).ToUnixTimeSeconds() }
                $out.WriteLine("f`t$size`t$m`t$r")
            }
        }
    }
}

function CopyItem([string[]]$parts, [string]$dest, [bool]$move, [int64]$size, [int]$giveUp) {
    # Timing policy lives in Python (CopyWatch), which can see Windows' progress window;
    # $giveUp is only a last-resort backstop so this loop can never spin forever.
    $parent = $parts[0..($parts.Count - 2)]
    $it = FindItem (GetFolder $parent) ($parent -join $SEP) $parts[-1]
    $target = $sh.Namespace($dest)
    if ($null -eq $target) { throw "Folder staging tidak ada: $dest" }
    # 4 no progress UI | 16 yes to all | 512 no mkdir prompt | 1024 no error UI
    if ($move) { $target.MoveHere($it, 1556) } else { $target.CopyHere($it, 1556) }
    # The Shell copies asynchronously. $dest starts empty, so the copy is done
    # once its single file has the expected size (or stopped growing) and
    # nothing holds it open any more.
    $last = -1
    $started = [DateTime]::Now
    $changed = $started
    $beat = $started
    $seen = $false
    while ($true) {
        $files = [IO.Directory]::GetFiles($dest)
        if ($files.Count -ge 1) { $seen = $true }
        if (-not $seen -and ([DateTime]::Now - $started).TotalSeconds -gt $giveUp) {
            throw "File tidak mulai tersalin dalam $giveUp detik: $($parts[-1])"
        }
        if ($files.Count -eq 1) {
            $len = [IO.FileInfo]::new($files[0]).Length
            if ($len -ne $last) { $last = $len; $changed = [DateTime]::Now }
            if ($len -eq $size -or ([DateTime]::Now - $changed).TotalSeconds -gt 5) {
                try {
                    [IO.File]::Open($files[0], 'Open', 'Read', 'None').Close()
                    $out.WriteLine("p`t" + $files[0])
                    break
                } catch {}
            }
        }
        # Windows pre-allocates the full size at once (seen: 883 MB at 0.5 s) and then fills
        # it, so the length can't show progress; "done" is decided by the exclusive open above.
        if ($seen -and ([DateTime]::Now - $changed).TotalSeconds -gt $giveUp) {
            throw "Penyalinan macet: $($parts[-1])"
        }
        # Heartbeat: tells Python we're alive while a big file arrives. If the Shell call
        # above hangs instead (seen after a USB drop), no beats come and Python restarts us.
        if (([DateTime]::Now - $beat).TotalSeconds -ge 1) { $out.WriteLine('h'); $beat = [DateTime]::Now }
        Start-Sleep -Milliseconds 20
    }
    if ($move) { $items.Remove($parts -join $SEP) }
}

function FindWindow([string]$path) {
    foreach ($w in $sh.Windows()) {
        try { if ($w.Document.Folder.Self.Path -eq $path) { return $w } } catch {}
    }
    $null
}

function RevealItem([string[]]$parts) {
    # MTP parsing names ("...\SID-{..}\{object id}") can't be parsed back from outside
    # (SHParseDisplayName: E_INVALIDARG), so instead of handing Explorer a path, open the
    # live parent Folder we already hold and select the live FolderItem in that window.
    $parent = $parts[0..($parts.Count - 2)]
    $folder = GetFolder $parent
    $it = FindItem $folder ($parent -join $SEP) $parts[-1]
    $target = $folder.Self.Path
    $win = FindWindow $target  # reuse a window already showing that folder
    if ($null -eq $win) {
        $sh.Open($folder)
        for ($i = 0; $i -lt 150 -and $null -eq $win; $i++) {
            Start-Sleep -Milliseconds 100
            $win = FindWindow $target
        }
    }
    if ($null -eq $win) { throw "Explorer tidak membuka folder HP dalam 15 detik." }
    # An MTP folder view fills asynchronously: retry until our item is the selection.
    # 29 = select | deselect others | ensure visible | focus
    $name = $it.Name
    for ($i = 0; $i -lt 50; $i++) {
        try { $win.Document.SelectItem($it, 29) } catch {}
        if (@($win.Document.SelectedItems() | Where-Object { $_.Name -eq $name }).Count) { break }
        Start-Sleep -Milliseconds 100
    }
    $out.WriteLine("p`t" + $win.HWND)
}

while ($null -ne ($line = $in.ReadLine())) {
    $a = $line.Split("`t")
    try {
        $parts = [string[]]@()
        if ($a.Count -gt 1 -and $a[1]) { $parts = [string[]]$a[1].Split($SEP) }
        switch ($a[0]) {
            'dirs' { ListDirs $parts }
            'list' { ListFiles $parts ($a[2] -eq '1') ($a[3] -eq '1') }
            'copy' {
                $giveUp = 3600
                if ($a.Count -gt 5) { $giveUp = [int]$a[5] }
                CopyItem $parts $a[2] ($a[3] -eq '1') ([int64]$a[4]) $giveUp
            }
            'reveal' { RevealItem $parts }
            default { throw "Perintah tidak dikenal: $($a[0])" }
        }
        $out.WriteLine('end')
    } catch {
        $out.WriteLine("err`t" + ($_.Exception.Message -replace '\s+', ' '))
    }
}
'''


class ShellBridge:
    """
    Android phones over USB (MTP) have no drive letter, so Python's file APIs
    can't see them. Explorer reaches them through the Windows Shell; this keeps
    one PowerShell process driving that same Shell COM API and talks to it over
    stdin/stdout. No extra packages needed.
    """

    def __init__(self):
        encoded = base64.b64encode(PS_BRIDGE.encode("utf-16-le")).decode("ascii")
        self.proc = subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-EncodedCommand", encoded],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self.lock = threading.Lock()
        # stdout is read on its own thread so a call can time out: a blocking readline()
        # waited forever when a Shell MoveHere hung after a USB drop (0 % CPU, no output).
        self.lines = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()

    # Seconds with no output at all (not even a copy heartbeat) before the bridge is
    # treated as hung, killed, and replaced on the next call.
    SILENCE_LIMIT = 90

    def _pump(self):
        for line in self.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)  # EOF: the process ended or was killed

    def _call(self, *args, on_line=None, timeout=None) -> list[str]:
        timeout = timeout or self.SILENCE_LIMIT
        with self.lock:
            self.proc.stdin.write("\t".join(args) + "\n")
            self.proc.stdin.flush()
            lines = []
            while True:
                try:
                    line = self.lines.get(timeout=timeout)
                except queue.Empty:
                    self.close()
                    raise RuntimeError(T("HP/Windows tidak merespons {} detik — koneksi dimulai ulang.",
                                         f"{timeout:.0f}")) from None
                if line is None:
                    raise RuntimeError(T("Koneksi ke Windows Shell terputus."))
                kind, _, rest = line.rstrip("\r\n").partition("\t")
                if kind == "h":  # heartbeat from a copy in progress
                    continue
                if kind == "end":
                    return lines
                if kind == "err":
                    raise RuntimeError(bridge_message(rest))
                lines.append(rest)
                if on_line:
                    on_line(len(lines), rest)

    def dirs(self, parts=(), timeout=None) -> list[str]:
        """Device names for (), else the subfolder names of that folder."""
        return self._call("dirs", SEP.join(parts), timeout=timeout)

    def list_files(self, root, recursive: bool, progress=None, skip_junk: bool = True) -> list[Entry]:
        """progress(count, line) is called for every file; line ends with its relative path."""
        base = PurePosixPath(*root)
        entries = []
        for line in self._call("list", SEP.join(root), "1" if recursive else "0",
                               "1" if skip_junk else "0", on_line=progress):
            size, mtime, rel = line.split("\t", 2)
            entries.append(make_entry(base.joinpath(*rel.split("/")),
                                      int(size or 0), float(mtime or 0), base))
        return entries

    def reveal(self, path: PurePosixPath) -> int:
        """Show a phone file selected in an Explorer window; returns that window's handle."""
        return int(self._call("reveal", SEP.join(path.parts))[-1])

    # One attempt at a file is written off after this many seconds with NO sign of life:
    # no Windows progress window, no data, no finished file. Measured on a worn SD card:
    # the same 26 MB PDF took 87 s once and 6 s the next time, so a fixed total time
    # would kill slow-but-working copies; "no sign of life" doesn't.
    STALL_LIMIT = 15
    MAX_BUSY_MIN = 300  # s a copy may keep Windows busy before it is cancelled (Cancel button)

    def fetch(self, path: PurePosixPath, size: int, staging: Path, move: bool) -> Path:
        """Copy (or move) one phone file into the empty folder `staging`; returns the local file.
        Raises RuntimeError with Windows' own error text when the Shell showed one."""
        staging.mkdir(parents=True, exist_ok=True)
        # While Windows shows its progress window it is working: allow even a 0.2 MB/s
        # link (worn SD card) to finish, min. 5 minutes, then cancel it properly.
        max_busy = max(self.MAX_BUSY_MIN, size / (0.2 * 1024 * 1024))
        watch = CopyWatch(self, self.STALL_LIMIT, max_busy)
        try:
            lines = self._call("copy", SEP.join(path.parts), str(staging), "1" if move else "0",
                               str(size), str(int(max_busy + 120)),
                               timeout=max_busy + 180)  # CopyWatch decides about hangs, not silence
        except RuntimeError as exc:
            raise RuntimeError(watch.reason or str(exc)) from None
        finally:
            watch.stop()
        return Path(lines[-1])

    def close(self):
        self.closed = True
        self.proc.kill()

    closed = False


class CopyWatch:
    """
    Watches one phone copy from the outside (the bridge process can't: a failing Shell
    copy blocks it inside a modal dialog). Every 0.5 s:
      • Windows error dialogs of the bridge are read and closed (Windows has already
        given up on that transfer), so nobody has to click OK and the log gets the text;
      • Windows' own progress window ("Copying..."/"Moving...") or I/O by the bridge
        means the transfer is alive. MTP transfers can run in another Windows process
        that killing our bridge does NOT stop (seen: abandoned transfers kept the phone
        busy until even small files couldn't get through), so a live transfer is only
        ever ended with its Cancel button, after `max_busy` s;
      • no sign of life at all for `limit` s → nothing is running; end the attempt.
    """
    # Bytes that count as progress. The bridge's own wait loop makes ~6 KB/s of I/O
    # (measured), which a lower bar mistook for a live transfer; the slowest real SD-card
    # read seen (0.3 MB/s) clears this in under a second.
    MIN_PROGRESS = 256 * 1024

    def __init__(self, bridge, limit, max_busy=3600):
        import ctypes
        from ctypes import wintypes
        self.ctypes, self.wintypes = ctypes, wintypes
        self.bridge, self.limit, self.max_busy, self.reason = bridge, limit, max_busy, ""
        self.user32, self.kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        self.handle = self.kernel32.OpenProcess(0x1000, False, bridge.proc.pid)  # QUERY_LIMITED_INFORMATION
        self.enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.closed_dialogs = set()
        self.done = threading.Event()
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.done.set()
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None

    def _io_bytes(self):
        class IoCounters(self.ctypes.Structure):
            _fields_ = [(n, self.ctypes.c_ulonglong) for n in
                        ("ro", "wo", "oo", "read", "write", "other")]
        c = IoCounters()
        if not self.handle or not self.kernel32.GetProcessIoCounters(self.handle, self.ctypes.byref(c)):
            return None
        return c.read + c.write + c.other

    def _text(self, hwnd, cls=False):
        buf = self.ctypes.create_unicode_buffer(1024)
        (self.user32.GetClassNameW if cls else self.user32.GetWindowTextW)(hwnd, buf, 1024)
        return buf.value

    def _dialogs(self):
        """(progress windows, error dialogs) among the bridge's visible #32770 windows.
        A progress window's title ends in "..." ("Copying...", "Moving...")."""
        pid, progress, errors = self.bridge.proc.pid, [], []

        def each(hwnd, _):
            owner = self.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, self.ctypes.byref(owner))
            if owner.value == pid and self.user32.IsWindowVisible(hwnd) \
                    and self._text(hwnd, cls=True) == "#32770":
                title = self._text(hwnd)
                (progress if title.rstrip().endswith(("...", "…")) else errors).append((hwnd, title))
            return True

        self.user32.EnumWindows(self.enum_proc(each), 0)
        return progress, errors

    def _press_cancel(self, hwnd):
        """Press the progress window's Cancel button (control id IDCANCEL = 2), so Windows
        really stops the transfer instead of leaving it running."""
        button = self.user32.GetDlgItem(hwnd, 2)
        if button:
            self.user32.PostMessageW(button, 0x00F5, 0, 0)  # BM_CLICK
        else:
            self.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

    def _dialog_message(self, hwnd, title):
        texts = []

        def each(child, _):
            if self._text(child, cls=True) == "Static" and self._text(child).strip():
                texts.append(self._text(child).strip())
            return True

        self.user32.EnumChildWindows(hwnd, self.enum_proc(each), 0)
        return f"Windows: {title}" + (f" — {' '.join(texts)}" if texts else "")

    def _run(self):
        last = self._io_bytes() or 0
        alive_at = started = time.monotonic()
        cancel_at = None
        while not self.done.wait(0.5):
            progress, errors = self._dialogs()
            for hwnd, title in errors:
                if hwnd not in self.closed_dialogs:
                    self.closed_dialogs.add(hwnd)
                    self.reason = self.reason or self._dialog_message(hwnd, title)
                    self.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE = its OK
            now_bytes = self._io_bytes()
            if self.done.is_set():
                return
            now = time.monotonic()
            if progress or (now_bytes is not None and now_bytes - last >= self.MIN_PROGRESS):
                alive_at = now
                last = now_bytes if now_bytes is not None else last
            if progress and now - started > self.max_busy:
                # Alive but far too slow: cancel it the way a user would, then wait for
                # Windows to wind it down before this attempt is reported as failed.
                if cancel_at is None:
                    cancel_at = now
                    self.reason = self.reason or T("dibatalkan: lebih dari {} detik belum selesai",
                                                   int(self.max_busy))
                    for hwnd, _ in progress:
                        self._press_cancel(hwnd)
                elif now - cancel_at > 30:
                    self.bridge.close()  # Cancel didn't take; nothing more we can do
                    return
            elif not progress and now - alive_at > self.limit:
                # No progress window, no data: nothing is running for this attempt any more.
                self.reason = self.reason or T("tidak ada aktivitas transfer selama {} detik", self.limit)
                self.bridge.close()  # ends the attempt; the next call gets a fresh bridge
                return


class Style:
    BG = "#f3f5f8"
    CARD = "#ffffff"
    TEXT = "#0f172a"
    MUTED = "#64748b"
    BORDER = "#dfe5ec"
    BLUE = "#2563eb"
    BLUE_SOFT = "#e8effd"
    GREEN = "#16a34a"
    RED = "#dc2626"
    AMBER = "#b45309"
    STRIPE = "#f8fafc"
    SELECT = "#dbeafe"

    @staticmethod
    def apply(root):
        s = ttk.Style(root)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass

        base = ("Segoe UI", 10)
        bold = ("Segoe UI Semibold", 10)
        s.configure(".", font=base, background=Style.CARD, foreground=Style.TEXT,
                    bordercolor=Style.BORDER)
        s.configure("TFrame", background=Style.BG)
        s.configure("Card.TFrame", background=Style.CARD)
        s.configure("TLabel", background=Style.CARD)
        s.configure("Bg.TLabel", background=Style.BG)
        s.configure("Muted.TLabel", background=Style.BG, foreground=Style.MUTED)
        s.configure("CardMuted.TLabel", foreground=Style.MUTED)
        s.configure("Title.TLabel", background=Style.BG, font=("Segoe UI Semibold", 14))
        s.configure("Heading.TLabel", font=("Segoe UI Semibold", 12))
        s.configure("Icon.TLabel", font=("Segoe UI Emoji", 28), foreground=Style.MUTED)
        s.configure("Placeholder.TLabel", background="#ffffff", foreground="#9aa5b1")

        # No dotted focus rectangles on buttons; entries still show focus with a blue border.
        s.layout("TButton", [("Button.border", {"sticky": "nswe", "border": "1", "children": [
            ("Button.padding", {"sticky": "nswe", "children": [("Button.label", {"sticky": "nswe"})]})]})])
        s.layout("Toolbutton", [("Toolbutton.border", {"sticky": "nswe", "children": [
            ("Toolbutton.padding", {"sticky": "nswe", "children": [("Toolbutton.label", {"sticky": "nswe"})]})]})])

        # Flat look: clam draws a bevel from light/darkcolor, so they follow the background.
        def flat(name, bg, active, pressed, disabled, fg, disabled_fg, border, selected=None,
                 selected_fg=None, **kw):
            s.configure(name, background=bg, lightcolor=bg, darkcolor=bg,
                        bordercolor=border, foreground=fg, relief="solid", **kw)
            states = [("disabled", disabled), ("pressed", pressed), ("active", active)]
            fgs = [("disabled", disabled_fg)]
            if selected:
                states.insert(1, ("selected", selected))
                fgs.append(("selected", selected_fg))
            s.map(name, background=states, lightcolor=states, darkcolor=states,
                  foreground=fgs, relief=[("pressed", "solid"), ("selected", "solid")],
                  bordercolor=[("selected", selected or border)])

        flat("TButton", "#ffffff", "#eef2f7", "#e2e8f0", "#f8fafc", Style.TEXT, "#a3adba",
             Style.BORDER, padding=(12, 5))
        flat("Primary.TButton", Style.BLUE, "#1d4ed8", "#1e40af", "#a5bff5", "#ffffff",
             "#eef3fe", Style.BLUE, padding=(16, 6), font=bold)
        flat("Danger.TButton", Style.RED, "#b91c1c", "#991b1b", "#f1c4c4", "#ffffff",
             "#fdf2f2", Style.RED, padding=(16, 6), font=bold)
        flat("Link.TButton", Style.BG, Style.BG, Style.BG, Style.BG, Style.BLUE, "#a3adba",
             Style.BG, padding=(2, 0))
        flat("Chip.Toolbutton", "#ffffff", "#eef2f7", "#e2e8f0", "#ffffff", "#334155", "#b6bfca",
             Style.BORDER, selected=Style.BLUE, selected_fg="#ffffff", padding=(11, 4), anchor="center")
        flat("Seg.Toolbutton", "#ffffff", "#eef2f7", "#e2e8f0", "#f8fafc", Style.MUTED, "#b6bfca",
             Style.BORDER, selected=Style.BLUE_SOFT, selected_fg=Style.BLUE, padding=(12, 5),
             anchor="center")

        s.configure("TEntry", padding=(7, 5), fieldbackground="#ffffff", lightcolor=Style.BORDER)
        s.map("TEntry", lightcolor=[("focus", Style.BLUE)], bordercolor=[("focus", Style.BLUE)],
              fieldbackground=[("readonly", "#f8fafc")])

        linespace = tkfont.Font(root, font=base).metrics("linespace")
        s.configure("Treeview", rowheight=linespace + linespace // 2 + 2, background="#ffffff",
                    fieldbackground="#ffffff", foreground=Style.TEXT, borderwidth=0)
        s.configure("Treeview.Heading", background="#ffffff", foreground=Style.MUTED,
                    font=bold, padding=(8, 7), relief="flat", bordercolor=Style.BORDER,
                    lightcolor="#ffffff", darkcolor=Style.BORDER)
        s.map("Treeview.Heading", background=[("active", Style.STRIPE)])
        s.map("Treeview", background=[("selected", Style.SELECT)],
              foreground=[("selected", Style.TEXT)])
        s.configure("Horizontal.TProgressbar", troughcolor="#e2e8f0", bordercolor="#e2e8f0",
                    background=Style.BLUE, lightcolor=Style.BLUE,
                    darkcolor=Style.BLUE, thickness=6)


def faster_window_redraw(root):
    """
    Tk registers its window classes with CS_HREDRAW|CS_VREDRAW, which makes Windows
    repaint every widget on every size change, including ones that didn't move.
    Tk already redraws what actually changes, so dropping the flags is safe and cut
    a window-resize step from ~140 to ~80 ms here. Class-wide, so dialogs benefit too.
    """
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        user32.GetClassLongPtrW.restype = ctypes.c_size_t
        user32.GetClassLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.SetClassLongPtrW.restype = ctypes.c_size_t
        user32.SetClassLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_size_t]
        root.update_idletasks()
        for hwnd in (int(root.wm_frame(), 16), root.winfo_id()):  # TkTopLevel, TkChild
            style = user32.GetClassLongPtrW(hwnd, -26)  # GCL_STYLE
            user32.SetClassLongPtrW(hwnd, -26, style & ~0x3)  # CS_VREDRAW | CS_HREDRAW
    except (AttributeError, OSError, ValueError, tk.TclError):
        pass  # not on Windows: nothing to do


class SizeMoveWatcher:
    """
    Reports when the user starts/stops dragging this window's edge or title bar
    (EVENT_SYSTEM_MOVESIZESTART/END), which Tk doesn't expose. An out-of-context
    WinEvent hook: nothing is inserted into Tk's own message handling.

    The callbacks run inside Tk's message pump but outside any Tcl call, so they must
    NOT touch tkinter: a tkinter call from there resets _tkinter's thread-local
    thread state, and the next Python binding Tk runs dies with a fatal GIL error.
    Set flags / enqueue work instead.
    """

    def __init__(self, root, on_start, on_end):
        import ctypes
        from ctypes import wintypes
        proto = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND, wintypes.LONG,
                                   wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
        user32 = ctypes.windll.user32
        user32.SetWinEventHook.restype = wintypes.HANDLE
        user32.SetWinEventHook.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE, proto,
                                           wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
        user32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
        root.update_idletasks()
        wrapper = int(root.wm_frame(), 16)

        def callback(hook, event, hwnd, id_object, id_child, thread, time_ms):
            if hwnd == wrapper:
                (on_start if event == 0x000A else on_end)()

        self.user32 = user32
        self.callback = proto(callback)  # must stay referenced while hooked
        # MOVESIZESTART..MOVESIZEEND, this process only, WINEVENT_OUTOFCONTEXT.
        self.hook = user32.SetWinEventHook(0x000A, 0x000B, None, self.callback, os.getpid(), 0, 0)
        if not self.hook:
            raise OSError("SetWinEventHook gagal")

    def remove(self):
        self.user32.UnhookWinEvent(self.hook)


def text_width(font, texts, cap: int = 4000) -> int:
    """Pixel width of the widest text plus cell padding. Measures only the 30 longest by
    character count: exact enough, and fast even for 100k rows."""
    longest = heapq.nlargest(30, texts, key=len)
    return min(cap, max((font.measure(t) for t in longest), default=0) + 24)


def scroll_last_column(tree, content_width):
    """
    Size the last column to its content (or wider, to fill the view) instead of letting
    it stretch to the window: a stretched column cuts long text off at the window edge
    with nothing to scroll to. Returns fit(), to call again when the content changes.
    """
    columns = tree["columns"]
    tree.column(columns[-1], stretch=False)

    def fit(_event=None):
        others = sum(int(tree.column(c, "width")) for c in columns[:-1])
        if "tree" in str(tree["show"]):
            others += int(tree.column("#0", "width"))
        tree.column(columns[-1], width=max(content_width(), tree.winfo_width() - others - 2, 160))

    tree.bind("<Configure>", fit, add="+")
    return fit


def bind_horizontal_scroll(tree):
    """Shift+wheel, touchpad sideways swipe/tilt wheel, and ←/→ scroll the table sideways."""
    # A Treeview xview "unit" is ONE PIXEL, so the old "3 units per notch" moved the
    # table 3 px — scrolling looked broken. Scroll by pixels: 60 per wheel notch
    # (delta 120); touchpad deltas are smaller, so swipes stay smooth and proportional.
    def wheel(event):
        # Shift+wheel up (delta > 0) = left. Tk delivers a sideways touchpad swipe / tilt
        # wheel (WM_MOUSEHWHEEL) as Shift+wheel too; verified with real input: same sign.
        pixels = -event.delta // 2 or (-1 if event.delta > 0 else 1)
        tree.xview_scroll(pixels, "units")
        return "break"

    tree.bind("<Shift-MouseWheel>", wheel)
    tree.bind("<Left>", lambda e: (tree.xview_scroll(-40, "units"), "break")[1])
    tree.bind("<Right>", lambda e: (tree.xview_scroll(40, "units"), "break")[1])


def make_tree(parent, columns, headings, widths, show="headings", anchors=None):
    """Treeview + both scrollbars in `parent` (a fresh frame), returns the tree."""
    tree = ttk.Treeview(parent, columns=columns, show=show, selectmode="extended")
    for c in columns:
        tree.heading(c, text=headings[c], anchor=(anchors or {}).get(c, "w"))
        # Only the last column stretches, and none below a readable minimum: with Tk's
        # default (all stretch) widening one column squeezed the others to ~20 px
        # instead of letting the table scroll horizontally.
        last = c == columns[-1]
        tree.column(c, width=widths[c], anchor=(anchors or {}).get(c, "w"),
                    stretch=last, minwidth=160 if last else 60)
    ys = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    xs = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ys.grid(row=0, column=1, sticky="ns")
    xs.grid(row=1, column=0, sticky="ew")
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)
    tree.tag_configure("odd", background=Style.STRIPE)
    tree.tag_configure("locked", foreground="#94a3b8")
    return tree


def fill_tree(tree, rows, budget: float = 0.025):
    """
    Insert (parent, iid, options) rows in ~25 ms slices so the window keeps
    responding while tens of thousands of rows load. Starting a new fill on
    the same tree cancels the one in progress.
    """
    token = object()
    tree.fill_token = token
    rows = iter(rows)

    def step():
        if getattr(tree, "fill_token", None) is not token or not tree.winfo_exists():
            return
        deadline = time.perf_counter() + budget
        for parent, iid, options in rows:
            tree.insert(parent, "end", iid=iid, **options)
            if time.perf_counter() > deadline:
                tree.after(1, step)
                return

    step()


class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, records, source, dest: Path, title="Preview / Dry Run"):
        super().__init__(parent, bg=Style.CARD)
        self.title(title)
        self.geometry(f"{parent.px(1040)}x{parent.px(600)}")
        self.transient(parent)
        self.grab_set()

        counts = Counter(r["category"] for r in records)
        renames = sum(r["action"] == "RENAME" for r in records)
        ttk.Label(self, text=T("Preview — {} file → {}", f"{len(records):,}", dest), style="Heading.TLabel").pack(
            anchor="w", padx=16, pady=(14, 2))
        summary = "  ·  ".join(f"{cat.replace('/', ' › ')}: {n:,}" for cat, n in sorted(counts.items()))
        if renames:
            summary += "   |   " + T("{} akan diberi nama baru", f"{renames:,}")
        ttk.Label(self, text=summary, style="CardMuted.TLabel", wraplength=parent.px(1000)).pack(
            anchor="w", padx=16, pady=(0, 10))

        frame = ttk.Frame(self, style="Card.TFrame")
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        cols = ("action", "category", "source", "destination")
        tree = make_tree(
            frame, cols,
            {"action": T("Aksi"), "category": T("Tujuan"), "source": T("Sumber"), "destination": T("Ke")},
            {"action": parent.px(110), "category": parent.px(190),
             "source": parent.px(340), "destination": parent.px(380)},
        )
        tree.tag_configure("RENAME", foreground=Style.AMBER)
        tree.tag_configure("SKIP_CONFLICT", foreground=Style.MUTED)
        tree.tag_configure("OVERWRITE", foreground=Style.RED)

        sources = [rel_path(r["source"], source) for r in records]
        targets = [rel_path(r["destination"], dest) for r in records]
        tree.column("source", width=max(parent.px(200), text_width(parent.cell_font, sources, parent.px(520))))
        target_width = text_width(parent.cell_font, targets)
        scroll_last_column(tree, lambda: target_width)
        bind_horizontal_scroll(tree)
        fill_tree(tree, (("", None, {
            "tags": (r["action"], "odd") if i % 2 else (r["action"],),
            "values": (r["action"], r["category"].replace("/", " › "), sources[i], targets[i]),
        }) for i, r in enumerate(records)))

        ttk.Button(self, text=T("Tutup"), command=self.destroy).pack(pady=(0, 14))


class DuplicateWindow(tk.Toplevel):
    def __init__(self, parent, groups: list[list[Entry]], source: Path, callback):
        super().__init__(parent, bg=Style.CARD)
        self.title(T("Duplikat Ditemukan"))
        self.geometry(f"{parent.px(1040)}x{parent.px(620)}")
        self.transient(parent)
        self.grab_set()
        self.groups = groups
        self.callback = callback

        dup_count = sum(len(g) - 1 for g in groups)
        wasted = sum(g[0].size * (len(g) - 1) for g in groups)
        ttk.Label(self, text=T("{} file duplikat dalam {} grup  ·  bisa hemat {}",
                               f"{dup_count:,}", f"{len(groups):,}", human_size(wasted)),
                  style="Heading.TLabel").pack(anchor="w", padx=16, pady=(14, 2))
        ttk.Label(self, text=T("Isi file identik byte-per-byte (SHA-256). File tertua di tiap grup disimpan, "
                               "sisanya dipindah ke folder {}\\ — tidak ada yang dihapus. "
                               "Klik dua kali untuk membuka lokasi file.", DUPLICATES_DIR),
                  style="CardMuted.TLabel", wraplength=parent.px(1000)).pack(anchor="w", padx=16, pady=(0, 10))

        frame = ttk.Frame(self, style="Card.TFrame")
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        cols = ("status", "size", "modified", "path")
        tree = make_tree(
            frame, cols,
            {"status": "Status", "size": T("Ukuran"), "modified": T("Diubah"), "path": T("Lokasi")},
            {"status": parent.px(90), "size": parent.px(90),
             "modified": parent.px(130), "path": parent.px(420)},
            show="tree headings", anchors={"status": "center", "size": "e"},
        )
        tree.heading("#0", text="File", anchor="w")
        tree.column("#0", width=parent.px(320))
        tree.tag_configure("group", background="#f1f5f9")
        tree.tag_configure("keep", foreground=Style.GREEN)
        tree.tag_configure("dup", foreground=Style.AMBER)

        self.paths = {f"g{n}.{i}": e.path for n, g in enumerate(groups) for i, e in enumerate(g)}

        def rows():
            for n, g in enumerate(groups):
                yield "", f"g{n}", {"open": True, "tags": ("group",),
                                    "text": T("Grup {} — {} file identik", n + 1, len(g)),
                                    "values": ("", f"−{human_size(g[0].size * (len(g) - 1))}", "", "")}
                for i, e in enumerate(g):
                    yield f"g{n}", f"g{n}.{i}", {
                        "text": e.path.name, "tags": ("keep" if i == 0 else "dup",),
                        "values": (T("Simpan") if i == 0 else T("Duplikat"), human_size(e.size),
                                   fmt_time(e.mtime), rel_path(e.path, source))}

        path_width = text_width(parent.cell_font, (rel_path(p, source) for p in self.paths.values()))
        scroll_last_column(tree, lambda: path_width)
        bind_horizontal_scroll(tree)
        fill_tree(tree, rows())
        tree.bind("<Double-1>", lambda ev: self.paths.get(tree.focus()) and
                  parent.reveal_path(self.paths[tree.focus()]))

        bar = ttk.Frame(self, style="Card.TFrame")
        bar.pack(fill="x", padx=16, pady=(0, 14))
        ttk.Button(bar, text=T("Pindahkan {} duplikat ke {}\\", f"{dup_count:,}", DUPLICATES_DIR),
                   style="Primary.TButton", command=self.move).pack(side="right")
        ttk.Button(bar, text=T("Tutup"), command=self.destroy).pack(side="right", padx=8)

    def move(self):
        self.destroy()
        self.callback(self.groups)


class ExcludeFoldersWindow(tk.Toplevel):
    def __init__(self, parent, source: Path, current: set[str], callback):
        super().__init__(parent, bg=Style.CARD)
        self.title(T("Kecualikan Folder"))
        self.geometry(f"{parent.px(600)}x{parent.px(500)}")
        self.transient(parent)
        self.grab_set()
        self.callback = callback
        self.source = source

        ttk.Label(self, text=T("Pilih folder yang tidak boleh diproses."),
                  style="Heading.TLabel").pack(anchor="w", padx=16, pady=(14, 2))
        ttk.Label(self, text=T("Folder buatan aplikasi (Images, Videos, Duplicates, dll.) selalu dikecualikan."),
                  style="CardMuted.TLabel").pack(anchor="w", padx=16, pady=(0, 10))

        frame = ttk.Frame(self, style="Card.TFrame")
        frame.pack(fill="both", expand=True, padx=16)

        self.listbox = tk.Listbox(frame, selectmode=tk.EXTENDED, font=("Segoe UI", 10),
                                  relief="solid", borderwidth=1, highlightthickness=0,
                                  selectbackground=Style.SELECT, selectforeground=Style.TEXT,
                                  activestyle="none")
        ys = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=ys.set)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        folders = []
        for root, dirs, _ in os.walk(source):
            if Path(root) == source:
                dirs[:] = [d for d in dirs if d not in OWNED_DIRS]
            folders += [os.path.relpath(os.path.join(root, d), source) for d in dirs]

        folders.sort(key=lambda x: (x.count(os.sep), x.lower()))
        self.folders = folders

        for rel in folders:
            self.listbox.insert("end", rel)
            if rel in current:
                idx = self.listbox.size() - 1
                self.listbox.selection_set(idx)

        bar = ttk.Frame(self, style="Card.TFrame")
        bar.pack(fill="x", padx=16, pady=14)
        ttk.Button(bar, text=T("Pilih Semua"), command=lambda: self.listbox.select_set(0, "end")).pack(side="left")
        ttk.Button(bar, text=T("Batal Pilihan"), command=lambda: self.listbox.selection_clear(0, "end")).pack(side="left", padx=6)
        ttk.Button(bar, text=T("Terapkan"), style="Primary.TButton", command=self.apply).pack(side="right")

    def apply(self):
        selected = {self.folders[i] for i in self.listbox.curselection()}
        self.callback(selected)
        self.destroy()


class DeviceBrowser(tk.Toplevel):
    """Pick a folder on a phone connected over USB (MTP). Folders load lazily when opened."""
    LOADING = SEP + "\x1e"

    def __init__(self, parent, callback):
        super().__init__(parent, bg=Style.CARD)
        self.app = parent
        self.callback = callback
        self.title(T("Pilih Folder di HP"))
        self.geometry(f"{parent.px(560)}x{parent.px(500)}")
        self.transient(parent)
        self.grab_set()

        ttk.Label(self, text=T("Pilih folder di HP"), style="Heading.TLabel").pack(anchor="w", padx=16, pady=(14, 2))
        self.hint = ttk.Label(self, style="CardMuted.TLabel", wraplength=parent.px(520), justify="left")
        self.hint.pack(anchor="w", padx=16, pady=(0, 10))

        frame = ttk.Frame(self, style="Card.TFrame")
        frame.pack(fill="both", expand=True, padx=16)
        self.tree = make_tree(frame, (), {}, {}, show="tree")
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.ok_btn.state(
            ["!disabled"] if self.tree.selection() else ["disabled"]))

        bar = ttk.Frame(self, style="Card.TFrame")
        bar.pack(fill="x", padx=16, pady=14)
        ttk.Button(bar, text=T("⟳ Muat ulang"), command=self.reload).pack(side="left")
        self.ok_btn = ttk.Button(bar, text=T("Pilih folder ini"), style="Primary.TButton", command=self.choose)
        self.ok_btn.pack(side="right")
        self.ok_btn.state(["disabled"])
        ttk.Button(bar, text=T("Batal"), command=self.destroy).pack(side="right", padx=8)
        self.pending = 0
        self.bind("<Destroy>", self._on_destroy)
        self.reload()

    def _on_destroy(self, event):
        # Closed while the phone still hasn't answered (locked screen?): free the bridge.
        if event.widget is self and self.pending and self.app.bridge:
            self.app.bridge.close()

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        self.hint.configure(text=T("Mencari perangkat…"))
        self._load("")

    def _load(self, iid):
        parts = tuple(iid.split(SEP)) if iid else ()
        self.pending += 1
        self.app.run_bg(lambda: self.app.bridge_instance().dirs(parts), lambda names: self._loaded(iid, names))

    def _loaded(self, iid, names):
        if not self.winfo_exists():
            return
        self.pending -= 1
        if iid:
            self.tree.delete(*[k for k in self.tree.get_children(iid) if k.endswith(self.LOADING)])
        elif names:
            self.hint.configure(text=T("Buka perangkat lalu pilih folder, misalnya DCIM atau "
                                       "Android/media/com.whatsapp. Subfolder ikut dibaca."))
        else:
            self.hint.configure(text=T("Tidak ada HP terdeteksi. Hubungkan HP dengan kabel USB/OTG, "
                                       "buka kunci layar, lalu pilih mode USB “Transfer file / MTP”. "
                                       "Setelah itu klik Muat ulang.\n\nFlashdisk OTG atau HP mode "
                                       "penyimpanan punya huruf drive — pilih lewat 📁 Folder PC."))
            return
        for name in names:
            child = f"{iid}{SEP}{name}" if iid else name
            self.tree.insert(iid, "end", iid=child, text=("📁 " if iid else "📱 ") + name)
            self.tree.insert(child, "end", iid=child + self.LOADING, text=T("Memuat…"))

    def _on_open(self, event):
        iid = self.tree.focus()
        if any(k.endswith(self.LOADING) for k in self.tree.get_children(iid)):
            self._load(iid)

    def choose(self):
        selected = self.tree.selection()
        if selected and not selected[0].endswith(self.LOADING):
            self.destroy()
            self.callback(tuple(selected[0].split(SEP)))


class App(tk.Tk):
    COLUMNS = ("name", "category", "size", "modified", "path")
    HEADINGS = {"name": "Nama", "category": "Tujuan", "size": "Ukuran",
                "modified": "Diubah", "path": "Folder"}

    def __init__(self):
        global LANG
        lang = load_settings().get("lang")
        LANG = lang if lang in LANGS else "English"  # before any text is built
        super().__init__()
        scale = self.winfo_fpixels("1i") / 96
        self.px = lambda n: int(n * scale)
        self.title(APP_TITLE)
        self.icons = [tk.PhotoImage(data=ICON_PNG[px]) for px in (64, 32)]
        self.iconphoto(True, *self.icons)   # default: dialogs and other Toplevels get it too...
        self.iconphoto(False, *self.icons)  # ...and the taskbar reads this window's own icon (WM_SETICON)
        w = min(self.px(1280), self.winfo_screenwidth() - 40)
        h = min(self.px(780), self.winfo_screenheight() - 80)
        self.geometry(f"{w}x{h}")
        self.minsize(min(self.px(1000), w), min(self.px(560), h))
        self.configure(bg=Style.BG)
        Style.apply(self)
        faster_window_redraw(self)

        # Deliberately blank. User must choose a folder.
        self.source_var = tk.StringVar(value="")
        self.dest_var = tk.StringVar(value="")
        self.device_root: tuple[str, ...] | None = None
        self.mode_var = tk.StringVar(value="MOVE")
        self.conflict_var = tk.StringVar(value="unique")
        self.include_subfolders = tk.BooleanVar(value=False)
        self.android_var = tk.BooleanVar(value=True)
        self.skip_junk = tk.BooleanVar(value=True)
        self.protect_var = tk.BooleanVar(value=True)
        self.exclusions = Exclusions(CONFIG_DIR / "exclusions.json")
        self.category_var = tk.StringVar(value="")
        self.lang_var = tk.StringVar(value=LANG)
        self.search_var = tk.StringVar(value="")
        self.ext_var = tk.StringVar(value="")
        self.min_var = tk.StringVar(value="")
        self.max_var = tk.StringVar(value="")
        self.from_var = tk.StringVar(value="")
        self.to_var = tk.StringVar(value="")
        self.exclude_var = tk.StringVar(value="")
        self.status = tk.StringVar(value=T("Pilih folder di PC atau hubungkan HP untuk mulai."))

        self.all_files: list[Entry] = []
        self.filtered_files: list[Entry] = []
        self.category_counts = Counter()
        self.scanned = False
        self.busy = False
        self.stop_event = threading.Event()
        self.q = queue.Queue()
        self.last_log_path: Path | None = None
        self.bridge: ShellBridge | None = None
        self._bridge_lock = threading.Lock()
        self._sort = ("modified", True)
        self._filter_job = None
        self._listing_phone = False
        self._refit_pending = False

        self._build_ui()
        for var in (self.search_var, self.ext_var, self.min_var, self.max_var, self.from_var, self.to_var):
            var.trace_add("write", lambda *_: self._schedule_filter())
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._queue_job = self.after(50, self._process_queue)

        self._sizing = False   # set by SizeMoveWatcher (plain flag, never a Tk call)
        self._frozen = False
        self._settle_job = None
        self.bind("<Configure>", self._on_window_configure, add="+")
        try:
            self._sizemove = SizeMoveWatcher(self, self._drag_started, self._drag_ended)
        except (AttributeError, OSError, ValueError, tk.TclError):
            self._sizemove = None  # not on Windows: the layout simply follows every resize

    # ── interactive resize ────────────────────────────────────────────────
    # Windows only sends the next size once the previous one is painted. A full
    # relayout + repaint here is ~60 ms (the table alone ~30 ms), so live layout
    # capped the drag at ~15 fps with the edge trailing the cursor. Instead, during
    # a drag the layout is frozen between catch-ups every RELAYOUT_MS: the window
    # edge moves freely in between, and the content is laid out exactly on release.
    def _drag_started(self):  # WinEvent callback: flags only
        self._sizing = True

    def _drag_ended(self):  # WinEvent callback: flags only; the thaw runs from the queue
        self._sizing = False
        self.q.put(("thaw",))

    # During a drag, catch the content up this often. Measured with real drags:
    # live layout 15 fps; frozen-until-release 82 fps but a 130 px blank strip;
    # 40 ms → 36 fps with the content matching the window (median 0 px off).
    RELAYOUT_MS = 40

    def _on_window_configure(self, event):
        if event.widget is not self or not self._sizing:
            return
        if not self._frozen:
            # Runs before place's idle relayout, so outer still has its old size here.
            self._frozen = True
            self.outer.place_configure(relwidth=0, relheight=0,
                                       width=self.outer.winfo_width(), height=self.outer.winfo_height())
        # Throttle, not debounce: waiting for the mouse to pause left a blank strip
        # beside the content for as long as the user kept dragging.
        if not self._settle_job:
            self._settle_job = self.after(self.RELAYOUT_MS, self._settle_layout)

    def _thaw_layout(self):
        if self._settle_job:
            self.after_cancel(self._settle_job)
            self._settle_job = None
        if self._frozen:
            self._frozen = False
            self.outer.place_configure(relwidth=1, relheight=1, width=0, height=0)

    def _settle_layout(self):
        # Mid-drag catch-up: lay the content out once at the window's current size.
        self._settle_job = None
        if self._sizing:
            self.outer.place_configure(width=self.winfo_width(), height=self.winfo_height())

    # ── layout ────────────────────────────────────────────────────────────
    def _build_ui(self):
        px = self.px
        # Placed (not packed) so the layout can be frozen during a window drag; see _freeze_layout.
        self.outer = outer = ttk.Frame(self, padding=(18, 14, 18, 14))
        outer.place(x=0, y=0, relwidth=1, relheight=1)

        # Header: title · source · pickers.
        self.head = head = ttk.Frame(outer)
        head.pack(fill="x")
        ttk.Label(head, text="Android Media Separator", style="Title.TLabel").pack(side="left", padx=(0, 18))
        # Right-aligned controls live in one frame per row: on resize Windows then moves
        # a single window (children ride along) instead of repainting each button.
        pickers = ttk.Frame(head)
        pickers.pack(side="right")
        self.folder_btn = ttk.Button(pickers, text=T("📁 Folder PC"), command=self.choose_folder)
        self.folder_btn.pack(side="left")
        self.phone_btn = ttk.Button(pickers, text=T("📱 HP / OTG"), command=self.choose_device)
        self.phone_btn.pack(side="left", padx=6)
        self.scan_btn = ttk.Button(pickers, text="⟳", width=3, command=self.scan)
        self.scan_btn.pack(side="left")
        self.source_icon = ttk.Label(head, text="📁", style="Bg.TLabel")
        self.source_icon.pack(side="left")
        self.source_entry = ttk.Entry(head, textvariable=self.source_var)
        self.source_entry.pack(side="left", fill="x", expand=True, padx=(6, 10))
        self.source_entry.bind("<Return>", lambda e: self.scan())

        # Destination row, only when importing from a phone.
        self.dest_row = ttk.Frame(outer)
        ttk.Label(self.dest_row, text=T("Simpan ke PC:"), style="Muted.TLabel").pack(side="left", padx=(28, 6))
        self.dest_lbl = ttk.Label(self.dest_row, text="", style="Bg.TLabel")
        self.dest_lbl.pack(side="left")
        ttk.Button(self.dest_row, text=T("Ubah…"), style="Link.TButton", command=self.choose_dest).pack(side="left", padx=8)

        # Toolbar: category chips · search · filter · options.
        self.toolbar = ttk.Frame(outer)
        self.toolbar.pack(fill="x", pady=(14, 10))
        # Tools are packed first so they keep their space; on a narrow window the chips
        # drop their counts (see _fit_toolbar) and, if still too wide, get clipped instead.
        self.tools = tools = ttk.Frame(self.toolbar)
        tools.pack(side="right")
        self.chips = ttk.Frame(self.toolbar)
        self.chips.pack(side="left")
        self.chip_buttons = {}
        self._compact_chips = False
        self._full_toolbar_width = 0
        for key in ("",) + CATEGORY_DIRS:
            chip = ttk.Radiobutton(self.chips, value=key, variable=self.category_var,
                                   style="Chip.Toolbutton", command=self.apply_filters)
            chip.pack(side="left", padx=(0, 5))
            self.chip_buttons[key] = chip
        self._update_chips()
        self.toolbar.bind("<Configure>", self._fit_toolbar)

        ttk.Label(tools, text="🔍", style="Bg.TLabel").pack(side="left", padx=(14, 5))
        self.search_entry = ttk.Entry(tools, textvariable=self.search_var, width=24)
        self.search_entry.pack(side="left")
        self.filter_btn = ttk.Button(tools, text="Filter ▾", command=self.toggle_filters)
        self.filter_btn.pack(side="left", padx=6)
        self.options_menu = self._options_menu(self)
        self.opt_btn = ttk.Button(tools, text=T("⚙ Opsi ▾"), command=lambda: self.options_menu.tk_popup(
            self.opt_btn.winfo_rootx(), self.opt_btn.winfo_rooty() + self.opt_btn.winfo_height()))
        self.opt_btn.pack(side="left")
        # Placeholder text: shown while the box is empty and not focused.
        self.search_hint = ttk.Label(tools, text=T("Cari nama file…"), style="Placeholder.TLabel")
        self.search_hint.bind("<Button-1>", lambda e: self.search_entry.focus_set())
        for event in ("<FocusIn>", "<FocusOut>"):
            self.search_entry.bind(event, lambda e: self.after_idle(self._update_search_hint), add="+")
        self.search_var.trace_add("write", lambda *_: self._update_search_hint())
        self.after_idle(self._update_search_hint)

        # Advanced filters, hidden until asked for.
        self.filter_panel = ttk.Frame(outer, style="Card.TFrame", padding=(14, 10))
        for label, var, width in (("Ekstensi", self.ext_var, 16), ("Min MB", self.min_var, 7),
                                  ("Max MB", self.max_var, 7), ("Dari", self.from_var, 11),
                                  ("Sampai", self.to_var, 11)):
            ttk.Label(self.filter_panel, text=T(label), style="CardMuted.TLabel").pack(side="left", padx=(0, 5))
            ttk.Entry(self.filter_panel, textvariable=var, width=width).pack(side="left", padx=(0, 14))
        ttk.Label(self.filter_panel, text=T("mis. .jpg,.pdf · tanggal YYYY-MM-DD"),
                  style="CardMuted.TLabel").pack(side="left")
        ttk.Button(self.filter_panel, text="Reset", command=self.reset_filters).pack(side="right")

        # Action bar (packed before the table so it never gets squeezed out).
        bar = ttk.Frame(outer, style="Card.TFrame", padding=(14, 10))
        bar.pack(side="bottom", fill="x", pady=(10, 0))
        actions = ttk.Frame(bar, style="Card.TFrame")
        actions.pack(side="right")
        seg = ttk.Frame(actions, style="Card.TFrame")
        seg.pack(side="left", padx=(0, 16))
        self.dup_btn = ttk.Button(actions, text=T("Cari duplikat"), command=self.scan_duplicates)
        self.dup_btn.pack(side="left")
        self.preview_btn = ttk.Button(actions, text="Preview", command=self.preview)
        self.preview_btn.pack(side="left", padx=8)
        self.go_btn = ttk.Button(actions, style="Primary.TButton", width=24, command=self.organize)
        self.go_btn.pack(side="left")
        self.mode_buttons = []
        for text, value in (("Pindahkan", "MOVE"), ("Salin", "COPY")):
            b = ttk.Radiobutton(seg, text=T(text), value=value, variable=self.mode_var,
                                style="Seg.Toolbutton", command=self._update_go_button)
            b.pack(side="left")
            self.mode_buttons.append(b)
        self.progress = ttk.Progressbar(bar, mode="determinate", maximum=100, length=px(150))
        self.status_lbl = ttk.Label(bar, textvariable=self.status, style="CardMuted.TLabel")
        self.status_lbl.pack(side="left", fill="x", expand=True)

        # File table.
        self.table = table = ttk.Frame(outer, style="Card.TFrame")
        table.pack(fill="both", expand=True)
        self.tree = make_tree(
            table, self.COLUMNS, self.HEADINGS,
            {"name": px(360), "category": px(190), "size": px(90), "modified": px(140), "path": px(420)},
            anchors={"size": "e"},
        )
        for c in self.COLUMNS:
            self.tree.heading(c, command=lambda c=c: self.sort_by(c))
        self._update_headings()
        self.cell_font = tkfont.Font(self, font=("Segoe UI", 10))
        self.head_font = tkfont.Font(self, font=("Segoe UI Semibold", 10))
        self._path_width = 0
        self._fit_path_column = scroll_last_column(self.tree, lambda: self._path_width)
        bind_horizontal_scroll(self.tree)
        self.tree.bind("<Control-a>", lambda e: (self.select_all(), "break")[1])
        self.tree.bind("<Escape>", lambda e: self.tree.selection_remove(self.tree.selection()))
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_go_button())
        self.bind("<Control-o>", lambda e: self.choose_folder())
        self.bind("<Control-f>", lambda e: (self.search_entry.focus_set(), "break")[1])
        self.bind("<F5>", lambda e: self.scan())

        self.context_menu = tk.Menu(self, tearoff=False)
        self.context_menu.add_command(label=T("Pisahkan yang dipilih"), command=self.organize)
        self.context_menu.add_command(label=T("Buka lokasi file"), command=self._reveal_selected)
        self.context_menu.add_command(label=T("Salin path"), command=self._copy_paths)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=T("🔒 Kecualikan file yang dipilih"), command=self.exclude_selected)
        self.context_menu.add_command(label=T("🔒 Kecualikan seluruh folder ini"),
                                      command=lambda: self.exclude_selected(folder=True))
        self.context_menu.add_command(label=T("Batalkan pengecualian"), command=self.unexclude_selected)

        # Empty state, laid over the table.
        self.empty = ttk.Frame(table, style="Card.TFrame", padding=20)
        self.empty_icon = ttk.Label(self.empty, text="📂", style="Icon.TLabel")
        self.empty_icon.pack()
        self.empty_title = ttk.Label(self.empty, style="Heading.TLabel")
        self.empty_title.pack(pady=(6, 2))
        self.empty_text = ttk.Label(self.empty, style="CardMuted.TLabel", justify="center")
        self.empty_text.pack()
        self.empty_actions = ttk.Frame(self.empty, style="Card.TFrame")
        self.empty_actions.pack(pady=(14, 0))
        self.empty_folder = ttk.Button(self.empty_actions, text=T("📁 Pilih folder PC"),
                                       style="Primary.TButton", command=self.choose_folder)
        self.empty_phone = ttk.Button(self.empty_actions, text=T("📱 Hubungkan HP"), command=self.choose_device)
        self.empty_reset = ttk.Button(self.empty_actions, text=T("Reset filter"), command=self.reset_filters)

        self._lockable = [self.folder_btn, self.phone_btn, self.scan_btn, self.source_entry,
                          self.preview_btn, self.dup_btn, self.opt_btn, *self.mode_buttons]
        self._update_go_button()
        self._update_empty_state()

    def _options_menu(self, owner):
        menu = tk.Menu(owner, tearoff=False)
        menu.add_command(label=T("Jika nama file sudah ada:"), state="disabled")
        for text, value in (("Buat nama baru", "unique"), ("Lewati", "skip"), ("Timpa", "overwrite")):
            menu.add_radiobutton(label="    " + T(text), variable=self.conflict_var, value=value)
        menu.add_separator()
        menu.add_checkbutton(label=T("Sertakan subfolder"), variable=self.include_subfolders,
                             command=self._rescan_if_ready)
        menu.add_checkbutton(label=T("Lewati folder sistem & tersembunyi (Android/data, .thumbnails, …)"),
                             variable=self.skip_junk, command=self._rescan_if_ready)
        menu.add_checkbutton(label=T("Subfolder Android (WhatsApp, Kamera, Screenshot…)"),
                             variable=self.android_var, command=lambda: self._rerender(refit=True))
        menu.add_separator()
        menu.add_command(label=T("Kecualikan folder…"), command=self.exclude_folders)
        menu.add_separator()
        menu.add_checkbutton(label=T("🔒 Lindungi data aplikasi (backup WhatsApp, database, .nomedia)"),
                             variable=self.protect_var,
                             command=lambda: (self._rerender(refit=True), self.status.set(self._summary())))
        menu.add_command(label=T("Hapus semua pengecualian manual…"), command=self.clear_exclusions)
        menu.add_separator()
        menu.add_command(label=T("Buka log"), command=self.open_log)
        menu.add_separator()
        # Always bilingual, so someone who can't read the current language still finds it.
        languages = tk.Menu(menu, tearoff=False)
        for lang in LANGS:
            languages.add_radiobutton(label=LANG_NAMES[lang], variable=self.lang_var, value=lang,
                                      command=self._set_language)
        menu.add_cascade(label="🌐 Language / Bahasa", menu=languages)
        return menu

    def _set_language(self):
        try:
            save_settings({**load_settings(), "lang": self.lang_var.get()})
        except OSError as exc:
            messagebox.showerror("Language / Bahasa", str(exc), parent=self)
            return
        restart = {"English": "The language changes the next time the app starts.",
                   "Indonesia": "Bahasa akan berganti saat aplikasi dibuka lagi."}
        messagebox.showinfo("Language / Bahasa", restart[self.lang_var.get()], parent=self)

    # ── small UI helpers ──────────────────────────────────────────────────
    def _on_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "cell":
            iid = self.tree.identify_row(event.y)
            if iid:
                self._reveal(self.filtered_files[int(iid)])

    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid and iid not in self.tree.selection():
            self.tree.selection_set(iid)
        if self.tree.selection() and not self.busy:
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _reveal(self, entry: Entry):
        self.reveal_path(entry.path)

    def reveal_path(self, path):
        """Show a file selected in Explorer — on the PC or on the phone. Off the UI thread,
        since resolving a phone path goes over USB."""
        if isinstance(path, PurePosixPath):  # a file on the phone
            if self.busy:
                self.status.set(T("Tunggu proses selesai dulu — koneksi HP sedang dipakai."))
                return
            bridge = self.bridge_instance

            def work():
                hwnd = bridge().reveal(path)
                # The bridge runs in a background process, which Windows won't let raise
                # a window; this process has the user's click, so it can.
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
                user32.SetForegroundWindow.argtypes = [wintypes.HWND]
                if user32.IsIconic(wintypes.HWND(hwnd)):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
        else:
            work = lambda: reveal_in_explorer(str(path))
        self.status.set(T("Membuka lokasi {}…", path.name))
        self.run_bg(work, lambda _: self.status.set(T("Lokasi {} dibuka di Explorer.", path.name)))

    def _reveal_selected(self):
        selected = self.tree.selection()
        if selected:
            self._reveal(self.filtered_files[int(selected[0])])

    def _copy_paths(self):
        self.clipboard_clear()
        self.clipboard_append("\n".join(str(e.path) for e in self._selected_entries()))

    def _selected_entries(self) -> list[Entry]:
        return [self.filtered_files[int(i)] for i in self.tree.selection()]

    def _target_entries(self) -> list[Entry]:
        """What the main button acts on: the selection, or everything shown."""
        return self._selected_entries() or list(self.filtered_files)

    def _blocked(self, e: Entry) -> str:
        """Why this file must not be processed ("" = fine). The one place every action asks."""
        if self.protect_var.get() and e.protected:
            return e.protected
        return "dikecualikan" if self.exclusions.match(e.path) else ""

    def _destination_text(self, e: Entry, android: bool) -> str:
        """The "Tujuan" cell: where it goes, or 🔒 and why it stays."""
        blocked = self._blocked(e)
        return f"🔒 {T(blocked)}" if blocked else entry_label(e, android).replace("/", " › ")

    def _actionable(self, entries) -> tuple[list[Entry], int]:
        ok = [e for e in entries if not self._blocked(e)]
        return ok, len(entries) - len(ok)

    def exclude_selected(self, folder=False):
        entries = self._selected_entries()
        if not entries:
            return
        if folder:
            self.exclusions.add_folder(entries[0].path.parent)
            self.status.set(T("Folder {} dikecualikan (tersimpan).", entries[0].path.parent.name))
        else:
            self.exclusions.add_files(e.path for e in entries)
            self.status.set(T("{} file dikecualikan (tersimpan).", f"{len(entries):,}"))
        self._rerender(refit=True)

    def unexclude_selected(self):
        entries = self._selected_entries()
        self.exclusions.remove(e.path for e in entries)
        self.status.set(T("Pengecualian dihapus untuk {} file.", f"{len(entries):,}"))
        self._rerender(refit=True)

    def clear_exclusions(self):
        if not len(self.exclusions):
            messagebox.showinfo(T("Pengecualian"), T("Belum ada file atau folder yang dikecualikan."), parent=self)
        elif messagebox.askyesno(T("Hapus semua pengecualian"),
                                 T("Hapus {} pengecualian? File-file itu akan ikut diproses lagi "
                                   "(data aplikasi yang dilindungi tetap aman).", f"{len(self.exclusions):,}"),
                                 parent=self):
            self.exclusions.clear()
            self._rerender(refit=True)
            self.status.set(self._summary())

    def select_all(self):
        self.tree.selection_set(self.tree.get_children())

    def _update_search_hint(self):
        if self.search_var.get() or self.focus_get() is self.search_entry:
            self.search_hint.place_forget()
        else:
            self.search_hint.place(in_=self.search_entry, x=9, rely=0.5, anchor="w")

    def toggle_filters(self):
        if self.filter_panel.winfo_ismapped():
            self.filter_panel.pack_forget()
        else:
            self.filter_panel.pack(fill="x", pady=(0, 10), after=self.toolbar)

    def _fit_toolbar(self, _event=None):
        available = self.toolbar.winfo_width()
        if available <= 1:
            return
        needed = self.chips.winfo_reqwidth() + self.tools.winfo_reqwidth()
        if not self._compact_chips and needed > available:
            self._full_toolbar_width = needed  # remember what the full labels need
            self._compact_chips = True
            self._update_chips()
        elif self._compact_chips and available >= self._full_toolbar_width:
            self._compact_chips = False
            self._update_chips()

    def _update_chips(self):
        for key, chip in self.chip_buttons.items():
            name = T(CATEGORY_LABELS.get(key, "Semua"))
            count = self.category_counts[key] if key else len(self.all_files)
            chip.configure(text=f"{name}  {count:,}" if self.scanned and not self._compact_chips else name)
            chip.state(["disabled"] if self.scanned and key and not count else ["!disabled"])

    def _update_go_button(self):
        if self.busy:
            return
        selected = bool(self.tree.selection())
        count = len(self._actionable(self._target_entries())[0])  # protected/excluded never count
        text = T("⚡ Pisahkan {} dipilih" if selected else "⚡ Pisahkan semua ({})", f"{count:,}")
        self.go_btn.configure(text=text, style="Primary.TButton", command=self.organize)
        self.go_btn.state(["!disabled"] if count else ["disabled"])

    def _update_empty_state(self):
        if self.filtered_files:
            self.empty.place_forget()
            return
        for b in (self.empty_folder, self.empty_phone, self.empty_reset):
            b.pack_forget()
        if self.all_files:
            self.empty_icon.configure(text="🔍")
            self.empty_title.configure(text=T("Tidak ada file yang cocok"))
            self.empty_text.configure(text=T("Coba kategori lain, kata kunci lain, atau reset filter."))
            self.empty_reset.pack()
        else:
            self.empty_icon.configure(text="📂")
            if self.scanned:
                self.empty_title.configure(text=T("Tidak ada file di sini"))
                self.empty_text.configure(text=T("Folder ini kosong atau semua file sudah dipisahkan.\n"
                                                 "Aktifkan “Sertakan subfolder” di ⚙ Opsi untuk ikut membaca subfolder."))
            else:
                self.empty_title.configure(text=T("Mulai dengan memilih sumber file"))
                self.empty_text.configure(text=T("Pilih folder di PC, atau hubungkan HP Android lewat kabel USB/OTG.\n"
                                                 "Ctrl+O pilih folder  ·  F5 scan ulang  ·  Ctrl+F cari"))
            self.empty_folder.pack(side="left")
            self.empty_phone.pack(side="left", padx=(8, 0))
        self.empty.place(relx=0.5, rely=0.45, anchor="center")
        self.empty.lift()

    def _summary(self) -> str:
        text = T("{} file · {}", f"{len(self.all_files):,}", human_size(sum(e.size for e in self.all_files)))
        if len(self.filtered_files) != len(self.all_files):
            text += "  —  " + T("tampil {} ({})", f"{len(self.filtered_files):,}",
                                human_size(sum(e.size for e in self.filtered_files)))
        blocked = sum(1 for e in self.all_files if self._blocked(e))
        if blocked:
            text += "  ·  " + T("🔒 {} dilindungi/dikecualikan, tidak akan diproses", f"{blocked:,}")
        return text

    # ── background work ───────────────────────────────────────────────────
    def run_bg(self, work, done, status=None, cancellable=False, determinate=False):
        """Run work() on a thread, then done(result) on the UI thread. With a
        status the window shows progress and locks conflicting controls."""
        if status is not None:
            self._set_busy(True, status, cancellable, determinate)

        def run():
            try:
                self.q.put(("done", done, work(), status is not None))
            except Exception as exc:
                self.q.put(("error", str(exc), status is not None))

        threading.Thread(target=run, daemon=True).start()

    def _reporter(self):
        return throttled(lambda cur, total, text: self.q.put(("progress", cur, total, text)))

    def bridge_instance(self) -> ShellBridge:
        with self._bridge_lock:
            if self.bridge is None or self.bridge.closed or self.bridge.proc.poll() is not None:
                self.bridge = ShellBridge()
            return self.bridge

    def _set_busy(self, busy, status="", cancellable=False, determinate=False):
        self.busy = busy
        for w in self._lockable:
            w.state(["disabled"] if busy else ["!disabled"])
        self.progress.stop()
        if busy:
            self.stop_event.clear()
            self.status.set(status)
            self.progress.configure(mode="determinate" if determinate else "indeterminate", value=0)
            self.progress.pack(side="left", padx=(0, 12), before=self.status_lbl)
            if not determinate:
                self.progress.start(12)
            self.go_btn.configure(text="■ Stop", style="Danger.TButton", command=self.stop_operation)
            self.go_btn.state(["!disabled"] if cancellable else ["disabled"])
        else:
            self.progress.pack_forget()
            self._update_go_button()

    def _process_queue(self):
        try:
            while True:
                kind, *rest = self.q.get_nowait()
                if kind == "thaw":
                    self._thaw_layout()
                elif kind == "progress":
                    current, total, text = rest
                    if total:
                        self.progress["value"] = current / total * 100
                    self.status.set(text)
                elif kind == "done":
                    done, result, was_busy = rest
                    if was_busy:
                        self._set_busy(False)
                    done(result)
                elif kind == "error":
                    message, was_busy = rest
                    if was_busy:
                        self._set_busy(False)
                    if self.stop_event.is_set():  # the user stopped it; the error is just the fallout
                        self.status.set(T("Dihentikan."))
                    else:
                        self.status.set(T("Terjadi error."))
                        messagebox.showerror("Error", message, parent=self)
        except queue.Empty:
            pass
        finally:
            self._queue_job = self.after(50, self._process_queue)

    def stop_operation(self):
        if not self.busy:
            return
        second_press = self.stop_event.is_set()
        self.stop_event.set()
        # A locked/asleep phone can leave a Shell call hanging forever, so a phone
        # listing (or a second press) cuts the bridge instead of waiting politely.
        if self.device_root and self.bridge and (second_press or self._listing_phone):
            self.bridge.close()
            self.status.set(T("Dihentikan paksa."))
        else:
            self.status.set(T("Menghentikan setelah file ini…  (klik Stop lagi untuk paksa)"))

    def _on_close(self):
        self.stop_event.set()
        self.after_cancel(self._queue_job)
        if self._sizemove:
            self._sizemove.remove()
        if self.bridge:
            self.bridge.close()
        self.destroy()

    # ── source / destination ──────────────────────────────────────────────
    def source(self):
        if self.device_root:
            return PurePosixPath(*self.device_root)
        return Path(self.source_var.get().strip().strip('"'))

    def dest_root(self) -> Path:
        return Path(self.dest_var.get()) if self.device_root else self.source()

    def choose_folder(self):
        folder = filedialog.askdirectory(title=T("Pilih folder sumber"), parent=self)
        if folder:
            self.device_root = None
            self.source_entry.state(["!readonly"])
            self.source_icon.configure(text="📁")
            self.source_var.set(folder)
            self.dest_row.pack_forget()
            self.scan()

    def choose_device(self):
        DeviceBrowser(self, self.set_device)

    def set_device(self, parts):
        self.device_root = tuple(parts)
        self.source_icon.configure(text="📱")
        self.source_var.set("  ›  ".join(parts))
        self.source_entry.state(["readonly"])
        self.include_subfolders.set(True)  # phone media sits in subfolders (DCIM/Camera, …)
        self.dest_row.pack(fill="x", pady=(8, 0), after=self.head)
        self.dest_lbl.configure(text=self.dest_var.get() or T("belum dipilih — ditanyakan saat memisahkan"))
        self.scan()

    def choose_dest(self):
        folder = filedialog.askdirectory(title=T("Pilih folder di PC untuk menyimpan file dari HP"), parent=self)
        if folder:
            self.dest_var.set(folder)
            self.dest_lbl.configure(text=folder)
        return bool(folder)

    def _require_dest(self) -> Path | None:
        if self.device_root and not self.dest_var.get() and not self.choose_dest():
            return None
        return self.dest_root()

    def validate_source(self):
        if self.device_root:
            return self.source()
        raw = self.source_var.get().strip().strip('"')
        if not raw:
            messagebox.showinfo(T("Pilih folder sumber"),
                                T('Klik "Folder PC" atau "HP / OTG" untuk memilih sumber file.'), parent=self)
            return None
        p = Path(raw)
        if not p.is_dir():
            messagebox.showerror(T("Folder tidak valid"), T("Folder tidak ditemukan:\n{}", p), parent=self)
            return None
        return p

    def _rescan_if_ready(self):
        if self.scanned:
            self.scan()

    # ── scan / filter / table ─────────────────────────────────────────────
    def scan(self):
        if self.busy:
            return
        source = self.validate_source()
        if source is None:
            return

        recursive, skip_junk = self.include_subfolders.get(), self.skip_junk.get()
        report = self._reporter()
        device = self.device_root
        if device:
            def progress(n, line):
                # Show where the scan is, so a slow folder is easy to spot (and exclude).
                folder = line.rsplit("\t", 1)[-1].rpartition("/")[0] or "  ›  ".join(device)
                report(n, None, T("Membaca HP… {} file  ·  {}", f"{n:,}", folder))

            def work():
                try:
                    return self.bridge_instance().list_files(device, recursive, progress, skip_junk)
                finally:
                    self._listing_phone = False
            self._listing_phone = True
        else:
            excluded = parse_excluded_paths(self.exclude_var.get(), source)
            script = Path(sys.argv[0]).name

            def work():
                return discover_files(source, recursive, script, excluded,
                                      lambda n, _: report(n, None, T("Membaca folder… {} file", f"{n:,}")),
                                      skip_junk)
        self.run_bg(work, self._scan_done, cancellable=bool(device),
                    status=T("Membaca HP… (biarkan layar HP tetap menyala)") if device else T("Membaca folder…"))

    def _scan_done(self, found):
        self.scanned = True
        self.all_files = found
        self.category_counts = Counter(e.category for e in found)
        if self.category_var.get() and not self.category_counts[self.category_var.get()]:
            self.category_var.set("")
        self._compact_chips = False  # counts changed: re-measure the full labels
        self._update_chips()
        self._refit_pending = True  # new data: size every column to it
        self.after_idle(self._fit_toolbar)
        self.apply_filters()

    def parse_filters(self):
        def number(var, label):
            text = var.get().strip()
            if not text:
                return None
            try:
                value = float(text.replace(",", "."))
            except ValueError:
                raise ValueError(T("{} harus berupa angka.", label))
            if value < 0:
                raise ValueError(T("{} tidak boleh negatif.", label))
            return value

        min_mb = number(self.min_var, "Min MB")
        max_mb = number(self.max_var, "Max MB")
        if min_mb is not None and max_mb is not None and min_mb > max_mb:
            raise ValueError(T("Min MB tidak boleh lebih besar dari Max MB."))

        def date_value(var, label):
            text = var.get().strip()
            if not text:
                return None
            try:
                return datetime.strptime(text, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(T("{} harus YYYY-MM-DD.", label))

        date_from = date_value(self.from_var, T("Tanggal Dari"))
        date_to = date_value(self.to_var, T("Tanggal Sampai"))
        if date_from and date_to and date_from > date_to:
            raise ValueError(T("Tanggal Dari tidak boleh lebih besar dari Tanggal Sampai."))

        return min_mb, max_mb, date_from, date_to, parse_extensions(self.ext_var.get())

    def _schedule_filter(self):
        # Filter while typing, but only once the typing pauses.
        if self._filter_job:
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(200, self.apply_filters)

    def apply_filters(self):
        if self._filter_job:
            self.after_cancel(self._filter_job)
            self._filter_job = None
        active = sum(bool(v.get().strip()) for v in
                     (self.ext_var, self.min_var, self.max_var, self.from_var, self.to_var))
        self.filter_btn.configure(text=f"Filter ({active}) ▾" if active else "Filter ▾")
        try:
            min_mb, max_mb, date_from, date_to, extensions = self.parse_filters()
        except ValueError as exc:
            self.status.set(f"⚠ {exc}")
            return
        self.filtered_files = filter_files(self.all_files, min_mb, max_mb, date_from, date_to,
                                           extensions, self.category_var.get(), self.search_var.get())
        self._apply_sort()
        self._refresh_table()
        if not self.busy and self.scanned:
            self.status.set(self._summary())

    def reset_filters(self):
        for var in (self.ext_var, self.min_var, self.max_var, self.from_var, self.to_var,
                    self.search_var, self.category_var):
            var.set("")
        self.apply_filters()

    def sort_by(self, col):
        current, reverse = self._sort
        # Same column flips; a new column starts biggest/newest first for numbers, A→Z for text.
        self._sort = (col, not reverse if col == current else col in ("size", "modified"))
        self._rerender()

    def _rerender(self, refit=False):
        self._apply_sort()
        self._refresh_table(refit)

    def _fit_columns(self, files, refit):
        """Columns sized to their content, so nothing is cut off and the table scrolls
        sideways when it's wider than the window. `refit` (new data) also resizes the
        first columns; otherwise only the path column follows the data, keeping any
        width the user dragged by hand."""
        px, android, source = self.px, self.android_var.get(), self.source()
        heading = lambda c: self.head_font.measure(T(self.HEADINGS[c]) + " ▼") + 28
        if refit:
            for c, texts, cap in (
                    ("name", (e.path.name for e in files), px(560)),
                    ("category", (self._destination_text(e, android) for e in files), px(320)),
                    ("size", ("1,023.9 MB",), px(140)),
                    ("modified", ("2026-12-31 23:59",), px(200))):
                self.tree.column(c, width=max(heading(c), text_width(self.cell_font, texts, cap)))
        self._path_width = max(heading("path"), text_width(
            self.cell_font, (rel_path(e.path.parent, source) for e in files)))
        self._fit_path_column()

    def _apply_sort(self):
        col, reverse = self._sort
        android = self.android_var.get()
        key = {
            "name": lambda e: e.path.name.lower(),
            "category": lambda e: entry_label(e, android),
            "size": lambda e: e.size,
            "modified": lambda e: e.mtime,
            "path": lambda e: str(e.path).lower(),
        }[col]
        self.filtered_files.sort(key=key, reverse=reverse)
        self._update_headings()

    def _update_headings(self):
        col, reverse = self._sort
        for c in self.COLUMNS:
            arrow = (" ▼" if reverse else " ▲") if c == col else ""
            self.tree.heading(c, text=T(self.HEADINGS[c]) + arrow)

    def _refresh_table(self, refit=False):
        self.tree.delete(*self.tree.get_children())
        source, android, files = self.source(), self.android_var.get(), self.filtered_files
        self._fit_columns(files, refit or self._refit_pending)
        self._refit_pending = False
        def row(i, e):
            tags = (("odd",) if i % 2 else ()) + (("locked",) if self._blocked(e) else ())
            return "", str(i), {"tags": tags, "values": (
                e.path.name, self._destination_text(e, android), human_size(e.size), fmt_time(e.mtime),
                rel_path(e.path.parent, source) or "—")}

        fill_tree(self.tree, (row(i, e) for i, e in enumerate(files)))
        self._update_go_button()
        self._update_empty_state()

    # ── actions ───────────────────────────────────────────────────────────
    def exclude_folders(self):
        if self.device_root:
            messagebox.showinfo(T("Kecualikan folder"),
                                T("Untuk HP, pilih langsung folder yang ingin dibaca lewat 📱 HP / OTG."),
                                parent=self)
            return
        source = self.validate_source()
        if source is None:
            return

        current = set()
        raw = self.exclude_var.get().strip()
        if raw:
            current = {x.strip() for x in raw.replace(";", "\n").splitlines() if x.strip()}

        ExcludeFoldersWindow(self, source, current, self._set_excluded)

    def _set_excluded(self, selected: set[str]):
        self.exclude_var.set("\n".join(sorted(selected)))
        if self.source_var.get().strip():
            self.scan()

    def _entries_to_process(self):
        """Selection (or everything shown) minus protected/excluded files; None if nothing is left."""
        entries, blocked = self._actionable(self._target_entries())
        if not entries:
            if blocked:
                messagebox.showinfo(T("Tidak ada yang diproses"),
                                    T("Semua {} file ini dilindungi atau dikecualikan.", f"{blocked:,}"), parent=self)
            return None, blocked
        return entries, blocked

    def preview(self):
        files, _ = self._entries_to_process()
        if not files:
            return
        dest = self._require_dest()
        if dest is None:
            return
        paths = [e.path for e in files]
        source, conflict, android = self.source(), self.conflict_var.get(), self.android_var.get()
        self.run_bg(lambda: preview_operations(paths, source, conflict, android, dest),
                    lambda records: PreviewWindow(self, records, source, dest),
                    status=T("Menyiapkan preview…"))

    def _confirm(self, files, dest: Path, blocked: int = 0):
        move = self.mode_var.get() == "MOVE"
        conflict_text = T({
            "unique": "buat nama baru",
            "skip": "lewati",
            "overwrite": "timpa",
        }[self.conflict_var.get()])
        android_text = T("aktif") if self.android_var.get() else T("nonaktif")
        if self.device_root:
            head = T("MEMINDAHKAN {} file dari HP ke folder kategori di:\n{}" if move else
                     "MENYALIN {} file dari HP ke folder kategori di:\n{}", f"{len(files):,}", dest)
            if move:
                head += "\n" + T("(file di HP akan dihapus setelah tersalin)")
        else:
            head = T("MEMINDAHKAN {} file ke folder kategori di:\n{}" if move else
                     "MENYALIN {} file ke folder kategori di:\n{}", f"{len(files):,}", dest)

        msg = (
            head + "\n\n"
            + T("Jika nama sudah ada: {}.", conflict_text) + "\n"
            + T("Subfolder Android: {}.", android_text) + "\n"
            + (T("🔒 {} file dilindungi/dikecualikan tidak akan disentuh.", f"{blocked:,}") + "\n" if blocked else "")
            + "\n" + T("Klik Preview untuk memeriksa tujuan setiap file lebih dulu.")
        )
        return messagebox.askyesno(T("Konfirmasi"), msg, parent=self)

    def _whatsapp_media_check(self, entries) -> bool:
        """Before a MOVE of WhatsApp media: offer to copy instead. False = cancelled."""
        if self.mode_var.get() != "MOVE":
            return True
        source = self.source()
        count = sum(1 for e in entries if WHATSAPP_MEDIA.search(rel_path(e.path, source).replace("\\", "/")))
        if not count:
            return True
        answer = messagebox.askyesnocancel(
            T("Media WhatsApp"),
            T("{} file adalah media WhatsApp. Kalau dipindahkan, foto/video/dokumen itu "
              "akan tampil buram atau hilang di dalam chat WhatsApp.\n\n"
              "Ya — ganti ke SALIN (disarankan, HP tidak berubah)\n"
              "Tidak — tetap PINDAHKAN\n"
              "Batal — jangan lakukan apa pun", f"{count:,}"), icon="warning", parent=self)
        if answer is None:
            return False
        if answer:
            self.mode_var.set("COPY")
            self._update_go_button()
        return True

    def organize(self):
        entries, blocked = self._entries_to_process()
        if not entries:
            return
        dest = self._require_dest()
        if dest is None or not self._whatsapp_media_check(entries) or not self._confirm(entries, dest, blocked):
            return
        paths = [e.path for e in entries]
        source, conflict, android = self.source(), self.conflict_var.get(), self.android_var.get()
        mode = self.mode_var.get()
        fetch = None
        if self.device_root:
            fetch = self._phone_fetcher({e.path: e.size for e in entries}, dest, mode == "MOVE")
        self._start_operation(lambda: preview_operations(paths, source, conflict, android, dest),
                              mode, conflict, dest, fetch)

    RETRY_WAITS = (2,)     # seconds before the 2nd (last) attempt at one file
    LATE_GRACE = 20        # after the run, seconds to wait for written-off transfers to show up
    ABORT_AFTER = 3        # files in a row that fail → check whether the phone still answers

    def _phone_fetcher(self, sizes, dest: Path, move: bool):
        """
        fetch(record) for execute_operations, hardened after a real USB drop mid-move
        ("A device attached to the system is not functioning", phone back to OK seconds
        later): retry a file a couple of times, accept a copy the Shell finished late,
        and stop the whole run if the connection is clearly gone.
        """
        staging = dest / STAGING_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
        counter = itertools.count()
        bridge = self.bridge_instance
        failures_in_row = 0

        device = self.device_root[:1]

        def phone_answers() -> bool:
            try:
                return bool(bridge().dirs(device, timeout=ShellBridge.STALL_LIMIT))
            except Exception:
                return False

        def finished_late(folders, size):
            # A transfer outlives the attempt that started it: MTP copies run in another
            # Windows process, so killing our bridge doesn't stop them (seen: a 375 MB PDF
            # completed after its attempt had timed out). A staged file of the right size
            # is the real thing.
            return next((p for f in folders if f.is_dir() for p in f.iterdir()
                         if p.is_file() and p.stat().st_size == size), None)

        def still_on_phone(src) -> bool:
            try:
                return any(e.path == src for e in bridge().list_files(src.parts[:-1], False, skip_junk=False))
            except Exception:
                return True  # can't tell: assume it's there, i.e. treat a short copy as incomplete

        staged = {}  # attempt folder → record, for recover()

        def fetch(record):
            nonlocal failures_in_row
            src, size = record["source"], sizes[record["source"]]
            tried, error, local, note = [], None, None, ""
            for wait in (0, *self.RETRY_WAITS):
                if wait and self.stop_event.wait(wait):  # interruptible pause before a retry
                    break
                folder = staging / str(next(counter))  # fresh empty folder: how completion is detected
                tried.append(folder)
                staged[folder] = record
                try:
                    got = bridge().fetch(src, size, folder, move)
                    received = got.stat().st_size
                    if received == size:
                        local = got
                        break
                    # The Shell let go of a short file: a cancelled copy (seen: 0 B) unless the
                    # phone no longer has the source, i.e. it did move it and misreported the size.
                    if move and not still_on_phone(src):
                        local, note = got, T("ukuran dilaporkan HP {} B, diterima {} B", f"{size:,}", f"{received:,}")
                        break
                    got.unlink(missing_ok=True)
                    error = RuntimeError(T("tersalin tidak lengkap ({} dari {} B)", f"{received:,}", f"{size:,}"))
                except Exception as exc:
                    error = exc
                local = finished_late(tried, size)
                if local or self.stop_event.is_set():
                    break
            if local is None:
                failures_in_row += 1
                if failures_in_row >= self.ABORT_AFTER and not self.stop_event.is_set():
                    # Several bad files in a row (e.g. a worn SD-card folder) is not a dead
                    # link: keep going as long as the phone still answers.
                    if phone_answers():
                        failures_in_row = 0
                    else:
                        self._abort_reason = T(
                            "HP tidak merespons lagi setelah {} file berturut-turut "
                            "gagal, jadi proses dihentikan otomatis.\n\n"
                            "Cabut-colok kabel, buka kunci layar HP, pilih “Transfer file”, lalu "
                            "scan ulang dan jalankan lagi. File yang sudah berhasil tidak akan "
                            "diproses ulang; file yang gagal masih ada di HP.", self.ABORT_AFTER)
                        self.stop_event.set()
                raise error or RuntimeError(T("Dihentikan."))
            failures_in_row = 0
            return (local, note) if note else local

        def recover(logs) -> list[dict]:
            """
            After the run: transfers that finished after their attempt was written off are
            sitting in staging. If that file still has no successful row, move it to its
            destination (for a MOVE it's now the only copy); if it already succeeded through
            another attempt, the staged file is a spare copy and is removed.
            """
            done = {l["source"] for l in logs if l["status"] == "OK"}

            def pending():
                """Written-off attempts still without a file (may yet arrive), and files still being written."""
                empty = busy = False
                for folder, record in staged.items():
                    if str(record["source"]) in done:
                        continue
                    files = [p for p in folder.iterdir() if p.is_file()] if folder.is_dir() else []
                    empty |= not files
                    busy |= any(_in_use(p) for p in files)
                return empty, busy

            # A late transfer may not even have created its file yet (a worn SD card can sit
            # silent for >15 s): give those 20 s; one already writing gets up to 5 minutes.
            # Not when stopped (by the user or because the phone is gone): stop means now.
            start = time.monotonic()
            while not self.stop_event.is_set():
                empty, busy = pending()
                elapsed = time.monotonic() - start
                if not ((empty and elapsed < self.LATE_GRACE) or (busy and elapsed < 300)):
                    break
                time.sleep(1)
            rows = []
            for folder, record in staged.items():
                for p in (list(folder.iterdir()) if folder.is_dir() else []):
                    src = record["source"]
                    if not p.is_file() or _in_use(p) or p.stat().st_size != sizes[src]:
                        continue  # incomplete: left in staging and reported to the user
                    if str(src) in done:
                        p.unlink()
                        continue
                    target = record["destination"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists():
                        target = unique_destination(target.parent, src.name)
                    transfer(p, target, move=True)
                    done.add(str(src))
                    rows.append({"time": datetime.now().isoformat(timespec="seconds"),
                                 "action": "MOVE" if move else "COPY", "status": "OK",
                                 "category": record["category"], "source": str(src),
                                 "destination": str(target),
                                 "error": T("dipulihkan: tiba setelah percobaannya dianggap gagal")})
            return rows

        fetch.recover = recover
        return fetch

    def _start_operation(self, make_records, mode, conflict, log_dir: Path, fetch=None):
        report = self._reporter()

        def progress(current, total, ok, skipped, failed):
            report(current, total, T("{}/{}  ·  berhasil {}  ·  dilewati {}  ·  gagal {}",
                                     f"{current:,}", f"{total:,}", f"{ok:,}", f"{skipped:,}", f"{failed:,}"))

        # One log file per destination folder, never inside a category folder.
        log_path = log_dir / LOG_NAME
        self._abort_reason = None

        def work():
            records = make_records()
            log = LogWriter(log_path)
            try:
                result = list(execute_operations(records, mode, conflict, self.stop_event, progress, fetch,
                                                 on_record=log.write))
                if fetch and hasattr(fetch, "recover"):
                    report(0, None, T("Menunggu & memeriksa transfer yang tiba terlambat…"))
                    recovered = fetch.recover(result[4])
                    for row in recovered:
                        log.write(row)
                        result[4].append(row)
                    result[0] += len(recovered)  # success
                    result[2] -= len(recovered)  # failed (each one had an ERROR row)
            finally:
                log.close()
                if fetch:
                    remove_empty_dirs(log_dir / STAGING_DIR)
            stranded = sum(1 for p in (log_dir / STAGING_DIR).rglob("*") if p.is_file()) if fetch else 0
            return (*result, log_path, stranded)

        self.run_bg(work, self._operation_done, status=T("Memproses…"), cancellable=True, determinate=True)

    def _operation_done(self, result):
        success, skipped, failed, cancelled, logs, log_path, stranded = result
        self.last_log_path = log_path
        counts = T("Berhasil {}  ·  dilewati {}  ·  gagal {}", f"{success:,}", f"{skipped:,}", f"{failed:,}")
        self.status.set((T("Dihentikan — ") if cancelled else T("Selesai — ")) + counts)
        detail = "\n\n" + T("Berhasil: {}\nDilewati: {}\nGagal: {}\n\nLog: {}",
                            f"{success:,}", f"{skipped:,}", f"{failed:,}", log_path)
        if failed:
            recovered = {log["source"] for log in logs if log["status"] == "OK"}
            errors = [log for log in logs if log["status"] == "ERROR" and log["source"] not in recovered]
            detail += "\n\n" + T("Yang gagal:") + "\n" + "\n".join(
                f"• {Path(log['source'].replace('/', os.sep)).name} — {log['error'][:140]}" for log in errors[:6])
            if len(errors) > 6:
                detail += "\n" + T("… dan {} lainnya (lihat log)", f"{len(errors) - 6:,}")
        if failed and self.device_root:
            detail += "\n\n" + T("File yang gagal masih ada di HP — scan ulang lalu jalankan lagi untuk mencobanya.")
        if stranded:
            detail += "\n\n" + T("⚠ {} file tertahan di folder staging (sudah tersalin, belum "
                                 "dipindah ke kategori):\n{}", f"{stranded:,}", log_path.parent / STAGING_DIR)
        if self._abort_reason:
            messagebox.showwarning(T("Proses dihentikan otomatis"), self._abort_reason + detail, parent=self)
        elif cancelled:
            messagebox.showwarning(T("Operasi dihentikan"), T("Operasi dihentikan dengan aman.") + detail, parent=self)
        elif failed or stranded:
            messagebox.showwarning(T("Selesai dengan masalah"), T("Operasi selesai, tapi ada yang gagal.") + detail,
                                   parent=self)
        else:
            messagebox.showinfo(T("Selesai"), T("Operasi selesai.") + detail, parent=self)
        if self.device_root:
            # Re-listing a phone takes minutes; we already know what changed: only
            # files that were successfully MOVEd are gone from it.
            moved = {log["source"] for log in logs if log["status"] == "OK" and log["action"] == "MOVE"}
            self._scan_done([e for e in self.all_files if str(e.path) not in moved])
            self.status.set((T("Dihentikan — ") if cancelled else T("Selesai — ")) + counts)
        else:
            # Refresh filesystem state. If source becomes empty, the table shows the empty state.
            self.scan()

    def scan_duplicates(self):
        if self.busy:
            return
        if self.device_root:
            messagebox.showinfo(
                T("Cari duplikat"),
                T("Mencari duplikat perlu membaca isi setiap file — terlalu lambat lewat kabel MTP.\n\n"
                  "Salin file dari HP ke PC dulu, lalu buka folder tujuan lewat 📁 Folder PC "
                  "dan cari duplikat di sana."), parent=self)
            return
        entries, _ = self._actionable(self.filtered_files)  # never shuffle protected files into Duplicates/
        if not entries:
            return
        report = self._reporter()
        self.run_bg(lambda: find_duplicates(entries, self.stop_event,
                                            lambda c, t, phase: report(c, t, T("Mencari duplikat — {} {}/{}",
                                                                               T(phase), f"{c:,}", f"{t:,}"))),
                    self._dup_done, status=T("Mencari duplikat…"), cancellable=True, determinate=True)

    def _dup_done(self, groups):
        if self.stop_event.is_set():
            self.status.set(T("Pencarian duplikat dihentikan."))
        elif not groups:
            self.status.set(T("Tidak ada duplikat — ") + self._summary())
            messagebox.showinfo(T("Tidak ada duplikat"), T("Semua file yang tampil di tabel unik."), parent=self)
        else:
            count = sum(len(g) - 1 for g in groups)
            self.status.set(T("{} duplikat dalam {} grup.", f"{count:,}", f"{len(groups):,}"))
            DuplicateWindow(self, groups, self.source(), self._move_duplicates)

    def _move_duplicates(self, groups):
        source = self.source()
        count = sum(len(g) - 1 for g in groups)
        if not messagebox.askyesno(
                T("Konfirmasi"),
                T("Memindahkan {} file duplikat ke:\n{}\n\n"
                  "File yang disimpan tetap di tempatnya. Tidak ada file yang dihapus.",
                  f"{count:,}", source / DUPLICATES_DIR), parent=self):
            return
        self._start_operation(lambda: duplicate_records(groups, source), "MOVE", "unique", source)

    def open_log(self):
        for candidate in (self.last_log_path, self.dest_root() / LOG_NAME if self.scanned else None):
            if candidate and candidate.exists():
                os.startfile(str(candidate))
                return
        messagebox.showinfo(T("Log belum ada"), T("Log dibuat setelah file dipindahkan atau disalin."), parent=self)


def self_test():
    with tempfile.TemporaryDirectory(prefix="ams_test_") as td:
        root = Path(td)

        # Main files
        files = {
            "a.jpg": b"image",
            "b.mp4": b"video",
            "c.mp3": b"audio",
            "d.pdf": b"pdf",
            "e.docx": b"docx",
            "f.xlsx": b"xlsx",
            "g.pptx": b"pptx",
            "h.zip": b"zip",
            "i.py": b"code",
            "j.bin": b"other",
        }
        for name, data in files.items():
            (root / name).write_bytes(data)

        # Subfolder + excluded folder.
        (root / "Sub").mkdir()
        (root / "Sub" / "inside.jpg").write_bytes(b"x")
        (root / "ExcludeMe").mkdir()
        (root / "ExcludeMe" / "secret.pdf").write_bytes(b"x")
        (root / LOG_NAME).write_text("old log", encoding="utf-8")

        assert classify(root / "a.jpg") == "Images"
        assert classify(root / "b.mp4") == "Videos"
        assert classify(root / "c.mp3") == "Audio"
        assert classify(root / "d.pdf") == "Documents"
        assert classify(root / "e.docx") == "Documents"
        assert classify(root / "f.xlsx") == "Documents"
        assert classify(root / "g.pptx") == "Documents"
        assert classify(root / "h.zip") == "Archives"
        assert classify(root / "i.py") == "Code"
        assert classify(root / "j.bin") == "Other"

        # Android subfolders (local paths and phone-style paths).
        android_cases = {
            "IMG-20240512-WA0001.jpg": "Images/WhatsApp",
            "PTT-20240512-WA0003.opus": "Audio/WhatsApp",
            "DOC-20240512-WA0004.pdf": "Documents/WhatsApp",
            "Screenshot_20240512-101010.png": "Images/Screenshots",
            "Screenshot_20240512_101010_com.whatsapp.jpg": "Images/Screenshots",
            "Screen_Recording_20240512-101010.mp4": "Videos/Screen Recordings",
            "IMG_20240512_101010.jpg": "Images/Camera",
            "PXL_20240512_101010123.jpg": "Images/Camera",
            "20240512_101010.mp4": "Videos/Camera",
            "DCIM/Camera/holiday.jpg": "Images/Camera",
            "20240512_101010.pdf": "Documents",
            "Telegram/Telegram Images/photo.jpg": "Images/Telegram",
            "Recordings/Call/call_mom.m4a": "Audio/Recordings",
            "random.jpg": "Images",
        }
        phone_root = PurePosixPath("Galaxy S23", "Internal shared storage")
        for rel, want in android_cases.items():
            got = destination_label(root / rel, root, True)
            assert got == want, (rel, got, want)
            phone_path = phone_root.joinpath(*rel.split("/"))
            assert destination_label(phone_path, phone_root, True) == want, rel
            e = make_entry(phone_path, 1, 0, phone_root)
            assert entry_label(e, True) == want and entry_label(e, False) == want.split("/")[0]
        assert destination_label(root / "IMG-20240512-WA0001.jpg", root, False) == "Images"
        rec = preview_operations([root / "IMG-20240512-WA0001.jpg"], root, "unique", android=True)
        assert rec[0]["destination"] == root / "Images" / "WhatsApp" / "IMG-20240512-WA0001.jpg"

        # Filter tests.
        all_main = [root / n for n in files]
        entries = [make_entry(p, p.stat().st_size, p.stat().st_mtime, root) for p in all_main]
        filtered = filter_files(entries, None, None, None, None, {".pdf", ".docx", ".xlsx"})
        assert {e.path.suffix.lower() for e in filtered} == {".pdf", ".docx", ".xlsx"}
        assert [e.path.name for e in filter_files(entries, None, None, None, None, set(), "Images")] == ["a.jpg"]
        assert [e.path.name for e in filter_files(entries, None, None, None, None, set(), "", " D.P ")] == ["d.pdf"]
        assert [e.path.name for e in filter_files(entries, None, None, None, None, set(), "Documents", "XLS")] == ["f.xlsx"]

        # Exclusion + recursive discovery; the log file is never picked up.
        excluded = parse_excluded_paths("ExcludeMe", root)
        recursive = {e.path for e in discover_files(root, True, "not_this_script.py", excluded)}
        assert root / "Sub" / "inside.jpg" in recursive
        assert root / "ExcludeMe" / "secret.pdf" not in recursive
        assert root / LOG_NAME not in recursive
        junk_root = root / "junk_test"
        for rel in ("Android/data/com.app/cache.jpg", "Android/obb/game.obb", ".thumbnails/t.jpg",
                    "Android/media/com.whatsapp/WhatsApp/IMG-20240512-WA0001.jpg", "DCIM/.hidden/x.jpg",
                    "DCIM/Camera/IMG_20240512_101010.jpg"):
            (junk_root / rel).parent.mkdir(parents=True, exist_ok=True)
            (junk_root / rel).write_bytes(b"j")
        kept = {e.path.name for e in discover_files(junk_root, True, "x", [], skip_junk=True)}
        assert kept == {"IMG-20240512-WA0001.jpg", "IMG_20240512_101010.jpg"}, kept
        assert len(discover_files(junk_root, True, "x", [])) == 6  # off → everything
        flat = {e.path for e in discover_files(root, False, "not_this_script.py", [])}
        assert root / "Sub" / "inside.jpg" not in flat and root / "a.jpg" in flat

        # Preview must not alter the filesystem.
        before = set(p.relative_to(root).as_posix() for p in root.rglob("*"))
        preview = preview_operations(all_main, root, "unique")
        after = set(p.relative_to(root).as_posix() for p in root.rglob("*"))
        assert before == after
        assert len(preview) == len(all_main)

        # Real MOVE.
        success, skipped, failed, cancelled, logs = execute_operations(
            preview, "MOVE", "unique", threading.Event()
        )
        assert (success, skipped, failed, cancelled) == (10, 0, 0, False), (success, skipped, failed, cancelled)
        assert (root / "Images" / "a.jpg").exists()
        assert (root / "Documents" / "e.docx").exists()
        assert (root / "Documents" / "f.xlsx").exists()
        assert (root / "Documents" / "g.pptx").exists()
        assert (root / "Archives" / "h.zip").exists()
        assert (root / "Code" / "i.py").exists()
        # Category folders are pruned from the next scan.
        assert not any(e.path.parent.name == "Images"
                       for e in discover_files(root, True, "x", []))

        # Conflict unique test.
        (root / "Images" / "same.jpg").write_bytes(b"old")
        src = root / "same.jpg"
        src.write_bytes(b"new")
        rec = preview_operations([src], root, "unique")
        assert rec[0]["destination"].name == "same (1).jpg"
        execute_operations(rec, "MOVE", "unique", threading.Event())
        assert (root / "Images" / "same (1).jpg").exists()

        # Overwrite test.
        (root / "Images" / "over.jpg").write_bytes(b"old")
        src = root / "over.jpg"
        src.write_bytes(b"newer")
        execute_operations(preview_operations([src], root, "overwrite"), "MOVE", "overwrite", threading.Event())
        assert (root / "Images" / "over.jpg").read_bytes() == b"newer" and not src.exists()

        # Skip conflict test.
        (root / "Images" / "skip.jpg").write_bytes(b"old")
        src = root / "skip.jpg"
        src.write_bytes(b"new")
        rec = preview_operations([src], root, "skip")
        s, sk, f, c, _ = execute_operations(rec, "MOVE", "skip", threading.Event())
        assert sk == 1 and f == 0 and src.exists()

        # Cancel test: first file should process, then stop.
        cancel_root = root / "cancel_test"
        cancel_root.mkdir()
        for n in range(5):
            (cancel_root / f"{n}.txt").write_text(str(n), encoding="utf-8")
        cancel_files = list(cancel_root.iterdir())
        rec = preview_operations(cancel_files, cancel_root, "unique")
        ev = threading.Event()
        def cb(cur, total, success, skipped, failed):
            if cur == 1:
                ev.set()
        s, sk, f, cancelled, _ = execute_operations(rec, "MOVE", "unique", ev, cb)
        assert cancelled
        assert s == 1

        # Import path (phone → PC): fetch stages a copy, which is then moved into dest.
        phone = root / "phone_sim"
        phone.mkdir()
        (phone / "IMG-20240512-WA0009.jpg").write_bytes(b"phone")
        dest = root / "dest"
        fetched = []

        def fake_fetch(record):
            fetched.append(record["source"])
            staged = root / "stage" / str(len(fetched)) / record["source"].name
            staged.parent.mkdir(parents=True)
            shutil.copy2(record["source"], staged)
            return staged

        rec = preview_operations([phone / "IMG-20240512-WA0009.jpg"], phone, "skip", True, dest)
        assert rec[0]["destination"] == dest / "Images" / "WhatsApp" / "IMG-20240512-WA0009.jpg"
        s, sk, f, c, _ = execute_operations(rec, "COPY", "skip", threading.Event(), fetch=fake_fetch)
        assert (s, sk, f) == (1, 0, 0) and rec[0]["destination"].read_bytes() == b"phone"
        assert (phone / "IMG-20240512-WA0009.jpg").exists()  # COPY leaves the phone untouched
        assert not (root / "stage" / "1" / "IMG-20240512-WA0009.jpg").exists()  # staged copy moved
        s, sk, f, c, _ = execute_operations(rec, "COPY", "skip", threading.Event(), fetch=fake_fetch)
        assert sk == 1 and len(fetched) == 1  # skipped without reading the phone again

        # Duplicates: same size + same first 64 KiB but different tail must NOT match.
        dup_root = root / "dups"
        dup_root.mkdir()
        head = os.urandom(PARTIAL_HASH_BYTES)
        dup_files = {
            "a1.jpg": b"same", "a2.jpg": b"same", "a3 (1).jpg": b"same", "u.jpg": b"diff",
            "b1.bin": head + b"x", "b2.bin": head + b"y",
            "c1.bin": head + b"z", "c2.bin": head + b"z",
            "empty1.txt": b"", "empty2.txt": b"",
        }
        for name, data in dup_files.items():
            (dup_root / name).write_bytes(data)
        os.utime(dup_root / "a2.jpg", (1_000_000_000, 1_000_000_000))  # oldest → kept
        groups = find_duplicates(discover_files(dup_root, False, "x", []), threading.Event())
        names = sorted(sorted(e.path.name for e in g) for g in groups)
        assert names == [["a1.jpg", "a2.jpg", "a3 (1).jpg"], ["c1.bin", "c2.bin"]], names
        assert groups[0][0].path.suffix == ".bin"  # most bytes wasted first
        a_group = next(g for g in groups if g[0].path.suffix == ".jpg")
        assert a_group[0].path.name == "a2.jpg"
        stopped = threading.Event()
        stopped.set()
        assert find_duplicates(discover_files(dup_root, False, "x", []), stopped) == []

        rec = duplicate_records(groups, dup_root)
        s, sk, f, c, _ = execute_operations(rec, "MOVE", "unique", threading.Event())
        assert (s, sk, f) == (3, 0, 0)
        assert (dup_root / "a2.jpg").exists() and not (dup_root / "a1.jpg").exists()
        assert (dup_root / DUPLICATES_DIR / "a1.jpg").exists()
        assert not find_duplicates(discover_files(dup_root, True, "x", []), threading.Event())

        # Crash-safe log: every row is on disk before the next file starts.
        log_root = root / "log_test"
        log_root.mkdir()
        for n in range(3):
            (log_root / f"{n}.txt").write_text(str(n), encoding="utf-8")
        log_path = log_root / LOG_NAME
        writer = LogWriter(log_path)
        rows_on_disk = []

        def after_each(cur, total, *_):
            rows_on_disk.append(len(log_path.read_text(encoding="utf-8-sig").splitlines()) - 1)

        execute_operations(preview_operations(sorted(log_root.glob("*.txt")), log_root, "unique"),
                           "MOVE", "unique", threading.Event(), after_each, on_record=writer.write)
        writer.close()
        assert rows_on_disk == [1, 2, 3], rows_on_disk  # not only at the end
        writer = LogWriter(log_path)  # reopening appends, no second header / BOM
        writer.write({"time": "t", "action": "MOVE", "status": "OK", "category": "x",
                      "source": "s", "destination": "d", "error": ""})
        writer.close()
        text = log_path.read_text(encoding="utf-8-sig")
        assert text.count("time,action") == 1 and "﻿" not in text and len(text.splitlines()) == 5

        # A fetch may return (path, note): the note lands in the log, status stays OK.
        note_src = root / "note_src.jpg"
        note_src.write_bytes(b"12345")
        rec = preview_operations([note_src], root, "unique", dest_root=root / "note_dest")
        _, _, _, _, logs = execute_operations(rec, "MOVE", "unique", threading.Event(),
                                              fetch=lambda r: (r["source"], "ukuran berbeda"))
        assert logs[0]["status"] == "OK" and logs[0]["error"] == "ukuran berbeda"

        # Protected app data: caught anywhere; ordinary media/documents never caught.
        protected_cases = {
            "Android/media/com.whatsapp/WhatsApp/Databases/msgstore-2026-10-18.1.db.crypt14": True,
            "Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db.crypt15": True,
            "Download/msgstore.db.crypt14": True,
            "WhatsApp Business/Backups/wallpapers.backup": True,
            "Android/media/com.whatsapp/WhatsApp/Backups/chatsettingsbackup.db.crypt1": True,
            "WhatsApp/Databases/wa.db": True,
            "something/app.db-wal": True,
            "DCIM/Camera/.nomedia": True,
            "Download/backup.mcrypt1": True,
            "DCIM/Camera/20261018_192406_SPPG-Ilir Barat Satu Siringagung 3.jpg": False,
            "Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/IMG-20261018-WA0006.jpg": False,
            "Documents/database-notes.pdf": False,
            "Documents/crypto.docx": False,
            "Download/whispry-1.1.0.apk": False,
            "Movies/database.mp4": False,
        }
        for rel, want in protected_cases.items():
            assert bool(protection_reason(rel)) == want, (rel, protection_reason(rel))
            e = make_entry(phone_root.joinpath(*rel.split("/")), 1, 0, phone_root)
            assert bool(e.protected) == want, rel
        assert WHATSAPP_MEDIA.search("Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/x.jpg")
        assert WHATSAPP_MEDIA.search("Android/media/com.whatsapp.w4b/WhatsApp Business/Media/x.jpg")
        assert WHATSAPP_MEDIA.search("WhatsApp/Media/WhatsApp Video/x.mp4")
        assert not WHATSAPP_MEDIA.search("DCIM/Camera/IMG-20240512-WA0001.jpg")

        # Manual exclusions: files and folders, both path styles, persisted, removable.
        ex_path = root / "cfg" / "exclusions.json"
        ex = Exclusions(ex_path)
        phone_file = PurePosixPath("Galaxy", "Internal shared storage", "DCIM", "Camera", "a.jpg")
        pc_file = root / "Pictures" / "b.jpg"
        ex.add_files([phone_file])
        ex.add_folder(root / "Pictures")
        ex2 = Exclusions(ex_path)  # reloaded from disk
        assert ex2.match(phone_file) and ex2.match(pc_file) and ex2.match(root / "Pictures" / "sub" / "c.jpg")
        assert not ex2.match(PurePosixPath("Galaxy", "Internal shared storage", "DCIM", "Camera", "a.jpg2"))
        assert not ex2.match(root / "Pictures2" / "d.jpg")  # a sibling with a longer name is not inside
        ex2.remove([pc_file])  # un-excluding a file inside an excluded folder lifts the folder
        assert not Exclusions(ex_path).match(pc_file) and Exclusions(ex_path).match(phone_file)
        ex2.clear()
        assert len(Exclusions(ex_path)) == 0
        assert len(Exclusions(root / "missing" / "x.json")) == 0  # no file yet → empty, no crash
        (root / "cfg" / "broken.json").write_text("{not json", encoding="utf-8")
        assert len(Exclusions(root / "cfg" / "broken.json")) == 0  # corrupt file → empty, no crash

        # Every text passed to T() (and every key used indirectly) has an English entry with
        # the same {} slots; Indonesian returns the key itself.
        import ast

        def literals(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return [node.value]
            if isinstance(node, ast.IfExp):
                return literals(node.body) + literals(node.orelse)
            if isinstance(node, ast.Dict):
                return [k for v in node.values for k in literals(v)]
            return []

        source_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        keys = {k for n in ast.walk(source_tree)
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "T" and n.args
                for k in literals(n.args[0] if not isinstance(n.args[0], ast.Subscript) else n.args[0].value)}
        keys |= (set(CATEGORY_LABELS.values()) | {"Semua", "dikecualikan", "cek awal file", "hash penuh"}
                 | {r for r, _ in PROTECTED_RULES} | (set(App.HEADINGS.values()) - {"Folder"})
                 | {"Ekstensi", "Dari", "Sampai", "Pindahkan", "Salin", "Buat nama baru", "Lewati", "Timpa"}
                 | set(BRIDGE_MESSAGES))
        missing = sorted(k for k in keys if k not in EN)
        assert not missing, missing
        slots = [k for k in keys if k.count("{}") != EN[k].count("{}")]
        assert not slots, slots
        assert LANG == "English" and T("Batal") == "Cancel" and T("Grup {} — {} file identik", 2, 3) == "Group 2 — 3 identical files"
        assert bridge_message("Tidak ditemukan: DCIM / Camera") == "Not found: DCIM / Camera"
        assert bridge_message("File tidak mulai tersalin dalam 60 detik: a.jpg") == "File did not start copying within 60 s: a.jpg"
        assert bridge_message("Access is denied.") == "Access is denied."  # Windows' own text untouched
        globals()["LANG"] = "Indonesia"
        try:
            assert T("Batal") == "Batal" and bridge_message("Penyalinan macet: x") == "Penyalinan macet: x"
        finally:
            globals()["LANG"] = "English"

        # Throttle keeps the final call.
        calls = []
        t = throttled(lambda cur, total: calls.append(cur), interval=60)
        for i in range(1, 101):
            t(i, 100)
        assert calls == [1, 100], calls

        # Windows Shell bridge (the MTP path), driven against a normal folder:
        # same COM calls, CopyHere/MoveHere copy engine and staging logic.
        if sys.platform == "win32":
            sim = root / "bridge_phone"
            (sim / "DCIM" / "Camera").mkdir(parents=True)
            (sim / "WhatsApp" / "Media").mkdir(parents=True)
            (sim / "DCIM" / "Camera" / "IMG_20240512_101010.jpg").write_bytes(b"cam" * 5000)
            (sim / "WhatsApp" / "Media" / "IMG-20240512-WA0001.jpg").write_bytes(b"wa")
            (sim / "WhatsApp" / "Media" / "foto é 日本.jpg").write_bytes(b"unicode")
            (sim / "backup.zip").write_bytes(b"PK\x05\x06" + b"\0" * 18)  # a file, not a folder
            bridge = ShellBridge()
            try:
                assert isinstance(bridge.dirs(()), list)  # devices under This PC (none attached is fine)
                assert sorted(bridge.dirs((str(sim),))) == ["DCIM", "WhatsApp"]
                listed = bridge.list_files((str(sim),), True)
                by_name = {e.path.name: e for e in listed}
                assert set(by_name) == {"IMG_20240512_101010.jpg", "IMG-20240512-WA0001.jpg",
                                        "foto é 日本.jpg", "backup.zip"}, set(by_name)
                assert by_name["IMG_20240512_101010.jpg"].size == 15000
                real_mtime = (sim / "DCIM" / "Camera" / "IMG_20240512_101010.jpg").stat().st_mtime
                assert abs(by_name["IMG_20240512_101010.jpg"].mtime - real_mtime) < 2, "date must be UTC-correct"
                assert entry_label(by_name["IMG_20240512_101010.jpg"], True) == "Images/Camera"
                assert entry_label(by_name["IMG-20240512-WA0001.jpg"], True) == "Images/WhatsApp"
                assert by_name["backup.zip"].category == "Archives"
                assert [e.path.name for e in bridge.list_files((str(sim),), False)] == ["backup.zip"]
                junk = {e.path.name for e in bridge.list_files((str(junk_root),), True)}
                assert junk == {"IMG-20240512-WA0001.jpg", "IMG_20240512_101010.jpg"}, junk
                assert len(bridge.list_files((str(junk_root),), True, skip_junk=False)) == 6
                seen = []
                bridge.list_files((str(junk_root),), True, lambda n, line: seen.append(line))
                assert all(line.count("\t") == 2 and "/" in line for line in seen), seen  # size, mtime, rel path
                try:
                    bridge.dirs((str(sim), "nope"))
                    raise AssertionError("missing folder must raise")
                except RuntimeError:
                    pass

                bdest = root / "bridge_dest"
                rec = preview_operations([e.path for e in listed], PurePosixPath(str(sim)),
                                         "unique", True, bdest)
                sizes = {e.path: e.size for e in listed}
                n = itertools.count()
                for mode in ("COPY", "MOVE"):
                    s, sk, f, c, logs = execute_operations(
                        rec, mode, "unique", threading.Event(),
                        fetch=lambda r: bridge.fetch(r["source"], sizes[r["source"]],
                                                     bdest / STAGING_DIR / str(next(n)), mode == "MOVE"))
                    assert (s, sk, f) == (4, 0, 0), logs
                remove_empty_dirs(bdest / STAGING_DIR)
                assert (bdest / "Images" / "Camera" / "IMG_20240512_101010.jpg").read_bytes() == b"cam" * 5000
                assert (bdest / "Images" / "Camera" / "IMG_20240512_101010 (1).jpg").exists()  # 2nd run → unique
                assert (bdest / "Images" / "WhatsApp" / "foto é 日本.jpg").read_bytes() == b"unicode"
                assert not (bdest / STAGING_DIR).exists()
                assert not any(p.is_file() for p in sim.rglob("*")), "MOVE must empty the source"
            finally:
                bridge.close()

        print("SELF-TEST PASSED")
        print("Protected app data + manual exclusions: OK")
        print("Crash-safe row-by-row log: OK")
        print("Classification: OK")
        print("Android subfolders: OK")
        print("PDF/DOCX/XLSX/PPTX: OK")
        print("Filters (incl. category + search): OK")
        print("Exclude folders: OK")
        print("Dry run non-destructive: OK")
        print("Automatic folders + MOVE: OK")
        print("Conflict unique/skip/overwrite: OK")
        print("STOP/cancel: OK")
        print("Phone import via staging: OK")
        print("Duplicates (size → partial → full hash): OK")
        if sys.platform == "win32":
            print("Windows Shell / MTP bridge (copy + move, unicode): OK")
        print("Log-ready records: OK")
        print("English/Indonesian texts: OK")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        if sys.platform == "win32":
            try:  # crisp text on scaled displays instead of a blurry bitmap stretch
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                pass
            # Own taskbar identity, else Windows groups the window under python.exe and shows Python's icon.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AndroidMediaSeparator")
        App().mainloop()
