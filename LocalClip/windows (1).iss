; LocalClip Windows installer (built by GitHub Actions)
; The version comes from the app itself: the workflow passes /DAppVersion=...
#ifndef AppVersion
  #define AppVersion "0"
#endif
[Setup]
AppId={{7A1E5C33-9B2D-4E80-A6F1-4C4C49504C43}
AppName=LocalClip
AppVersion={#AppVersion}
AppPublisher=The Art Medium (ImageStream)
AppPublisherURL=https://the-artmedium.github.io/ImageStream/
DefaultDirName={autopf}\LocalClip
DefaultGroupName=LocalClip
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=LocalClip-Setup-Windows
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\LocalClip.exe
SetupIconFile=..\resources\icon.ico
LicenseFile=..\LICENSE

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\LocalClip\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\LocalClip"; Filename: "{app}\LocalClip.exe"
Name: "{autodesktop}\LocalClip"; Filename: "{app}\LocalClip.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LocalClip.exe"; Description: "Open LocalClip now"; Flags: nowait postinstall skipifsilent
