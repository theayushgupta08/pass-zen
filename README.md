<div align="center">

# 🔐 PassZen

**A lightweight, local-first, zero-knowledge desktop password manager.**  
*Generate strong passwords or securely store existing credentials — fully encrypted with AES-256-GCM right on your PC.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/theayushgupta08/pass-zen)
[![Encryption](https://img.shields.io/badge/encryption-AES--256--GCM-green.svg)](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
[![Key Derivation](https://img.shields.io/badge/kdf-PBKDF2--HMAC--SHA256%20(600k)-orange.svg)](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

[Downloads](#-download--install) • [Features](#-features) • [Security & Encryption](#-security--encryption) • [Getting Started](#-getting-started) • [Contributing](#-contributing)

</div>

---

## 💡 Why PassZen?

Most modern password managers require expensive subscriptions, force you onto closed cloud servers, or sell browser tracking. **PassZen takes the opposite approach:**

- 🛡️ **100% Local-First & Zero-Knowledge:** Your passwords never leave your computer. There are zero servers, zero telemetry, and zero tracking cookies.
- ⚡ **Minimalist & Streamlined:** Only requires **2 inputs** to generate & store a password (*Website, Username*), or **3 inputs** to store an existing password (*Website, Username, Password*).
- 🔒 **Military-Grade Authenticated Encryption:** Built with **AES-256-GCM** (Galois/Counter Mode) and PBKDF2-HMAC-SHA256 with **600,000 rounds** (matching OWASP recommendations).
- 🪟 **Universal Cross-Platform:** Standalone native desktop application for **Windows**, **macOS**, and **Linux**. No browser extensions or Python runtimes required.

---

## ✨ Features

- **⚡ Generate or Store Modes:**
  - *Generate Mode:* Enter Website + Username/Email $\to$ instant cryptographically strong password created and stored.
  - *Store Mode:* Enter Website + Username/Email + Password $\to$ securely saved into your encrypted vault.
- **🛡️ 6-Digit Master PIN + Key Derivation:** Simple 6-digit unlock PIN hardened against brute force via 600,000 PBKDF2 iterations with a unique 32-byte cryptographic salt.
- **⏳ Auto-Lock on Inactivity:** Automatically locks the vault and purges keys from memory after 3 minutes of idle time.
- **🚨 Progressive Lockout Protection:** Defends against physical access brute-forcing by introducing escalating lockouts (30s $\to$ 1m $\to$ 5m) after failed PIN attempts.
- **📋 Clipboard Auto-Clear:** Automatically purges sensitive passwords from your system clipboard after 30 seconds to prevent clipboard snooping.
- **📊 Real-time Strength Meter:** Instant entropy and strength feedback (Very Weak, Weak, Fair, Strong, Very Strong).
- **🔍 Fast Search & Filter:** Instant search across website names, usernames, and customizable category tags.
- **📦 Encrypted Backups (.passzen):** Export and import your entire encrypted vault to portable `.passzen` files for safe offline backups or device migration.
- **🔑 Account Recovery:** Reset PIN using a personal security question or a cryptographically generated 24-character master recovery key.

---

## 🔒 Security & Encryption Architecture

PassZen follows the principle of **defense in depth**:

```
User Master PIN (6 Digits)
         │
         ▼
[PBKDF2-HMAC-SHA256] ── (600,000 iterations + 32-byte unique OS salt)
         │
         ▼
Master Encryption Key (256-bit)
         │
         ▼
[AES-256-GCM Authenticated Encryption] ── (Unique 96-bit Nonce per field)
         │
         ▼
Encrypted SQLite Database (%APPDATA%/PassZen or ~/.config/passzen)
```

| Security Layer | Implementation Details |
|---|---|
| **Cipher** | AES-256-GCM (Authenticated Encryption with Associated Data) |
| **KDF** | PBKDF2-HMAC-SHA256 with **600,000 iterations** (OWASP 2024+ recommendation) |
| **Salt** | Cryptographically secure 32-byte random salt generated via `os.urandom()` |
| **Integrity** | 16-byte GCM authentication tag protects against unauthorized database tampering |
| **Per-Entry Nonce** | Every single encrypted field uses a distinct, unique 12-byte (96-bit) initialization nonce |
| **Zero Plaintext** | Passwords are never written to disk unencrypted, and cleartext keys are flushed from memory on lock |

---

## 📥 Download & Install

### Option A: Standalone Installers (Recommended for Users)

Download the latest version from [GitHub Releases](https://github.com/theayushgupta08/pass-zen/releases):

| Operating System | Download File | Description |
|---|---|---|
| **Windows** | `PassZen-Setup.exe` or `PassZen.exe` | Self-contained installer or portable `.exe` (No Python needed) |
| **macOS** | `PassZen.dmg` | Drag-and-drop installer for Apple Silicon & Intel Macs |
| **Linux** | `PassZen.AppImage` | Universal binary compatible with Ubuntu, Debian, Fedora, Arch, etc. |

### Option B: Running from Source (Developers)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theayushgupta08/pass-zen.git
   cd pass-zen
   ```

2. **Set up a Python virtual environment (Python 3.10+):**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch PassZen:**
   ```bash
   python main.py
   ```

---

## 🚀 Getting Started

### 1. First-Time Setup
1. Launch **PassZen**.
2. Set your **6-digit Master PIN** and confirm it.
3. Choose a **Security Question & Answer** for recovery.
4. **Important:** Copy and securely save your **24-Character Recovery Key** shown on the screen. This key is your failsafe to recover your vault if you ever forget your PIN!

### 2. Generating & Storing Passwords
- **Generate a new password:** Select **Generate & Store**, enter the website name (e.g., `GitHub`) and username/email. PassZen will generate a cryptographically secure password with customized length and character sets.
- **Store an existing password:** Select **Store Existing**, input your credentials, and click **Save**.

### 3. Copying & Security
- Click the **Copy** icon next to any password.
- A 30-second security countdown begins, after which your clipboard is wiped automatically.

---

## 🛠️ Building Standalone Binaries & Installers

PassZen includes built-in scripts to compile standalone binaries without Python:

```bash
# Install packaging tools
pip install -r requirements-dev.txt

# Run cross-platform build
python build.py
```

The output will be placed in `dist/PassZen.exe` (Windows), `dist/PassZen.app` (macOS), or `dist/PassZen` (Linux).

For detailed steps on creating setup wizards, DMGs, or AppImages, read [PACKAGING.md](PACKAGING.md).

---

## 📁 Repository Structure

```
pass-zen/
├── .github/
│   └── workflows/
│       └── build.yml             # Automated multi-OS GitHub Actions CI/CD
├── assets/                       # App icons (.ico, .icns, .png)
├── installer/
│   ├── windows/                  # Inno Setup wizard (.iss)
│   └── linux/                    # Linux .desktop configuration
├── src/
│   ├── config.py                 # Paths, constants, and OS detection
│   ├── app.py                    # Main window controller and lifecycle
│   ├── crypto/                   # AES-256-GCM, PBKDF2, Password generator
│   ├── storage/                  # SQLite encrypted database engine
│   ├── models/                   # Password entry data models
│   ├── utils/                    # Clipboard, inactivity monitor, settings
│   └── ui/
│       ├── theme.py              # Dark theme palette and styling
│       ├── components/           # Custom reusable widgets
│       └── screens/              # Setup, Login, Dashboard, Add, Edit, Settings
├── build.py                      # Standalone PyInstaller build script
├── main.py                       # Application entry point
├── PACKAGING.md                  # Comprehensive packaging & installer guide
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # MIT License
└── requirements.txt              # Core dependencies
```

---

## 🤝 Contributing

Contributions make the open-source community a fantastic place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

1. **Fork the Project** (`https://github.com/theayushgupta08/pass-zen`)
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'feat: Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please review our [CONTRIBUTING.md](CONTRIBUTING.md) for code conventions, security guidelines, and project roadmap.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 👨‍💻 Author

Created and maintained by **[Ayush Gupta](https://github.com/theayushgupta08)**.

*If you find PassZen helpful, feel free to give the repository a ⭐ on GitHub!*
