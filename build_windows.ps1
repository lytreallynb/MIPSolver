# PowerShell build script for MIPSolver on Windows
# Requirements: Python 3.7+, CMake, Visual Studio Build Tools

param(
    [string]$PythonVersion = "3.12",
    [switch]$Clean = $false,
    [switch]$Test = $true,
    [switch]$Install = $false
)

Write-Host "MIPSolver Windows Build Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Error "Python is not installed or not in PATH. Please install Python from https://python.org"
    exit 1
}

if (-not (Test-Command "cmake")) {
    Write-Error "CMake is not installed or not in PATH. Please install CMake from https://cmake.org"
    exit 1
}

# Check Python version
$pythonVersionOutput = python --version 2>&1
Write-Host "Found: $pythonVersionOutput" -ForegroundColor Green

# Clean previous builds
if ($Clean) {
    Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Get-ChildItem -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force
}

# Install build dependencies
Write-Host "Installing build dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel build pybind11

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install build dependencies"
    exit 1
}

# Set environment variables for Windows build
$env:CMAKE_GENERATOR = "Visual Studio 16 2019"
$env:CMAKE_BUILD_PARALLEL_LEVEL = "4"

# Build the wheel
Write-Host "Building wheel package..." -ForegroundColor Yellow
python -m build --wheel

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed! Please check the error messages above."
    exit 1
}

Write-Host "Build successful!" -ForegroundColor Green

# Show created wheels
Write-Host "Created wheel packages:" -ForegroundColor Green
Get-ChildItem -Path "dist" -Filter "*.whl" | ForEach-Object {
    Write-Host "  $($_.Name)" -ForegroundColor Cyan
}

# Test installation
if ($Test) {
    Write-Host "Testing wheel installation..." -ForegroundColor Yellow
    
    # Create a temporary virtual environment for testing
    python -m venv test_env
    & "test_env\Scripts\Activate.ps1"
    
    # Install the wheel
    $wheelFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
    pip install $wheelFile.FullName
    
    # Test import
    python -c "import mipsolver; print('MIPSolver imported successfully!')"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Wheel test passed!" -ForegroundColor Green
    } else {
        Write-Error "Wheel test failed!"
    }
    
    # Cleanup test environment
    deactivate
    Remove-Item -Recurse -Force "test_env"
}

# Install in current environment
if ($Install) {
    Write-Host "Installing in current Python environment..." -ForegroundColor Yellow
    $wheelFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
    pip install --force-reinstall $wheelFile.FullName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installation successful!" -ForegroundColor Green
    } else {
        Write-Error "Installation failed!"
    }
}

Write-Host "Build process completed!" -ForegroundColor Green
Write-Host "To install the wheel: pip install dist\<wheel-name>.whl" -ForegroundColor Cyan
