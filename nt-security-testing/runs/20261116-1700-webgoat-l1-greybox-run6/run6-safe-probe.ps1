$ErrorActionPreference = 'Stop'

$RunDir = $PSScriptRoot
$EvidenceDir = Join-Path $RunDir 'evidence'
$HttpDir = Join-Path $EvidenceDir 'http'
New-Item -ItemType Directory -Path $HttpDir -Force | Out-Null

$StartTime = Get-Date
$StartTime.ToString('o') | Set-Content -Path (Join-Path $RunDir 'RUN-START-TIMESTAMP.txt')
$ExecutionLog = Join-Path $EvidenceDir 'execution-log.txt'
Set-Content -Path $ExecutionLog -Value "Run 6 read-only route checks started: $($StartTime.ToString('o'))"

$Target = 'http://10.242.10.31:8007/WebGoat'
$Routes = @(
    @{ Name = '01-webgoat-root'; Path = '/' },
    @{ Name = '02-login-route'; Path = '/login' },
    @{ Name = '03-lesson-menu'; Path = '/service/lessonmenu.mvc' }
)

$Failures = 0
foreach ($Route in $Routes) {
    $Url = $Target + $Route.Path
    $Transcript = Join-Path $HttpDir ($Route.Name + '.txt')
    $Timestamp = Get-Date
    Add-Content -Path $ExecutionLog -Value "`r`n[$($Timestamp.ToString('o'))] GET $Url"

    $Output = & curl.exe --trace-time --max-time 12 --include --verbose --silent --show-error $Url 2>&1
    $ExitCode = $LASTEXITCODE
    $Output | Set-Content -Path $Transcript
    Add-Content -Path $ExecutionLog -Value "curl exit code: $ExitCode"
    $Output | Add-Content -Path $ExecutionLog

    if ($ExitCode -ne 0) {
        $Failures++
    }

    Start-Sleep -Milliseconds 500
}

$EndTime = Get-Date
$EndTime.ToString('o') | Set-Content -Path (Join-Path $RunDir 'RUN-END-TIMESTAMP.txt')
Add-Content -Path $ExecutionLog -Value "`r`nRun ended: $($EndTime.ToString('o'))"

$ListingPath = Join-Path $EvidenceDir 'directory-listing.csv'
Get-ChildItem -Path $EvidenceDir -File |
    Select-Object Name, Length, LastWriteTime |
    Export-Csv -Path $ListingPath -NoTypeInformation
$Listing = Get-Item -Path $ListingPath
Add-Content -Path $ListingPath -Value "`"$($Listing.Name)`",$($Listing.Length),`"$($Listing.LastWriteTime.ToString('o'))`""

if ($Failures -gt 0) {
    Add-Content -Path $ExecutionLog -Value "RESULT: INCOMPLETE - $Failures request(s) did not complete successfully."
    exit 1
}

Add-Content -Path $ExecutionLog -Value 'RESULT: All three read-only route checks completed with curl exit code 0.'
exit 0
