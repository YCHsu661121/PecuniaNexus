# Docker 快速啟動腳本

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Taiwan Stock App - Docker 啟動腳本" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 等待構建完成
Write-Host "[1/4] 檢查 Docker 構建狀態..." -ForegroundColor Yellow
$buildRunning = $true
$attempts = 0
$maxAttempts = 60

while ($buildRunning -and $attempts -lt $maxAttempts) {
    $processes = Get-Process -Name "docker" -ErrorAction SilentlyContinue
    if ($processes) {
        Write-Host "." -NoNewline -ForegroundColor Gray
        Start-Sleep -Seconds 5
        $attempts++
    } else {
        $buildRunning = $false
    }
}

Write-Host ""
if ($attempts -ge $maxAttempts) {
    Write-Host "⏱ 構建超時，請手動檢查" -ForegroundColor Red
    exit 1
}

# 檢查鏡像
Write-Host "[2/4] 檢查 Docker 鏡像..." -ForegroundColor Yellow
$images = docker images --format "{{.Repository}}:{{.Tag}}" | Select-String "taiwan-stock"
if ($images) {
    Write-Host "✓ 鏡像已就緒：$images" -ForegroundColor Green
} else {
    Write-Host "✗ 未找到鏡像" -ForegroundColor Red
    exit 1
}

# 啟動容器
Write-Host "[3/4] 啟動 Docker 容器..." -ForegroundColor Yellow
docker-compose up -d

Start-Sleep -Seconds 10

# 檢查狀態
Write-Host "[4/4] 檢查服務狀態..." -ForegroundColor Yellow
$containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host $containers

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✓ 部署完成！" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "訪問應用：" -ForegroundColor Cyan
Write-Host "  主頁：    http://localhost:5788" -ForegroundColor White
Write-Host "  設置：    http://localhost:5788/settings" -ForegroundColor White
Write-Host ""
Write-Host "查看日誌：" -ForegroundColor Cyan
Write-Host "  docker logs pecunianexus -f" -ForegroundColor White
Write-Host ""
