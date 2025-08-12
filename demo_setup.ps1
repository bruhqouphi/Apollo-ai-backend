# Apollo AI Demo Setup Script
Write-Host "🚀 Setting up Apollo AI Demo Environment..." -ForegroundColor Green

# Check if Python is available
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
python --version

# Check if Node.js is available
Write-Host "📋 Checking Node.js installation..." -ForegroundColor Yellow
node --version

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install Node.js dependencies
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
cd apollo-frontend
npm install
cd ..

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path uploads, exports, static

# Test backend
Write-Host "🧪 Testing backend..." -ForegroundColor Yellow
python -c "import app.main; print('✅ Backend imports successfully')"

# Test frontend build
Write-Host "🧪 Testing frontend build..." -ForegroundColor Yellow
cd apollo-frontend
npm run build
cd ..

Write-Host "✅ Demo environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 To start the demo:" -ForegroundColor Cyan
Write-Host "1. Start backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host "2. Start frontend: cd apollo-frontend && npm start" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
