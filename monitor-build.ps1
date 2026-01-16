# 監控 Docker 構建進度腳本
Write-Host "監控 Docker 構建中..." -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止監控（不會停止構建）" -ForegroundColor Yellow
Write-Host ""

$maxWait = 600 # 最多等待 10 分鐘
$elapsed = 0
$checkInterval = 10

while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds $checkInterval
    $elapsed += $checkInterval
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 已等待 $elapsed 秒..." -ForegroundColor Gray
    
    # 檢查映像是否已創建
    $image = docker images taiwan-stock-app-pecunianexus --format "{{.Repository}}:{{.Tag}}" 2>$null
    
    if ($image) {
        Write-Host "`n✓ 構建完成！" -ForegroundColor Green
        Write-Host "映像: $image" -ForegroundColor Green
        Write-Host ""
        
        # 詢問是否啟動容器
        $start = Read-Host "是否要啟動容器？(Y/n)"
        if ($start -ne 'n' -and $start -ne 'N') {
            Write-Host "`n啟動容器..." -ForegroundColor Cyan
            docker-compose up -d
            
            Write-Host "`n等待 5 秒讓服務啟動..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            Write-Host "`n檢查容器狀態..." -ForegroundColor Cyan
            docker-compose ps
            
            Write-Host "`n查看日誌..." -ForegroundColor Cyan
            docker logs taiwan-stock-app-pecunianexus-1 --tail=30
            
            Write-Host "`n✓ 應用已啟動！" -ForegroundColor Green
            Write-Host "訪問: http://localhost:5788" -ForegroundColor Green
            Write-Host "設置頁面: http://localhost:5788/settings" -ForegroundColor Green
        }
        
        exit 0
    }
}

Write-Host "`n⚠ 超時：構建可能還在進行中或失敗了" -ForegroundColor Yellow
Write-Host "使用以下命令檢查狀態:" -ForegroundColor Yellow
Write-Host "  docker images | Select-String taiwan-stock" -ForegroundColor White
Write-Host "  docker-compose logs pecunianexus" -ForegroundColor White
