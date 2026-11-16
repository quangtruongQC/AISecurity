$ErrorActionPreference = 'Continue'

$RunDir = $PSScriptRoot
$EvidenceDir = Join-Path $RunDir 'evidence'
$HttpDir = Join-Path $EvidenceDir 'http'
$IntakePath = 'C:\AISecurity\nt-security-testing\SECURITY-TEST-INTAKE-webgoat.md'
$ExecutionLog = Join-Path $EvidenceDir 'execution-log.txt'
$Username = 'xtbuiquang'
$CredentialLine = Get-Content -Path $IntakePath | Where-Object { $_ -match '^\|\s*xtbuiquang\s*\|' } | Select-Object -First 1
$CredentialMatch = [regex]::Match($CredentialLine, '^\|\s*xtbuiquang\s*\|\s*([^|]+)\|')
if (-not $CredentialMatch.Success) {
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value 'STOP: configured test credential row could not be read.'
    exit 2
}
$Password = $CredentialMatch.Groups[1].Value.Trim()

$BodyPath = Join-Path $RunDir 'temporary-login-body.txt'
$TracePath = Join-Path $RunDir 'temporary-login-trace.txt'
$CookiePath = Join-Path $RunDir 'temporary-session-cookie.txt'
$LoginEvidence = Join-Path $HttpDir '04-login-post-redacted.txt'
$MenuEvidence = Join-Path $HttpDir '05-lesson-menu-authenticated-redacted.txt'
$Body = 'username=' + [uri]::EscapeDataString($Username) + '&password=' + [uri]::EscapeDataString($Password)
[System.IO.File]::WriteAllText($BodyPath, $Body, (New-Object System.Text.UTF8Encoding($false)))

$LoginUrl = 'http://10.242.10.31:8007/WebGoat/login'
$LoginTime = Get-Date
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`n[$($LoginTime.ToString('o'))] POST $LoginUrl using the intake test account; password redacted from saved evidence."
$LoginOutput = & curl.exe --trace-time --trace-ascii $TracePath --max-time 12 --include --silent --show-error --cookie-jar $CookiePath --data-binary "@$BodyPath" $LoginUrl 2>&1
$LoginExitCode = $LASTEXITCODE
$RawTrace = [System.IO.File]::ReadAllText($TracePath)
$RawTrace = $RawTrace.Replace([uri]::EscapeDataString($Password), '[REDACTED-TEST-PASSWORD]')
[System.IO.File]::WriteAllText($LoginEvidence, $RawTrace, (New-Object System.Text.UTF8Encoding($false)))
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "Login curl exit code: $LoginExitCode`r`nSaved password-redacted request/response trace: evidence/http/04-login-post-redacted.txt"
$LoginOutput | Add-Content -Encoding utf8 -Path $ExecutionLog

$LoginSucceeded = $LoginExitCode -eq 0 -and $RawTrace -match 'Location:.*?/WebGoat/(start\.mvc|welcome)'
if (-not $LoginSucceeded) {
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value 'STOP: login did not demonstrate a redirect to the authenticated application; no lesson request sent.'
} else {
    Start-Sleep -Milliseconds 500
    $MenuUrl = 'http://10.242.10.31:8007/WebGoat/service/lessonmenu.mvc'
    $MenuTime = Get-Date
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`n[$($MenuTime.ToString('o'))] GET $MenuUrl with the session from the successful login."
    $MenuTracePath = Join-Path $RunDir 'temporary-lesson-menu-trace.txt'
    $MenuOutput = & curl.exe --trace-time --trace-ascii $MenuTracePath --max-time 12 --include --silent --show-error --cookie $CookiePath $MenuUrl 2>&1
    $MenuExitCode = $LASTEXITCODE
    $MenuTrace = [System.IO.File]::ReadAllText($MenuTracePath)
    [System.IO.File]::WriteAllText($MenuEvidence, $MenuTrace, (New-Object System.Text.UTF8Encoding($false)))
    Add-Content -Encoding utf8 -Path $ExecutionLog -Value "Lesson-menu curl exit code: $MenuExitCode`r`nSaved request/response trace: evidence/http/05-lesson-menu-authenticated-redacted.txt"
    $MenuOutput | Add-Content -Encoding utf8 -Path $ExecutionLog
    if ($MenuExitCode -ne 0) {
        Add-Content -Encoding utf8 -Path $ExecutionLog -Value 'STOP: authenticated lesson-menu request failed.'
    }
}

$EndTime = Get-Date
$EndTime.ToString('o') | Set-Content -Encoding utf8 -Path (Join-Path $RunDir 'RUN-END-TIMESTAMP.txt')
Add-Content -Encoding utf8 -Path $ExecutionLog -Value "`r`nEnumeration step ended: $($EndTime.ToString('o'))"

Remove-Item -LiteralPath $BodyPath, $TracePath, $CookiePath -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath (Join-Path $RunDir 'temporary-lesson-menu-trace.txt')) {
    Remove-Item -LiteralPath (Join-Path $RunDir 'temporary-lesson-menu-trace.txt') -Force
}
