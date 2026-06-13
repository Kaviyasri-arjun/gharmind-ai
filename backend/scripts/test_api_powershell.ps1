# ═══════════════════════════════════════════════════════════════════════════
# GHARMIND AI — API Testing with PowerShell (Windows)
# Coimbatore Demo Household (Sundaram family)
# ═══════════════════════════════════════════════════════════════════════════
#
# Prerequisites:
#   1. Backend running: uvicorn app.main:app --reload
#   2. Database seeded: python -m scripts.seed_coimbatore_demo
#
# Usage: .\scripts\test_api_powershell.ps1
# ═══════════════════════════════════════════════════════════════════════════

$BASE = "http://localhost:8000"
$HID = "a1b2c3d4-e5f6-7890-abcd-111111111111"

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  GHARMIND AI — API Test Suite (PowerShell)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Health Check ─────────────────────────────────────────────────
Write-Host "1. Health Check" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/system/health"
$r | ConvertTo-Json -Depth 3
Write-Host ""

# ─── 2. Get Household ────────────────────────────────────────────────
Write-Host "2. Get Household" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID"
$r | ConvertTo-Json -Depth 3
Write-Host ""

# ─── 3. List Family Members ──────────────────────────────────────────
Write-Host "3. List Members" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID/members"
$r | ConvertTo-Json -Depth 4
Write-Host ""

# ─── 4. Twin State ───────────────────────────────────────────────────
Write-Host "4. Digital Twin State" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID/twin/state"
$r | ConvertTo-Json -Depth 5
Write-Host ""

# ─── 5. Predictions ──────────────────────────────────────────────────
Write-Host "5. Prediction Feed" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID/predictions?horizon=today&limit=5"
$r | ConvertTo-Json -Depth 5
Write-Host ""

# ─── 6. Routines ─────────────────────────────────────────────────────
Write-Host "6. Active Routines" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID/routines"
$r | ConvertTo-Json -Depth 4
Write-Host ""

# ─── 7. Chat — Motor question ────────────────────────────────────────
Write-Host "7. Chat: Motor question" -ForegroundColor Yellow
$body = @{message = "Motor chalana chahiye abhi?"; language = "hinglish"} | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "$BASE/v1/households/$HID/chat/message" -ContentType "application/json" -Body $body
$r | ConvertTo-Json -Depth 3
Write-Host ""

# ─── 8. Chat — Exam prep ─────────────────────────────────────────────
Write-Host "8. Chat: Exam prep" -ForegroundColor Yellow
$body = @{message = "Arjun ka exam kal hai, kya karna chahiye tonight?"} | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "$BASE/v1/households/$HID/chat/message" -ContentType "application/json" -Body $body
$r | ConvertTo-Json -Depth 3
Write-Host ""

# ─── 9. What-If: Power Cut ───────────────────────────────────────────
Write-Host "9. What-If: Power Cut at 2 PM" -ForegroundColor Yellow
$body = @{
    scenario_name = "TNEB Power Cut During Study"
    hypothesis = "Power cut at 2 PM during Arjun exam preparation"
    perturbations = @(@{type = "power_cut"; params = @{start_time = "14:00"; duration_hours = 1.5}})
    sim_duration_hours = 6
} | ConvertTo-Json -Depth 4
$r = Invoke-RestMethod -Method Post -Uri "$BASE/v1/households/$HID/simulator/run" -ContentType "application/json" -Body $body
$r | ConvertTo-Json -Depth 5
Write-Host ""

# ─── 10. What-If Templates ───────────────────────────────────────────
Write-Host "10. Available Scenarios" -ForegroundColor Yellow
$r = Invoke-RestMethod "$BASE/v1/households/$HID/simulator/scenarios"
$r | ConvertTo-Json -Depth 3
Write-Host ""

Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ All tests complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
