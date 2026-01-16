# Git Push Script
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Starting Git Push Process..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Set-Location E:\taiwan-stock-app

# Step 1: Check status
Write-Host "[1/5] Checking Git status..." -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 2: Add all files
Write-Host "[2/5] Adding all files..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green
Write-Host ""

# Step 3: Commit
Write-Host "[3/5] Committing changes..." -ForegroundColor Yellow
git commit -m "feat: Complete Ollama Docker integration with model management

Features:
- Install Ollama inside Docker container (no external installation)
- Add settings page at /settings for model management
- Support download/delete models and set default model
- Auto-analyze stocks with financial data and news
- AI buy/sell recommendations with price targets
- Add 6 comprehensive documentation files
- Add PowerShell automation scripts
- Update Docker Compose with Ollama configuration
- Add new Python dependencies (ollama, beautifulsoup4, etc.)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Commit successful" -ForegroundColor Green
} else {
    Write-Host "✗ Commit failed or nothing to commit" -ForegroundColor Red
}
Write-Host ""

# Step 4: Push
Write-Host "[4/5] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Push successful!" -ForegroundColor Green
} else {
    Write-Host "✗ Push failed" -ForegroundColor Red
    Write-Host "Try running: git push origin main --verbose" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Verify
Write-Host "[5/5] Verifying push..." -ForegroundColor Yellow
git log --oneline -3
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Git Push Process Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Visit your GitHub repository to verify" -ForegroundColor White
Write-Host "2. Check the latest commit timestamp" -ForegroundColor White
Write-Host "3. Verify all 13 files are updated" -ForegroundColor White
