# Contributing to PassZen 🤝

Thank you for your interest in contributing to **PassZen**! PassZen is an open-source, local-first desktop password manager dedicated to simplicity, transparency, and rock-solid privacy.

Whether you are reporting bugs, proposing new features, fixing security vulnerabilities, or improving documentation, all contributions are warmly welcomed!

---

## Code of Conduct

- Be respectful, constructive, and inclusive.
- Focus on what is best for the community and users' security.
- Treat bug reports and code reviews with empathy and care.

---

## Security Vulnerabilities 🚨

Because PassZen is a cryptographic security tool, please report any suspected vulnerabilities or cryptographic weaknesses responsibly.
- Do **not** open a public issue for zero-day security vulnerabilities.
- Please email the maintainer directly at **ayushkumarshaw980@gmail.com** or open a private security advisory on GitHub.

---

## Development Workflow

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Fork & Clone
```bash
# Fork the repository on GitHub, then clone your fork:
git clone https://github.com/<your-username>/pass-zen.git
cd pass-zen
```

### 3. Create a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
# Install runtime & development dependencies
pip install -r requirements-dev.txt
```

### 5. Running the App Locally
```bash
python main.py
```

### 6. Code Style & Guidelines
- Follow [PEP 8](https://peps.python.org/pep-0008/) naming conventions and formatting.
- Keep dependencies minimal to ensure PassZen remains lightweight and easily auditable.
- Cryptographic code in `src/crypto/` must strictly use well-vetted primitives (never roll custom ciphers).
- UI code should respect the central theme system defined in `src/ui/theme.py`.

---

## Submitting a Pull Request (PR)

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```
2. Commit your changes with clear, concise commit messages:
   ```bash
   git commit -m "feat(generator): add support for custom separator characters"
   ```
3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
4. Open a Pull Request against the `main` branch of `theayushgupta08/pass-zen`.
5. Provide a clear summary of what was changed and why.

---

## Ideas for Contributions
- [ ] Biometric unlock support (Windows Hello / macOS Touch ID)
- [ ] Password breach checking (via k-Anonymity HIBP API)
- [ ] Additional localized language translations
- [ ] Linux system tray minimization
- [ ] Browser extension companion

Thank you for helping make PassZen even better! 🚀
