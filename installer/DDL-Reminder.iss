#define MyAppName "DDL Reminder"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "DDL Reminder"
#define MyAppExeName "DDL-Reminder.exe"

[Setup]
AppId={{7F88AA88-7FC6-4F02-8BC2-20ED1F9BB204}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DDL Reminder
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer_dist
OutputBaseFilename=DDL-Reminder-Setup
SetupIconFile=..\src\ddl_reminder\ui\assets\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Files]
Source: "..\dist\DDL-Reminder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
