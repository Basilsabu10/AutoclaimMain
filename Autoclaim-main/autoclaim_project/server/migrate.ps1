# Database Migration Script for AutoClaim
# Migrates to v2.0 with comprehensive forensic analysis

Write-Host "=" * 80
Write-Host "DATABASE MIGRATION - Comprehensive Forensic Analysis v2.0"
Write-Host "=" * 80

# Create backup directory
$backupDir = "db_backups"
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# Backup existing database
if (Test-Path "autoclaim.db") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$backupDir\autoclaim_backup_$timestamp.db"
    Copy-Item "autoclaim.db" $backupFile
    Write-Host "`n✅ Backed up existing database to: $backupFile" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  No existing database found" -ForegroundColor Yellow
}

# Delete old database
if (Test-Path "autoclaim.db") {
    Remove-Item "autoclaim.db" -Force
    Write-Host "✅ Deleted old database" -ForegroundColor Green
}

Write-Host "`n🔄 Database will be recreated on next server start..." -ForegroundColor Cyan
Write-Host "`n📊 New ForensicAnalysis Table Will Include:" -ForegroundColor Cyan
Write-Host "   - YOLOv8 Detection (4 fields)"
Write-Host "   - Forensic Analysis / Image Integrity (4 fields)"
Write-Host "   - Vehicle Identification (11 fields)"
Write-Host "   - Enhanced Damage Assessment (8 fields)"
Write-Host "   - Pre-existing Damage Detection (4 fields)"
Write-Host "   - Contextual Analysis (5 fields)"
Write-Host "   - Cross-verification (4 fields)"
Write-Host "   - Risk Assessment & Final Assessment (7 fields)"
Write-Host "   - Total: 60+ comprehensive forensic fields"

Write-Host "`n" + ("=" * 80)
Write-Host "MIGRATION PREPARED!" -ForegroundColor Green
Write-Host ("=" * 80)
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Restart the server: python run.py"
Write-Host "   2. Submit a new claim to test"
Write-Host "   3. Run: python test_ai_storage.py"
Write-Host "`n✅ Migration script completed successfully!" -ForegroundColor Green
