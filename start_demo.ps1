# Apollo AI Demo Launcher - PowerShell Script
# Run this script to start the Apollo AI demo

Write-Host @"
🚀 APOLLO AI - DEMO LAUNCHER
==================================================
🎯 Starting server and opening demo interface...
==================================================

"@ -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "apollo_env")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "💡 Run: python -m venv apollo_env" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
& "apollo_env\Scripts\Activate.ps1"

# Check if activation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Start the server
Write-Host "🚀 Starting Apollo AI Server..." -ForegroundColor Green
Write-Host "📍 Server will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "📖 ReDoc Documentation: http://localhost:8000/redoc" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Gray

# Start server in background
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"

# Wait a moment for server to start
Start-Sleep -Seconds 3

# Open browser
Write-Host "🌐 Opening browser to API documentation..." -ForegroundColor Green
Start-Process "http://localhost:8000/docs"

Write-Host @"

🎯 TESTING WORKFLOW
==================================================
1. 📁 UPLOAD FILE:
   - Click "Try it out" on POST /upload
   - Upload a CSV file (use sample data in /uploads folder)
   - Copy the file_id from response

2. 📊 ANALYZE DATA:
   - Click "Try it out" on POST /analyze
   - Paste the file_id
   - Get comprehensive analysis in 0.2s

3. 🤖 GENERATE AI INSIGHTS:
   - Click "Try it out" on POST /insight
   - Paste the file_id
   - Choose AI provider (groq, anthropic, etc.)
   - Get AI-powered insights

4. 📈 CREATE VISUALIZATIONS:
   - Click "Try it out" on GET /visualize/{file_id}
   - Get available chart types
   - Use POST /visualize/{file_id}/{chart_type} to generate charts

5. 📄 EXPORT REPORTS:
   - Use POST /export/{file_id} for PDF/HTML reports

==================================================
💡 PRO TIPS:
- Use the sample CSV files in /uploads folder
- Test with different file sizes
- Try different AI providers
- Check response times (should be <1s)
==================================================

🎉 DEMO READY!
==================================================
✅ Server running: http://localhost:8000
✅ API Docs open: http://localhost:8000/docs
✅ Testing workflow provided above

Press Ctrl+C in the server window to stop when done
==================================================

"@ -ForegroundColor Green 