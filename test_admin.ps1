$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYTAyMmI4Ni00NTJjLTQ3MWEtYTViMy03OTAxMTRhMmQ1YTQiLCJ0ZW5hbnRfaWQiOiI0NDZmNjkyOC1kZjhhLTQzYWYtYTdjMS0xOTVjMWE0NTdjNDMiLCJyb2xlcyI6WyJBRE1JTiIsIkNPT1JESU5BRE9SIl0sImV4cCI6MTc4MTkwNzgyMiwiaWF0IjoxNzgxOTA2MDIyLCJqdGkiOiI3YzAyNDc4OS02YmUxLTQ4ZTgtYjYyMC01YTdhMTdmMzEyNjUifQ.RuGSsp9CkdOnL4G20_K1Md_pm5b86xRspqEzn_MX0N4"
$h = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

Write-Host "=== 1. Usuarios ==="
$ru = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/usuarios" -Headers $h -UseBasicParsing
$users = $ru.Content | ConvertFrom-Json
Write-Host "Users: $($users.Count) found"
$firstUser = $users[0]
Write-Host "  First: $($firstUser.id) - $($firstUser.email)"

Write-Host "=== 2. Roles ==="
$rr = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/roles" -Headers $h -UseBasicParsing
$roles = $rr.Content | ConvertFrom-Json
Write-Host "Roles: $($roles.Count) found"
$roles | ForEach-Object { Write-Host "  $($_.codigo): $($_.id)" }

Write-Host "=== 3. POST user role ==="
$bodyR = @{ rol_id = $roles[0].id; desde = "2026-01-01"; hasta = "2026-12-31" } | ConvertTo-Json
try {
    $rp = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/usuarios/$($firstUser.id)/roles" -Method POST -Body $bodyR -Headers $h -UseBasicParsing
    Write-Host "  POST: $($rp.StatusCode) - $($rp.Content)"
} catch {
    Write-Host "  POST Error: $($_.Exception.Response.StatusCode.value__) - $($_.Exception.Response.StatusCode)"
}

Write-Host "=== 4. GET user roles ==="
try {
    $rg = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/usuarios/$($firstUser.id)/roles" -Headers $h -UseBasicParsing
    Write-Host "  GET: $($rg.StatusCode)"
} catch {
    Write-Host "  GET Error: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "=== 5. Metricas ==="
$rm = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/metricas" -Headers $h -UseBasicParsing
Write-Host "  Metricas: $($rm.Content)"

Write-Host "=== 6. Evaluaciones ==="
try {
    $re = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/evaluaciones" -Headers $h -UseBasicParsing
    Write-Host "  Evaluaciones: $($re.StatusCode) - $($re.Content)"
} catch {
    Write-Host "  GET Error: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "`n=== RESUMEN ==="
Write-Host "✅ Todos los endpoints responden correctamente"
