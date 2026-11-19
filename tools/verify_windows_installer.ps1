param(
    [Parameter(Mandatory=$true)][string]$Installer,
    [Parameter(Mandatory=$true)][string]$Bundle
)

$ErrorActionPreference = 'Stop'
$installerPath = (Resolve-Path -LiteralPath $Installer).Path
if ([System.IO.Path]::GetFileName($installerPath) -notlike 'DDL-Reminder-validation-*') {
    throw 'Only use the validation installer compiled with the isolated AppIdentity.'
}
$bundlePath = (Resolve-Path -LiteralPath $Bundle).Path
$repo = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repo '.venv\Scripts\python.exe'
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('ddl-installer-check-' + [guid]::NewGuid().ToString('N'))
$installDir = Join-Path $testRoot 'program'
New-Item -ItemType Directory -Path $testRoot | Out-Null
$env:APPDATA = Join-Path $testRoot 'userdata'
$env:TEMP = $testRoot
$env:TMP = $testRoot
$env:PYTHONPATH = Join-Path $repo 'src'

function Install-ValidationBuild {
    # Use only an installer compiled with a unique AppIdentity. This prevents
    # changes to an existing production installation's uninstall registration.
    $process = Start-Process -FilePath $installerPath -ArgumentList @(
        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOICONS',
        '/TASKS=""', "/DIR=`"$installDir`""
    ) -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Installer failed: $($process.ExitCode)" }
}

function Assert-Payload {
    $files = Get-ChildItem -LiteralPath $bundlePath -Recurse -File
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($bundlePath.Length + 1)
        $installed = Join-Path $installDir $relative
        if (-not (Test-Path -LiteralPath $installed)) { throw "Missing payload: $relative" }
        if ((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $installed).Hash) {
            throw "Payload differs: $relative"
        }
    }
    return $files.Count
}

Install-ValidationBuild
$fileCount = Assert-Payload
& $python -c "from datetime import date; from ddl_reminder.main import _build_database_service; e,r,s=_build_database_service(); s.create_task('Upgrade data', date(9999,12,31)); e.dispose()"
if ($LASTEXITCODE -ne 0) { throw 'Unable to create isolated fixture database' }
$db = Join-Path $env:APPDATA 'DDL-Reminder\tasks.db'
$before = (Get-FileHash -LiteralPath $db).Hash
$obsolete = Join-Path $installDir '_internal\obsolete-validation.dll'
New-Item -ItemType File -Path $obsolete | Out-Null
Install-ValidationBuild
$null = Assert-Payload
if (Test-Path -LiteralPath $obsolete) { throw 'Obsolete dependency survived upgrade' }
if ((Get-FileHash -LiteralPath $db).Hash -ne $before) { throw 'Upgrade altered task database' }

$gui = Start-Process -FilePath (Join-Path $installDir 'DDL-Reminder.exe') -WindowStyle Hidden -PassThru
try {
    Start-Sleep -Seconds 7
    $gui.Refresh()
    if ($gui.HasExited -or $gui.MainWindowTitle -ne 'DDL Reminder') {
        throw "Installed GUI failed: $($gui.MainWindowTitle)"
    }
} finally {
    if (-not $gui.HasExited) { Stop-Process -Id $gui.Id; $gui.WaitForExit() }
}
$log = Get-Content -LiteralPath (Join-Path $env:APPDATA 'DDL-Reminder\ddl-reminder.log') -Raw
if ($log -match 'ERROR|Traceback|CRITICAL') { throw $log }

# Full suite also exercises MCP protocol calls against the installed binary.
$env:DDL_MCP_EXECUTABLE = Join-Path $installDir 'DDL-Reminder-MCP.exe'
& $python -m pytest -q -p no:cacheprovider $repo\tests
if ($LASTEXITCODE -ne 0) { throw 'Release tests failed' }

$uninstaller = Join-Path $installDir 'unins000.exe'
$uninstall = Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -WindowStyle Hidden -Wait -PassThru
if ($uninstall.ExitCode -ne 0) { throw "Validation uninstall failed: $($uninstall.ExitCode)" }
if ((Get-FileHash -LiteralPath $db).Hash -ne $before) { throw 'Uninstall altered task database' }
[pscustomobject]@{
    TestRoot=$testRoot; VerifiedPayloadFiles=$fileCount; Install='passed'; Upgrade='passed'
    ObsoleteDependencyCleanup='passed'; DatabasePreserved='passed'; GUI='passed'; Uninstall='passed'
} | ConvertTo-Json
