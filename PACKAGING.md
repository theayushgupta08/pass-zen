# 📦 PassZen — Packaging & Distribution Guide

## Overview

This guide covers how to package PassZen into installable files for **Windows**, **macOS**, and **Linux** so anyone can download, install, and use it — no Python required.

---

## Strategy

```
┌──────────────┐     ┌──────────────┐     ┌───────────────────────┐
│  Python Code  │ ──▶ │  PyInstaller  │ ──▶ │  Standalone Executable │
│  (pass-zen/)  │     │  (bundler)    │     │  (no Python needed)    │
└──────────────┘     └──────────────┘     └──────────┬────────────┘
                                                      │
                          ┌───────────────────────────┼───────────────────────────┐
                          ▼                           ▼                           ▼
                   ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
                   │   Windows     │           │    macOS      │           │    Linux      │
                   │  Inno Setup   │           │  .dmg bundle  │           │   AppImage    │
                   │  → .exe       │           │  → .dmg       │           │   → .AppImage │
                   │  installer    │           │  installer    │           │   (portable)  │
                   └──────────────┘           └──────────────┘           └──────────────┘
```

| Platform | Output | Tool |
|----------|--------|------|
| Windows | `PassZen-Setup.exe` (installer) | PyInstaller + Inno Setup |
| macOS | `PassZen.dmg` (disk image) | PyInstaller + create-dmg |
| Linux | `PassZen.AppImage` (portable) | PyInstaller + appimagetool |

---

## Step 1: Install Build Dependencies

```bash
pip install -r requirements-dev.txt
```

---

## Step 2: App Icons

Platform-specific icons are stored in `assets/`:
```
assets/
├── icon.ico      # Windows
├── icon.icns     # macOS
└── icon.png      # Linux (256x256)
```

---

## Step 3: PyInstaller Build (Creates Standalone Executable)

Run the build script from the project root:

```bash
python build.py
```

Output:
- **Windows**: `dist/PassZen.exe`
- **macOS**: `dist/PassZen.app`
- **Linux**: `dist/PassZen`

---

## Step 4: Create Platform Installers

### 🪟 Windows — Inno Setup Installer

[Inno Setup](https://jrsoftware.org/isinfo.php) creates `.exe` installers with:
- Install/uninstall wizard
- Desktop shortcut
- Start Menu entry
- Custom install directory

1. Download and install [Inno Setup](https://jrsoftware.org/isdl.php).
2. Build the binary first: `python build.py`.
3. Open `installer/windows/passzen_installer.iss` in Inno Setup.
4. Click **Build > Compile**.
5. Output: `installer/windows/Output/PassZen-Setup.exe`.

### 🍎 macOS — .dmg Disk Image

1. Build on macOS: `python build.py`.
2. Install `create-dmg` (via Homebrew):
   ```bash
   brew install create-dmg
   ```
3. Create the DMG:
   ```bash
   create-dmg \
     --volname "PassZen" \
     --volicon "assets/icon.icns" \
     --window-pos 200 120 \
     --window-size 600 400 \
     --icon-size 100 \
     --icon "PassZen.app" 175 190 \
     --app-drop-link 425 190 \
     "dist/PassZen.dmg" \
     "dist/PassZen.app"
   ```

### 🐧 Linux — AppImage (Universal)

AppImage runs on virtually all Linux distributions without installation.

1. Build on Linux: `python build.py`.
2. Create AppImage structure:
   ```bash
   mkdir -p PassZen.AppDir/usr/bin
   mkdir -p PassZen.AppDir/usr/share/icons/hicolor/256x256/apps

   cp dist/PassZen PassZen.AppDir/usr/bin/
   cp assets/icon.png PassZen.AppDir/usr/share/icons/hicolor/256x256/apps/passzen.png
   cp installer/linux/passzen.desktop PassZen.AppDir/
   cp assets/icon.png PassZen.AppDir/passzen.png
   ln -s usr/bin/PassZen PassZen.AppDir/AppRun

   # Download appimagetool
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage

   # Build the AppImage
   ./appimagetool-x86_64.AppImage PassZen.AppDir dist/PassZen.AppImage
   ```

---

## Step 5: Automated Releases via GitHub Actions

The repository includes a ready-to-use CI/CD workflow at `.github/workflows/build.yml`.

When you push a version tag to your GitHub repository:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically compile on Windows, macOS, and Ubuntu virtual runners and attach all three installers to a new GitHub Release for users to download.
