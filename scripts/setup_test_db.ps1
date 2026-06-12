# activia-trace — Test database setup script
# Run as Administrator to configure local PostgreSQL for testing

Write-Host "=== activia-trace Test DB Setup ===" -ForegroundColor Cyan

# 1. Create test databases
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h 127.0.0.1 -p 5432 -U postgres -c "CREATE DATABASE activia_trace_test;" 2>$null
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h 127.0.0.1 -p 5432 -U postgres -c "CREATE DATABASE activia_trace;" 2>$null

# 2. Add trust auth for local test connections
$hbaPath = "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
$hbaContent = Get-Content $hbaPath -Raw

if ($hbaContent -notmatch "trust.*added.by.activia") {
    $trustEntry = @"

# Trust local connections for development (added by activia-trace setup)
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
"@
    Add-Content -Path $hbaPath -Value $trustEntry
    Write-Host "  Added trust entries to pg_hba.conf" -ForegroundColor Green

    # 3. Reload PostgreSQL
    Restart-Service -Name "postgresql-x64-18"
    Write-Host "  PostgreSQL restarted" -ForegroundColor Green
} else {
    Write-Host "  pg_hba.conf already configured" -ForegroundColor Yellow
}

# 4. Verify
& "C:\Program Files\PostgreSQL\18\bin\pg_isready.exe" -h 127.0.0.1 -p 5432
Write-Host "Setup complete! Run tests with: cd backend; pytest -v --asyncio-mode=auto" -ForegroundColor Cyan
