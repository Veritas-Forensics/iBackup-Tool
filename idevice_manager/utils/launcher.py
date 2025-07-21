#!/usr/bin/env python3
"""
iDevice Manager - Auto-Installing Launcher
This launcher automatically checks and installs dependencies before starting the main application.
"""

import sys
import os
import subprocess
import platform
import threading
import time
from pathlib import Path

# Import winreg for Windows registry access (Windows only)
try:
    import winreg
except ImportError:
    winreg = None  # Not available on non-Windows systems

# Try to import tkinter (built into Python)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Tkinter not available - falling back to console mode")

class DependencyInstaller:
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        self.python_installed = False
        self.python_executable = None
        
        # Check for Python installation
        self.check_and_setup_python()
        
        self.venv_path = Path("venv")
        self.requirements = [
            "PyQt6>=6.4.0",
            "pymobiledevice3>=3.0.0",
            "Pillow>=9.0.0",
            "cryptography>=36.0.0",
            "requests>=2.28.0",
            "six>=1.16.0"
        ]
    
    def check_and_setup_python(self):
        """Check if Python is installed, set up executable path."""
        if getattr(sys, 'frozen', False):
            # We're running in a PyInstaller bundle
            print(f"DEBUG: Running as compiled executable: {sys.executable}")
            # Try to find Python executable in the system
            import shutil
            python_path = shutil.which('python')
            if not python_path:
                python_path = shutil.which('python3')
            if not python_path:
                python_path = shutil.which('pythonw')
            
            if python_path:
                self.python_executable = python_path
                self.python_installed = True
                print(f"DEBUG: Found Python executable: {self.python_executable}")
            else:
                print("DEBUG: No Python interpreter found on system")
                self.python_installed = False
                # We'll install Python later if needed
        else:
            # Running as script
            self.python_executable = sys.executable
            self.python_installed = True
            print(f"DEBUG: Running as script with: {self.python_executable}")
    
    def download_file(self, url, filepath, progress_callback=None):
        """Download a file with progress reporting."""
        import urllib.request
        import urllib.error
        
        def report_progress(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                progress_callback(f"Downloading... {percent}%")
        
        try:
            urllib.request.urlretrieve(url, filepath, reporthook=report_progress)
            return True
        except urllib.error.URLError as e:
            if progress_callback:
                progress_callback(f"Download failed: {e}")
            return False
    
    def install_python_windows(self, progress_callback=None):
        """Download and install Python on Windows."""
        if not self.is_windows:
            return True, "Not Windows - skipping Python installation"
        
        if progress_callback:
            progress_callback("Downloading Python installer...")
        
        # Download Python installer
        python_version = "3.11.7"  # Stable version
        python_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-amd64.exe"
        installer_path = Path("python_installer.exe")
        
        try:
            # Download Python installer
            if not self.download_file(python_url, installer_path, progress_callback):
                return False, "Failed to download Python installer"
            
            if progress_callback:
                progress_callback("Installing Python... This may take a few minutes.")
            
            # Run Python installer silently
            kwargs = {}
            if self.is_windows:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            # Install Python with specific options
            install_cmd = [
                str(installer_path),
                "/quiet",  # Silent installation
                "InstallAllUsers=0",  # Install for current user only
                "PrependPath=1",  # Add to PATH
                "Include_test=0",  # Don't install test suite
                "Include_pip=1",  # Install pip
                "Include_tcltk=1",  # Install tkinter
                "Include_launcher=1",  # Install py launcher
                "InstallLauncherAllUsers=0"  # Launcher for current user
            ]
            
            result = subprocess.run(install_cmd, **kwargs)
            
            # Clean up installer
            if installer_path.exists():
                installer_path.unlink()
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback("Python installed successfully! Refreshing environment...")
                
                # Refresh the PATH and find Python
                self.refresh_python_path()
                return True, "Python installed successfully"
            else:
                return False, f"Python installation failed with code {result.returncode}"
                
        except Exception as e:
            # Clean up installer if it exists
            if installer_path.exists():
                installer_path.unlink()
            return False, f"Python installation error: {e}"
    
    def refresh_python_path(self):
        """Refresh the PATH and find Python executable after installation."""
        import shutil
        import os
        
        # Force refresh of PATH environment variable
        if self.is_windows and winreg:
            # On Windows, we need to refresh the PATH from registry
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
                    user_path, _ = winreg.QueryValueEx(key, "PATH")
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_READ) as key:
                    system_path, _ = winreg.QueryValueEx(key, "PATH")
                
                # Update current process PATH
                os.environ["PATH"] = user_path + ";" + system_path + ";" + os.environ.get("PATH", "")
            except Exception as e:
                print(f"DEBUG: Registry access failed: {e}")
                pass  # If registry access fails, continue with current PATH
        
        # Try to find Python again
        python_path = shutil.which('python')
        if not python_path:
            python_path = shutil.which('python3')
        if not python_path:
            python_path = shutil.which('pythonw')
        
        if python_path:
            self.python_executable = python_path
            self.python_installed = True
            print(f"DEBUG: Found Python after installation: {self.python_executable}")
        else:
            print("DEBUG: Python still not found after installation")
    
    def ensure_python_available(self, progress_callback=None):
        """Ensure Python is available, install if necessary."""
        if self.python_installed and self.python_executable:
            return True, f"Python is available at {self.python_executable}"
        
        if progress_callback:
            progress_callback("Python not found. Installing Python...")
        
        if self.is_windows:
            success, message = self.install_python_windows(progress_callback)
            if not success:
                return False, f"Failed to install Python: {message}"
        else:
            return False, "Automatic Python installation only supported on Windows"
        
        # Verify Python is now available
        if not self.python_installed or not self.python_executable:
            return False, "Python installation completed but Python still not found"
        
        return True, "Python is now available"
        
    def check_python_version(self):
        """Check if Python version meets requirements."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            return False, f"Python 3.8+ required. Current: {version.major}.{version.minor}.{version.micro}"
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    
    def check_pip_available(self):
        """Check if pip is available."""
        try:
            # Hide console window on Windows
            kwargs = {}
            if self.is_windows:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            subprocess.run([self.python_executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True, **kwargs)
            return True, "pip is available"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "pip is not available"
    
    def create_virtual_environment(self, progress_callback=None):
        """Create virtual environment if it doesn't exist."""
        if self.venv_path.exists():
            if progress_callback:
                progress_callback("Virtual environment already exists")
            return True, "Virtual environment already exists"
        
        try:
            if progress_callback:
                progress_callback("Creating virtual environment...")
            
            # Hide console window on Windows
            kwargs = {}
            if self.is_windows:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            subprocess.run([self.python_executable, "-m", "venv", "venv"], 
                         check=True, capture_output=True, **kwargs)
            
            if progress_callback:
                progress_callback("Virtual environment created successfully")
            return True, "Virtual environment created successfully"
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create virtual environment: {e}"
            if progress_callback:
                progress_callback(error_msg)
            return False, error_msg
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment."""
        if self.is_windows:
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pythonw(self):
        """Get path to Python GUI executable in virtual environment (Windows only)."""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pythonw.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get path to pip executable in virtual environment."""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def install_system_dependencies_macos(self, progress_callback=None):
        """Install system dependencies on macOS using Homebrew."""
        if not self.is_macos:
            return True, "Not macOS - skipping system dependencies"
        
        try:
            # Check if brew is installed
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            if progress_callback:
                progress_callback("Homebrew not found - installing...")
            
            # Install Homebrew
            try:
                install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                subprocess.run(install_cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                return False, "Failed to install Homebrew"
        
        # Install system libraries
        packages = ["libusb", "libimobiledevice", "usbmuxd"]
        for package in packages:
            if progress_callback:
                progress_callback(f"Installing {package}...")
            try:
                subprocess.run(["brew", "install", package], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                # Package might already be installed
                pass
        
        return True, "System dependencies installed"
    
    def install_python_dependencies(self, progress_callback=None):
        """Install Python dependencies in virtual environment."""
        venv_python = self.get_venv_python()
        
        # Upgrade pip first using python -m pip
        if progress_callback:
            progress_callback("Upgrading pip...")
        try:
            # Hide console window on Windows
            kwargs = {}
            if self.is_windows:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True, check=True, **kwargs)
        except subprocess.CalledProcessError:
            pass  # Continue even if pip upgrade fails
        
        # Install each requirement using python -m pip
        for i, requirement in enumerate(self.requirements, 1):
            package_name = requirement.split(">=")[0]
            if progress_callback:
                progress_callback(f"Installing {package_name} ({i}/{len(self.requirements)})...")
            
            try:
                # Hide console window on Windows
                kwargs = {}
                if self.is_windows:
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                result = subprocess.run([str(venv_python), "-m", "pip", "install", requirement], 
                                      capture_output=True, text=True, **kwargs)
                if result.returncode != 0:
                    return False, f"Failed to install {requirement}: {result.stderr}"
            except subprocess.CalledProcessError as e:
                return False, f"Failed to install {requirement}: {e}"
        
        return True, "All Python dependencies installed successfully"
    
    def test_imports(self, progress_callback=None):
        """Test if all required modules can be imported."""
        venv_python = self.get_venv_python()
        
        test_modules = ["PyQt6", "pymobiledevice3", "PIL"]
        
        for module in test_modules:
            if progress_callback:
                progress_callback(f"Testing {module} import...")
            
            try:
                # Hide console window on Windows
                kwargs = {}
                if self.is_windows:
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                result = subprocess.run([str(venv_python), "-c", f"import {module}"], 
                                      capture_output=True, text=True, **kwargs)
                if result.returncode != 0:
                    return False, f"Failed to import {module}: {result.stderr}"
            except subprocess.CalledProcessError as e:
                return False, f"Failed to import {module}: {e}"
        
        return True, "All imports successful"
    
    def check_main_app_exists(self):
        """Check if main application file exists."""
        # Check in current directory first
        if Path("main2.py").exists():
            return True
        
        # If running as compiled executable, check in bundle first, then executable directory
        if getattr(sys, 'frozen', False):
            # Check in PyInstaller bundle
            if hasattr(sys, '_MEIPASS'):
                bundled_main = Path(sys._MEIPASS) / "main2.py"
                if bundled_main.exists():
                    return True
            
            # Fallback: check in executable directory
            exe_dir = Path(sys.executable).parent
            return (exe_dir / "main2.py").exists()
        
        return False
    
    def launch_main_app(self, progress_callback=None):
        """Launch the main application."""
        # Find the main2.py file
        main_py_path = None
        
        if getattr(sys, 'frozen', False):
            # We're running as compiled executable - extract main2.py from bundle
            import tempfile
            import shutil
            
            # PyInstaller stores bundled files in sys._MEIPASS when frozen
            if hasattr(sys, '_MEIPASS'):
                bundled_main = Path(sys._MEIPASS) / "main2.py"
                if bundled_main.exists():
                    # Extract to a temporary location that persists for the subprocess
                    temp_dir = Path(tempfile.gettempdir()) / "idevice_manager_temp"
                    temp_dir.mkdir(exist_ok=True)
                    main_py_path = temp_dir / "main2.py"
                    shutil.copy2(bundled_main, main_py_path)
                    if progress_callback:
                        progress_callback(f"Extracted main2.py to {main_py_path}")
                else:
                    return False, f"main2.py not found in bundle at {sys._MEIPASS}"
            else:
                # Fallback: check in executable directory
                exe_dir = Path(sys.executable).parent
                if (exe_dir / "main2.py").exists():
                    main_py_path = exe_dir / "main2.py"
        else:
            # Running as script - check current directory
            if Path("main2.py").exists():
                main_py_path = Path("main2.py").absolute()
        
        if not main_py_path:
            return False, "main2.py not found in current directory, executable directory, or bundle"
        
        if progress_callback:
            progress_callback("Launching iDevice Manager...")
        
        try:
            # Launch the main app in a new process without console window
            if self.is_windows:
                # Use pythonw.exe for GUI applications to avoid console window
                venv_pythonw = self.get_venv_pythonw()
                
                # Use DETACHED_PROCESS to completely separate from parent console
                subprocess.Popen([str(venv_pythonw), str(main_py_path)], 
                               creationflags=subprocess.DETACHED_PROCESS,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               stdin=subprocess.DEVNULL)
            else:
                # For macOS/Linux, use regular python and detach from terminal
                venv_python = self.get_venv_python()
                subprocess.Popen([str(venv_python), str(main_py_path)],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               stdin=subprocess.DEVNULL)
            
            return True, "Application launched successfully"
        except Exception as e:
            return False, f"Failed to launch application: {e}"

class InstallerGUI:
    def __init__(self):
        self.installer = DependencyInstaller()
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI interface."""
        self.root = tk.Tk()
        self.root.title("iDevice Manager - First Time Setup")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Apply modern styling
        style = ttk.Style()
        if platform.system() == "Windows":
            style.theme_use('vista')
        elif platform.system() == "Darwin":
            style.theme_use('aqua')
        else:
            style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="iDevice Manager", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Setting up dependencies for first-time use...",
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", 
                                       padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Initializing...")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        button_frame.columnconfigure(1, weight=1)
        
        # Buttons
        self.start_button = ttk.Button(button_frame, text="Start Installation", 
                                      command=self.start_installation)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.launch_button = ttk.Button(button_frame, text="Launch App", 
                                       command=self.launch_app, state='disabled')
        self.launch_button.grid(row=0, column=2, padx=(10, 0))
        
        self.exit_button = ttk.Button(button_frame, text="Exit", 
                                     command=self.root.quit)
        self.exit_button.grid(row=0, column=3, padx=(10, 0))
        
        # Installation state
        self.installation_complete = False
        self.installation_thread = None
        self.installation_running = False
        
    def log_message(self, message):
        """Add message to log with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Thread-safe GUI update
        self.root.after(0, self._append_log, log_entry)
    
    def _append_log(self, message):
        """Append message to log text widget."""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        def _update():
            self.status_label.config(text=message)
            if progress is not None:
                self.progress_var.set(progress)
            self.root.update_idletasks()
        
        self.root.after(0, _update)
    
    def start_installation(self):
        """Start the installation process in a separate thread."""
        # Prevent multiple installations from running
        if self.installation_running or (self.installation_thread and self.installation_thread.is_alive()):
            self.log_message("Installation already in progress...")
            return
        
        self.installation_running = True
        self.start_button.config(state='disabled')
        self.launch_button.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        
        self.log_message("Starting dependency installation...")
        self.installation_thread = threading.Thread(target=self.run_installation)
        self.installation_thread.daemon = True
        self.installation_thread.start()
    
    def run_installation(self):
        """Run the complete installation process."""
        try:
            # Step 0: Ensure Python is available (5%)
            self.update_status("Ensuring Python is available...", 5)
            self.log_message("Checking for Python installation...")
            
            success, message = self.installer.ensure_python_available(
                progress_callback=self.log_message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 1: Check Python version (15%)
            self.update_status("Checking Python version...", 15)
            self.log_message("Verifying Python version...")
            
            success, message = self.installer.check_python_version()
            self.log_message(message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 2: Check pip (25%)
            self.update_status("Checking pip availability...", 25)
            self.log_message("Checking pip availability...")
            
            success, message = self.installer.check_pip_available()
            self.log_message(message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 3: Create virtual environment (35%)
            self.update_status("Creating virtual environment...", 35)
            self.log_message("Creating virtual environment...")
            
            success, message = self.installer.create_virtual_environment(
                progress_callback=self.log_message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 4: Install system dependencies (macOS only) (45%)
            if self.installer.is_macos:
                self.update_status("Installing system dependencies...", 45)
                self.log_message("Installing system dependencies (macOS)...")
                
                success, message = self.installer.install_system_dependencies_macos(
                    progress_callback=self.log_message)
                if not success:
                    self.log_message(f"Warning: {message}")
            
            # Step 5: Install Python dependencies (55-80%)
            self.update_status("Installing Python dependencies...", 55)
            self.log_message("Installing Python dependencies...")
            
            success, message = self.installer.install_python_dependencies(
                progress_callback=self.log_message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 6: Test imports (90%)
            self.update_status("Testing imports...", 90)
            self.log_message("Testing module imports...")
            
            success, message = self.installer.test_imports(
                progress_callback=self.log_message)
            if not success:
                self.installation_failed(message)
                return
            
            # Step 7: Complete (100%)
            self.update_status("Installation completed successfully!", 100)
            self.log_message("Installation completed successfully!")
            self.log_message("You can now launch the iDevice Manager application.")
            
            self.installation_complete = True
            
            # Enable launch button
            self.root.after(0, lambda: self.launch_button.config(state='normal'))
            self.root.after(0, lambda: self.start_button.config(text='Reinstall', state='normal'))
            
        except Exception as e:
            self.installation_failed(f"Unexpected error: {e}")
        finally:
            # Always reset the installation running flag
            self.installation_running = False
    
    def installation_failed(self, error_message):
        """Handle installation failure."""
        self.update_status("Installation failed!", 0)
        self.log_message(f"ERROR: {error_message}")
        self.log_message("Please check the log above and try again.")
        self.log_message("You can click 'Start Installation' to try again.")
        
        # Reset installation state
        self.installation_running = False
        
        # Re-enable start button
        self.root.after(0, lambda: self.start_button.config(state='normal'))
        
        # Don't show error dialog for now - just log the error
        # self.root.after(0, lambda: messagebox.showerror("Installation Failed", 
        #                                                f"Installation failed:\n\n{error_message}"))
    
    def launch_app(self):
        """Launch the main application."""
        if not self.installation_complete:
            messagebox.showwarning("Not Ready", 
                                 "Please complete the installation first.")
            return
        
        self.log_message("Launching iDevice Manager...")
        success, message = self.installer.launch_main_app(
            progress_callback=self.log_message)
        
        if success:
            self.log_message("Application launched successfully!")
            # Ask if user wants to close launcher
            if messagebox.askyesno("Application Launched", 
                                 "iDevice Manager has been launched successfully.\n\n"
                                 "Would you like to close this launcher window?"):
                self.root.quit()
        else:
            self.log_message(f"Failed to launch application: {message}")
            messagebox.showerror("Launch Failed", message)
    
    def run(self):
        """Run the GUI application."""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Show a prompt to start installation
        self.update_status("Ready to install dependencies. Click 'Start Installation' to begin.", 0)
        self.log_message("Welcome to iDevice Manager setup!")
        self.log_message("Click 'Start Installation' to automatically install all required dependencies.")
        
        self.root.mainloop()

def console_installer():
    """Fallback console-based installer if GUI is not available."""
    print("=" * 60)
    print("          iDevice Manager - Console Installer")
    print("=" * 60)
    print()
    
    installer = DependencyInstaller()
    
    def console_progress(message):
        print(f"  {message}")
    
    try:
        # Ensure Python is available
        print("Ensuring Python is available...")
        success, message = installer.ensure_python_available(console_progress)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        # Check Python version
        print("Checking Python version...")
        success, message = installer.check_python_version()
        console_progress(message)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        # Check pip
        print("Checking pip...")
        success, message = installer.check_pip_available()
        console_progress(message)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        # Create virtual environment
        print("Creating virtual environment...")
        success, message = installer.create_virtual_environment(console_progress)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        # Install system dependencies (macOS)
        if installer.is_macos:
            print("Installing system dependencies...")
            success, message = installer.install_system_dependencies_macos(console_progress)
            if not success:
                print(f"WARNING: {message}")
        
        # Install Python dependencies
        print("Installing Python dependencies...")
        success, message = installer.install_python_dependencies(console_progress)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        # Test imports
        print("Testing imports...")
        success, message = installer.test_imports(console_progress)
        if not success:
            print(f"ERROR: {message}")
            return False
        
        print()
        print("=" * 60)
        print("          Installation completed successfully!")
        print("=" * 60)
        print()
        
        # Launch main app
        if installer.check_main_app_exists():
            response = input("Would you like to launch the app now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                print("Launching iDevice Manager...")
                success, message = installer.launch_main_app()
                if success:
                    print("Application launched successfully!")
                    return True
                else:
                    print(f"Failed to launch: {message}")
                    return False
        else:
            print("main2.py not found. Please ensure all files are present.")
            return False
        
        return True
        
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Single instance checking functions (currently disabled to avoid conflicts)
# def check_single_instance():
#     """Check if another instance of the installer is already running."""
#     return True  # Always allow for now

# def cleanup_lock():
#     """Remove the lock file on exit."""
#     pass

def main():
    """Main entry point."""
    print("iDevice Manager - Auto Installer")
    print("Checking for GUI support...")
    
    if TKINTER_AVAILABLE:
        print("GUI mode available - starting graphical installer...")
        try:
            app = InstallerGUI()
            app.run()
        except Exception as e:
            print(f"GUI failed: {e}")
            print("Falling back to console mode...")
            console_installer()
    else:
        print("GUI not available - using console mode...")
        console_installer()

if __name__ == "__main__":
    main()