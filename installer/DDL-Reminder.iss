#define MyAppName "DDL Reminder"
#define MyAppVersion "0.3.0"
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

[Files]
Source: "{#AppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

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
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
