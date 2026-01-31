# SentiLex API Endpoint Testing Script
# Tests all major endpoints to ensure they're working correctly

$baseUrl = "http://localhost:8000"
$testResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "`n🔍 Testing: $Name" -ForegroundColor Cyan
    Write-Host "   URL: $Method $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ContentType = "application/json"
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            Write-Host "   Body: $($Body | ConvertTo-Json -Compress)" -ForegroundColor Gray
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "   ✅ PASSED - Status: $($response.StatusCode)" -ForegroundColor Green
            $script:testResults += [PSCustomObject]@{
                Endpoint = $Name
                Status = "✅ PASSED"
                StatusCode = $response.StatusCode
            }
            return $true
        } else {
            Write-Host "   ⚠️  Unexpected Status: $($response.StatusCode) (Expected: $ExpectedStatus)" -ForegroundColor Yellow
            $script:testResults += [PSCustomObject]@{
                Endpoint = $Name
                Status = "⚠️ WARNING"
                StatusCode = $response.StatusCode
            }
            return $false
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "   ✅ PASSED - Status: $statusCode (Expected error)" -ForegroundColor Green
            $script:testResults += [PSCustomObject]@{
                Endpoint = $Name
                Status = "✅ PASSED"
                StatusCode = $statusCode
            }
            return $true
        } else {
            Write-Host "   ❌ FAILED - Status: $statusCode" -ForegroundColor Red
            Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
            $script:testResults += [PSCustomObject]@{
                Endpoint = $Name
                Status = "❌ FAILED"
                StatusCode = $statusCode
            }
            return $false
        }
    }
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  SentiLex API Endpoint Testing" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# 1. Health Check
Write-Host "`n📋 CATEGORY: Health & Info" -ForegroundColor Yellow
Test-Endpoint -Name "Root Endpoint" -Url "$baseUrl/" -ExpectedStatus 200

# 2. Authentication Endpoints
Write-Host "`n📋 CATEGORY: User Authentication" -ForegroundColor Yellow

# Test login with invalid credentials (should fail with 401)
Test-Endpoint -Name "User Login (Invalid Credentials)" `
    -Url "$baseUrl/auth/login" `
    -Method POST `
    -Body @{
        email = "nonexistent@test.com"
        password = "wrongpassword"
    } `
    -ExpectedStatus 401

# Test super admin login (should succeed)
Test-Endpoint -Name "Super Admin Login" `
    -Url "$baseUrl/auth/login" `
    -Method POST `
    -Body @{
        email = "samprasharendaishika@gmail.com"
        password = "Sentilexadmin1234"
    } `
    -ExpectedStatus 200

# Test registration with missing data (should fail with 422)
Test-Endpoint -Name "User Registration (Invalid Data)" `
    -Url "$baseUrl/auth/register" `
    -Method POST `
    -Body @{
        email = "test@test.com"
    } `
    -ExpectedStatus 422

# 3. Google OAuth Endpoints
Write-Host "`n📋 CATEGORY: Google OAuth" -ForegroundColor Yellow

# These will redirect, so we expect 307 (Temporary Redirect)
Test-Endpoint -Name "Google OAuth - User Login" `
    -Url "$baseUrl/auth/google/login?user_type=user" `
    -ExpectedStatus 307

Test-Endpoint -Name "Google OAuth - Lawyer Login" `
    -Url "$baseUrl/auth/google/login?user_type=lawyer" `
    -ExpectedStatus 307

# 4. Lawyer Endpoints
Write-Host "`n📋 CATEGORY: Lawyer Endpoints" -ForegroundColor Yellow

Test-Endpoint -Name "Get All Lawyers" `
    -Url "$baseUrl/lawyers/" `
    -ExpectedStatus 200

# Test lawyer login with invalid credentials
Test-Endpoint -Name "Lawyer Login (Invalid)" `
    -Url "$baseUrl/lawyers/login" `
    -Method POST `
    -Body @{
        email = "nonexistent@lawyer.com"
        password = "wrongpassword"
    } `
    -ExpectedStatus 401

# 5. Legal Query Endpoint
Write-Host "`n📋 CATEGORY: Legal Services" -ForegroundColor Yellow

Test-Endpoint -Name "Legal Query (No Auth - Should Fail)" `
    -Url "$baseUrl/legal-query" `
    -Method POST `
    -Body @{
        query = "What are my rights?"
    } `
    -ExpectedStatus 401

# 6. Documentation Endpoints
Write-Host "`n📋 CATEGORY: Documentation" -ForegroundColor Yellow

Test-Endpoint -Name "OpenAPI Docs (Swagger UI)" `
    -Url "$baseUrl/docs" `
    -ExpectedStatus 200

Test-Endpoint -Name "OpenAPI Schema" `
    -Url "$baseUrl/openapi.json" `
    -ExpectedStatus 200

# Summary
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "  Test Summary" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

$testResults | Format-Table -AutoSize

$passed = ($testResults | Where-Object { $_.Status -eq "✅ PASSED" }).Count
$failed = ($testResults | Where-Object { $_.Status -eq "❌ FAILED" }).Count
$warning = ($testResults | Where-Object { $_.Status -eq "⚠️ WARNING" }).Count
$total = $testResults.Count

Write-Host "`nResults: $passed/$total passed, $failed failed, $warning warnings" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })

if ($failed -eq 0) {
    Write-Host "`n✅ All critical endpoints are working correctly!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some endpoints failed. Please review the errors above." -ForegroundColor Yellow
}

Write-Host "`n📚 Full API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
