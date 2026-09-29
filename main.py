"""
PassZen — Desktop Password Manager
Entry point.
"""

import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import PassZenApp


def main():
    app = PassZenApp()
    app.run()


if __name__ == "__main__":
    main()
