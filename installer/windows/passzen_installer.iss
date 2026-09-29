; PassZen — Inno Setup Installer Script
; Creates a professional Windows installer (.exe) with:
;   - Install/uninstall wizard
;   - Desktop shortcut
;   - Start Menu folder
;   - Custom install directory
;
; Prerequisites:
;   1. Run `python build.py` first to create dist/PassZen.exe
;   2. Install Inno Setup: https://jrsoftware.org/isdl.php
;   3. Open this file in Inno Setup and click Build > Compile
;
; Output: installer/windows/Output/PassZen-Setup.exe

#define MyAppName "PassZen"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "PassZen"
#define MyAppURL "https://github.com/theayushgupta08/pass-zen"
#define MyAppExeName "PassZen.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=PassZen-Setup
SetupIconFile=..\..\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The PyInstaller-built executable
Source: "..\..\dist\PassZen.exe"; DestDir: "{app}"; Flags: ignoreversion

; Include icon if it exists
Source: "..\..\assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
