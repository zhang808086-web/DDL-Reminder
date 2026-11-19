param(
    [Parameter(Mandatory=$true)][string]$McpExecutable,
    [switch]$Disable,
    [switch]$ConnectOnly
)
$ErrorActionPreference = 'Stop'
if ($ConnectOnly) {
    $background = Join-Path (Split-Path -Parent $McpExecutable) 'DDL-Reminder-Agent-Setup.exe'
    $child = Start-Process -FilePath $background -WindowStyle Hidden -PassThru -Wait
    exit $child.ExitCode
}
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$taskName = "DDL Reminder Agent Connect $sid"
$service = New-Object -ComObject 'Schedule.Service'
$service.Connect()
$folder = $service.GetFolder('\')
$dataDir = Join-Path $env:APPDATA 'DDL-Reminder'
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
if ($Disable) {
    try { $existing = $folder.GetTask($taskName) } catch { $existing = $null }
    if ($existing) {
        if ($existing.Definition.RegistrationInfo.Description -ne 'DDL Reminder per-user MCP auto-connect') {
            throw 'Refusing to remove an unrecognized scheduled task'
        }
        $background = Join-Path (Split-Path -Parent $McpExecutable) 'DDL-Reminder-Agent-Setup.exe'
        $action = $existing.Definition.Actions.Item(1)
        if ($action.Path -ne $background -and -not $action.Arguments.Contains('"' + $McpExecutable + '"')) {
            return # Another installation owns this user's auto-connect task.
        }
        $folder.DeleteTask($taskName, 0)
    }
} else {
    $exe = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $McpExecutable) 'DDL-Reminder-Agent-Setup.exe')).Path
    $task = $service.NewTask(0)
    $task.RegistrationInfo.Description = 'DDL Reminder per-user MCP auto-connect'
    $task.Principal.UserId = $sid
    $task.Principal.LogonType = 3
    $task.Principal.RunLevel = 0
    $task.Settings.Enabled = $true
    $task.Settings.Hidden = $true
    $task.Settings.DisallowStartIfOnBatteries = $false
    $task.Settings.StopIfGoingOnBatteries = $false
    $task.Settings.StartWhenAvailable = $true
    $task.Settings.MultipleInstances = 2
    $task.Settings.ExecutionTimeLimit = 'PT1M'
    $trigger = $task.Triggers.Create(1)
    $trigger.StartBoundary = (Get-Date).AddMinutes(1).ToString('s')
    $trigger.Repetition.Interval = 'PT2M'
    $trigger.Enabled = $true
    $logon = $task.Triggers.Create(9)
    $logon.UserId = $sid
    $logon.Delay = 'PT30S'
    $logon.Enabled = $true
    $action = $task.Actions.Create(0)
    $action.Path = $exe
    $action.Arguments = ''
    $action.WorkingDirectory = Split-Path -Parent $exe
    $null = $folder.RegisterTaskDefinition($taskName, $task, 6, $sid, $null, 3)
}
@{enabled=(-not $Disable); task=$taskName} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dataDir 'agent-autoconnect.json') -Encoding UTF8
