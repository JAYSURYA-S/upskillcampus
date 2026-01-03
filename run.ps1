# Check if python is available
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not found in your PATH. Please install Python." -ForegroundColor Red
    exit
}

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Run the app
Write-Host "Starting LinkShrink..." -ForegroundColor Green
python app.py
