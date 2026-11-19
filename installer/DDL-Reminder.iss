#define MyAppName "DDL Reminder"
#define MyAppVersion "0.3.2"
#define MyAppPublisher "DDL Reminder"
#define MyAppExeName "DDL-Reminder.exe"
#ifndef AppSource
  #define AppSource "..\dist\DDL-Reminder"
#endif
#ifndef AppIdentity
  #define AppIdentity "{{7F88AA88-7FC6-4F02-8BC2-20ED1F9BB204}"
#endif

[Setup]
AppId={#AppIdentity}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DDL Reminder
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer_dist
OutputBaseFilename=DDL-Reminder-Setup-v{#MyAppVersion}
SetupIconFile=..\src\ddl_reminder\ui\assets\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce
Name: "connectagents"; Description: "Automatically connect installed Claude Code, Codex and DeepSeek Harness (backs up existing settings)"; GroupDescription: "Local agents:"; Flags: checkedonce

[Files]
Source: "{#AppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Configure-Agent-Autoconnect.ps1"; DestDir: "{app}"; Flags: ignoreversion

[InstallDelete]
; Remove obsolete bundled dependencies on upgrade; user databases live in AppData.
Type: filesandordirs; Name: "{app}\_internal"
Type: files; Name: "{app}\_internal\ucrtbase.dll"
Type: files; Name: "{app}\_internal\api-ms-win-*.dll"
Type: files; Name: "{app}\_internal\VCRUNTIME*.dll"
Type: files; Name: "{app}\_internal\MSVCP*.dll"
Type: files; Name: "{app}\_internal\icu*.dll"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Always retire the previous shell-based task, including opt-out upgrades.
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -File ""{app}\Configure-Agent-Autoconnect.ps1"" -McpExecutable ""{app}\DDL-Reminder-MCP.exe"" -Disable"; Flags: runhidden waituntilterminated
Filename: "{app}\DDL-Reminder-Agent-Setup.exe"; Tasks: connectagents; Flags: runhidden waituntilterminated
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -File ""{app}\Configure-Agent-Autoconnect.ps1"" -McpExecutable ""{app}\DDL-Reminder-MCP.exe"""; Tasks: connectagents; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -File ""{app}\Configure-Agent-Autoconnect.ps1"" -McpExecutable ""{app}\DDL-Reminder-MCP.exe"" -Disable"; Flags: runhidden waituntilterminated; RunOnceId: "DisableAgentAutoConnect"
