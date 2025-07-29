# MIPSolver Quick Start Guide

## Desktop Application - One-Click Setup

### For End Users (Recommended)

**No Python installation required!** - Download and run immediately.

#### Step 1: Download
Choose your operating system:

- **Windows**: Download `MipSolver-v1.0-Windows-x64.zip`
- **macOS**: Download `MipSolver-v1.0-macOS-arm64.zip`  
- **Linux**: Download `MipSolver-v1.0-Linux-x86_64.zip`

#### Step 2: Extract
Unzip the file to any folder, for example:
- **Windows**: `C:\MipSolver\`
- **macOS**: `~/Applications/MipSolver/`
- **Linux**: `~/MipSolver/`

#### Step 3: Run
**Double-click to start:**
- **Windows**: Double-click `MipSolver.exe`
- **macOS**: Double-click `MipSolver.app`
- **Linux**: Double-click `MipSolver` (or run `./MipSolver` from terminal)

#### Step 4: Use
1. Click "Browse" to select an MPS file
2. Choose solver: "Branch & Bound" or "Simplex (LP)"
3. Click "Start Solving"
4. View results and generate reports

### Quick Test
The application includes example files in the `examples/` folder:
- Try `examples/gr4x6.mps` for a quick test
- This small problem solves in under 1 second

## First-Time Setup Issues

### Windows Users
If you see "Windows protected your PC":
1. Click "More info"
2. Click "Run anyway"
3. (Optional) Add to antivirus whitelist

### macOS Users
If you see "Cannot open because developer cannot be verified":
1. Right-click the app → "Open"
2. Click "Open" in the dialog
3. Or: System Preferences → Security & Privacy → "Allow anyway"

### Linux Users
If the application won't run:
```bash
# Make executable
chmod +x MipSolver

# Install GUI libraries if needed (Ubuntu/Debian)
sudo apt-get install python3-tk

# Run from terminal to see error messages
./MipSolver
```

## What You Get

### Complete Application
- High-performance C++ solver engine
- User-friendly graphical interface
- MPS file format support  
- Professional LaTeX report generation
- No dependencies to install

### Example Problems Included
- Small test problems (< 1 second solve time)
- Medium problems (1-10 seconds)
- Real-world optimization examples

### Features
- **Algorithms**: Branch & Bound, Simplex Method
- **Problem Types**: Mixed-Integer Programming, Linear Programming
- **File Support**: MPS (Mathematical Programming System) format
- **Reports**: Professional PDF reports with Chinese support
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Need Help?

### Quick Solutions
- **No files to select**: Use examples in `examples/` folder
- **Slow solving**: Try smaller problems first
- **Report errors**: Check that XeLaTeX is installed for PDF generation

### Documentation
- [Full User Guide](docs/GUI_README.md)
- [Windows Specific Guide](docs/WINDOWS_USAGE.md)
- [Cross-Platform Guide](docs/CROSS_PLATFORM_GUIDE.md)

### Support
- Check GitHub Issues for common problems
- Email: support@mipsolver.com (if available)

---

**That's it!** You now have a professional optimization solver running on your desktop with just a few clicks.