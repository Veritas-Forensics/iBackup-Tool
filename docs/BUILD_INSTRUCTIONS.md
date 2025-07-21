# Build Instructions

This document provides instructions for building iDevice Manager from source code for both Windows and macOS platforms.

## Prerequisites

### General Requirements
- Python 3.8 or higher
- Git (for cloning the repository)
- iOS device for testing (optional but recommended)

### Windows Requirements
- Windows 10 or later
- Visual Studio Build Tools or Visual Studio Community (for compiling native dependencies)
- Windows SDK

### macOS Requirements
- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools
- Homebrew (recommended for dependency management)

## Building on Windows

### Quick Build
1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project directory
3. Run the build script:
   ```batch
   scripts\build_windows.bat
   ```

### Manual Build Steps
1. **Create Virtual Environment**
   ```batch
   python -m venv build_env
   build_env\Scripts\activate.bat
   ```

2. **Install Dependencies**
   ```batch
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Build Executable**
   ```batch
   pyinstaller --onefile --windowed --name "iDevice_Manager" idevice_manager/main.py
   ```

4. **Output Location**
   - Executable: `dist\iDevice_Manager.exe`

## Building on macOS

### Quick Build
1. Open Terminal
2. Navigate to the project directory
3. Run the build script:
   ```bash
   ./scripts/build_macos.sh
   ```

### Manual Build Steps
1. **Install Xcode Command Line Tools** (if not already installed)
   ```bash
   xcode-select --install
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv build_env
   source build_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. **Build Application Bundle**
   ```bash
   pyinstaller --onefile --windowed --name "iDevice Manager" \
     --osx-bundle-identifier "com.idevicemanager.app" \
     idevice_manager/main.py
   ```

5. **Output Location**
   - Application Bundle: `dist/iDevice Manager.app`

## Creating Distribution Packages

### Windows Installer
To create a Windows installer, you can use tools like:
- **Inno Setup** (recommended)
- **NSIS**
- **WiX Toolset**

### macOS DMG
To create a macOS DMG installer:
1. Install create-dmg:
   ```bash
   brew install create-dmg
   ```

2. Create DMG:
   ```bash
   create-dmg \
     --volname "iDevice Manager" \
     --window-pos 200 120 \
     --window-size 600 300 \
     --icon-size 100 \
     --icon "iDevice Manager.app" 175 120 \
     --hide-extension "iDevice Manager.app" \
     --app-drop-link 425 120 \
     "iDevice Manager.dmg" \
     dist/
   ```

## Build Customization

### PyInstaller Options
You can customize the build by modifying the PyInstaller command with these common options:

- `--icon=path/to/icon.ico` - Set application icon
- `--add-data "src:dest"` - Include additional files
- `--exclude-module module` - Exclude unnecessary modules
- `--upx-dir /path/to/upx` - Use UPX compression
- `--debug` - Create debug build

### Creating Spec Files
For advanced customization, create a `.spec` file:
```bash
pyinstaller --onefile idevice_manager/main.py
# Edit the generated main.spec file
pyinstaller main.spec
```

## Troubleshooting

### Common Issues

**Windows:**
- **Missing Visual Studio Build Tools**: Install from Microsoft website
- **SSL Certificate Errors**: Update certificates or use `--trusted-host` with pip
- **Permission Denied**: Run as Administrator

**macOS:**
- **Command Line Tools Missing**: Run `xcode-select --install`
- **Permission Issues**: Use `sudo` carefully or fix permissions
- **Library Not Found**: Install missing dependencies with Homebrew

### Dependency Issues
If you encounter dependency conflicts:
1. Delete the virtual environment
2. Create a fresh environment
3. Install dependencies one by one
4. Check for platform-specific requirements

### Performance Optimization
- Use `--exclude-module` to remove unused libraries
- Enable UPX compression for smaller executables
- Consider using `--onedir` instead of `--onefile` for faster startup

## Testing the Build

### Functional Testing
1. **Device Detection**: Connect an iOS device and verify detection
2. **Screenshot Capture**: Test screenshot functionality
3. **UI Responsiveness**: Check all buttons and menus
4. **Error Handling**: Test with no device connected

### Distribution Testing
1. **Clean Environment**: Test on a machine without development tools
2. **Different OS Versions**: Test on various Windows/macOS versions
3. **Antivirus Compatibility**: Verify antivirus software doesn't flag the executable

## Continuous Integration

For automated builds, consider setting up CI/CD with:
- **GitHub Actions**
- **Azure DevOps**
- **Jenkins**

Example GitHub Actions workflow files can be found in the `.github/workflows/` directory.

## Support

If you encounter issues during the build process:
1. Check this documentation
2. Review the error logs
3. Open an issue on the GitHub repository
4. Include your OS version, Python version, and error details