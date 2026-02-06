$outFile = Join-Path $PSScriptRoot "DC_AuditPolicy_Dump.txt"
Set-Content -Path $outFile -Value "--- Domain Controller Audit Policy Dump ---`n" -Encoding utf8

# List all subcategories
Add-Content -Path $outFile -Value "=== auditpol /list /subcategory:* /v ===`n"
$auditList = auditpol /list /subcategory:* /v
Add-Content -Path $outFile -Value $auditList

# Get by category (standard format)
Add-Content -Path $outFile -Value "`n=== auditpol /get /category:* ===`n"
$auditGet = auditpol /get /category:*
Add-Content -Path $outFile -Value $auditGet

# Get by category (report format)
Add-Content -Path $outFile -Value "`n=== auditpol /get /category:* /r ===`n"
$auditReport = auditpol /get /category:* /r
Add-Content -Path $outFile -Value $auditReport

Add-Content -Path $outFile -Value "`Done. Output saved to: $outFile"
Write-Host "`Completed! File saved to: $outFile"
