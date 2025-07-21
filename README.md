# iDevice Manager

A professional PyQt6-based iOS device management application that provides comprehensive utilities for interacting with iOS devices via USB connection.

## Features

- iOS device detection and connection
- Screenshot capture
- Device information display
- Backup management
- SpringBoard services integration
- Cross-platform support (Windows & macOS)

## Requirements

- Python 3.8+
- iOS device with USB connection
- iTunes (required for device drivers and connection)
- macOS or Windows

## Installation

### Option 1: From Source
1. Clone the repository:
```bash
git clone <repository-url>
cd usb_connect
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Development Installation
```bash
pip install -e .
```

## Usage

### Running from Source
```bash
python -m idevice_manager.main
```

### Using the Launcher
```bash
python idevice_manager/utils/launcher.py
```

### If Installed as Package
```bash
idevice-manager
```

## Development

### Project Structure
```
usb_connect/
├── idevice_manager/          # Main package
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── gui/                 # GUI components
│   ├── core/                # Core functionality
│   └── utils/               # Utilities
├── docs/                    # Documentation
├── scripts/                 # Build scripts
├── tests/                   # Unit tests
├── assets/                  # Icons, resources
├── binary/                  # Pre-built binaries
└── setup.py                 # Package setup
```

## Building

### Quick Build
- **Windows**: Run `scripts\build_windows.bat`
- **macOS**: Run `./scripts/build_macos.sh`

### Detailed Instructions
See [Build Instructions](docs/BUILD_INSTRUCTIONS.md) for comprehensive build documentation.

## Dependencies

- PyQt6 (GUI framework)
- pymobiledevice3 (iOS device communication)
- Pillow (Image processing)
- cryptography (Secure communication)

## License

See [LICENSE](LICENSE) file for details.

## Documentation

Additional documentation can be found in the `docs/` directory:
- [Build Instructions](docs/BUILD_INSTRUCTIONS.md)