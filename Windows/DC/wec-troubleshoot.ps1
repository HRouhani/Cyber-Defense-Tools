$outFile = Join-Path $PSScriptRoot "WEC_Subscriptions_Dump.txt"
Set-Content -Path $outFile -Value "--- Windows Event Collector (WEC) Subscriptions Dump ---`n" -Encoding utf8

# Get subscriptions
$subs = wecutil es

foreach ($sub in $subs) {
    Add-Content -Path $outFile -Value "`n=============================="
    Add-Content -Path $outFile -Value "Subscription Name: $sub"
    Add-Content -Path $outFile -Value "`n--- Subscription Details ---"
    $details = wecutil gs "$sub"
    Add-Content -Path $outFile -Value $details
}

Add-Content -Path $outFile -Value "` Done. Output saved to: $outFile"
Write-Host "` Completed! File saved to: $outFile"
