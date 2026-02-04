# Deploy RAG System with Docker
Write-Host "🚀 Deploying RAG System..." -ForegroundColor Green

# Check if Docker is running
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker is running" -ForegroundColor Green

# Stop existing containers
Write-Host "`n🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Build images
Write-Host "`n🔨 Building Docker images..." -ForegroundColor Yellow
docker-compose build --no-cache

# Start services
Write-Host "`n🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services
Write-Host "`n⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check health
Write-Host "`n🏥 Checking API health..." -ForegroundColor Yellow
$maxRetries = 10
$retry = 0

while ($retry -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Host "✅ API is healthy!" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Cyan
        break
    }
    catch {
        $retry++
        Write-Host "⏳ Waiting... (attempt $retry/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

if ($retry -eq $maxRetries) {
    Write-Host "❌ API health check failed" -ForegroundColor Red
    docker-compose logs rag-api
    exit 1
}

# Show running containers
Write-Host "`n📦 Running containers:" -ForegroundColor Green
docker-compose ps

# Show logs
Write-Host "`n📋 Recent logs:" -ForegroundColor Green
docker-compose logs --tail=20 rag-api

Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

Write-Host "`n🌐 Services:" -ForegroundColor Cyan
Write-Host "  API:        http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health:     http://localhost:8000/health" -ForegroundColor White
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "  Redis:      localhost:6379" -ForegroundColor White

Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:     docker-compose logs -f rag-api" -ForegroundColor White
Write-Host "  Stop:          docker-compose down" -ForegroundColor White
Write-Host "  Restart:       docker-compose restart" -ForegroundColor White
Write-Host "  Shell access:  docker exec -it rag-api /bin/bash" -ForegroundColor White
Write-Host ""