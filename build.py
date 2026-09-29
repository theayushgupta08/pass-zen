"""
PassZen Build Script — Creates standalone executables with PyInstaller.

Usage:
    python build.py

Output:
    dist/PassZen.exe    (Windows)
    dist/PassZen.app    (macOS)
    dist/PassZen        (Linux)
"""

import os
import sys
import platform
import subprocess
import shutil

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ── Configuration ────────────────────────────────────────────────────────────

APP_NAME = "PassZen"
MAIN_SCRIPT = "main.py"
ASSETS_DIR = "assets"

# Platform-specific icon
ICONS = {
    "Windows": os.path.join(ASSETS_DIR, "icon.ico"),
    "Darwin": os.path.join(ASSETS_DIR, "icon.icns"),
    "Linux": os.path.join(ASSETS_DIR, "icon.png"),
}


def get_separator():
    """Get the PyInstaller --add-data separator for the current OS."""
    return ";" if platform.system() == "Windows" else ":"


def clean_build():
    """Remove previous build artifacts."""
    for folder in ["build", "dist", f"{APP_NAME}.spec"]:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        elif os.path.isfile(folder):
            os.remove(folder)
    print("✅ Cleaned previous build artifacts.")


def build():
    """Run PyInstaller to create the executable."""
    system = platform.system()
    sep = get_separator()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
    ]

    # Add icon if it exists
    icon_path = ICONS.get(system, "")
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
        print(f"  Using icon: {icon_path}")

    # Add assets directory if it exists
    if os.path.isdir(ASSETS_DIR):
        cmd.extend(["--add-data", f"{ASSETS_DIR}{sep}{ASSETS_DIR}"])
        print(f"  Bundling assets: {ASSETS_DIR}/")

    # Hidden imports that PyInstaller might miss
    hidden_imports = [
        "cryptography",
        "cryptography.hazmat.primitives.ciphers.aead",
        "cryptography.hazmat.primitives.kdf.pbkdf2",
        "pyperclip",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    cmd.append(MAIN_SCRIPT)

    print(f"\n🔨 Building {APP_NAME} for {system}...")
    print(f"  Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        # Determine output path
        if system == "Windows":
            output = os.path.join("dist", f"{APP_NAME}.exe")
        elif system == "Darwin":
            output = os.path.join("dist", f"{APP_NAME}.app")
        else:
            output = os.path.join("dist", APP_NAME)

        if os.path.exists(output):
            size_mb = os.path.getsize(output) / (1024 * 1024) if os.path.isfile(output) else 0
            print(f"\n✅ Build successful!")
            print(f"  Output: {os.path.abspath(output)}")
            if size_mb > 0:
                print(f"  Size:   {size_mb:.1f} MB")
        else:
            print(f"\n✅ Build completed. Check the dist/ folder.")
    else:
        print(f"\n❌ Build failed with exit code {result.returncode}")
        sys.exit(1)


def main():
    print("=" * 60)
    print(f"  🔐 {APP_NAME} — Build Script")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print(f"  Python:   {sys.version.split()[0]}")
    print("=" * 60)

    # Check PyInstaller is installed
    try:
        import PyInstaller
        print(f"  PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("\n❌ PyInstaller is not installed.")
        print("  Install it with: pip install pyinstaller")
        sys.exit(1)

    print()

    clean_build()
    build()

    print("\n" + "=" * 60)
    print("  📦 Next steps:")
    print("  • Windows: Run Inno Setup on installer/windows/passzen_installer.iss")
    print("  • macOS:   Run create-dmg on dist/PassZen.app")
    print("  • Linux:   Create AppImage from dist/PassZen")
    print("=" * 60)


if __name__ == "__main__":
    main()
