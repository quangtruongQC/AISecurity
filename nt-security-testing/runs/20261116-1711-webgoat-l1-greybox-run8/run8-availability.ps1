$ErrorActionPreference = 'Continue'

$RunDir = $PSScriptRoot
$EvidenceDir = Join-Path $RunDir 'evidence'
$HttpDir = Join-Path $EvidenceDir 'http'
New-Item -ItemType Directory -Path $HttpDir -Force | Out-Null

$StartTime = Get-Date
$StartTime.ToString('o') | Set-Content -Encoding utf8 -Path (Join-Path $RunDir 'RUN-START-TIMESTAMP.txt')
$ExecutionLog = Join-Path $EvidenceDir 'execution-log.txt'
Set-Content -Encoding utf8 -Path $ExecutionLog -Value "Run 8 authorized read-only availability retry started: $($StartTime.ToString('o'))"

$Url = 'http://10.242.10.31:8007/WebGoat/'
$Transcript = Join-Path $HttpDir '01-webgoat-root.txt'
$RequestTime = Get-Date
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`n[$($RequestTime.ToString('o'))] GET $Url"

$Output = & curl.exe --trace-time --max-time 12 --include --verbose --silent --show-error $Url 2>&1
$ExitCode = $LASTEXITCODE
$Output | Set-Content -Encoding utf8 -Path $Transcript
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "curl exit code: $ExitCode"
$Output | Add-Content -Encoding utf8 -Path $ExecutionLog

$EndTime = Get-Date
$EndTime.ToString('o') | Set-Content -Encoding utf8 -Path (Join-Path $RunDir 'RUN-END-TIMESTAMP.txt')
if ($ExitCode -eq 0) {
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`nRESULT: Availability check completed; inspect the response before any further request."
} else {
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`nRESULT: INCOMPLETE - availability check failed with curl exit code $ExitCode."
}
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "Run ended: $($EndTime.ToString('o'))"

$ListingPath = Join-Path $EvidenceDir 'directory-listing.csv'
$Encoding = New-Object System.Text.UTF8Encoding($false)
$ListingTime = (Get-Date).ToString('o')
$Files = Get-ChildItem -Path $EvidenceDir -File -Recurse | Where-Object { $_.FullName -ne $ListingPath }
$Lines = @('Name,Length,LastWriteTime')
foreach ($File in $Files) {
    $RelativeName = $File.FullName.Substring($EvidenceDir.Length + 1)
    $Lines += ('"{0}",{1},"{2}"' -f $RelativeName, $File.Length, $File.LastWriteTime.ToString('o'))
}
$Size = 0
for ($Index = 0; $Index -lt 5; $Index++) {
    $SelfRow = '"directory-listing.csv",{0},"{1}"' -f $Size, $ListingTime
    $Content = (($Lines + $SelfRow) -join "`r`n") + "`r`n"
    $NewSize = $Encoding.GetByteCount($Content)
    if ($NewSize -eq $Size) { break }
    $Size = $NewSize
}
$SelfRow = '"directory-listing.csv",{0},"{1}"' -f $NewSize, $ListingTime
$Content = (($Lines + $SelfRow) -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($ListingPath, $Content, $Encoding)
(Get-Item -Path $ListingPath).LastWriteTime = (Get-Date $ListingTime)

if ($ExitCode -ne 0) { exit 1 }
exit 0
