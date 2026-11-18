; LocalRAW Windows installer (built by GitHub Actions)
; The version comes from the app itself: the workflow passes /DAppVersion=...
#ifndef AppVersion
  #define AppVersion "0"
#endif
[Setup]
AppId={{2B7C9E41-6D1A-4F63-8E55-4C4F43414C52}
AppName=LocalRAW
AppVersion={#AppVersion}
AppPublisher=The Art Medium (ImageStream)
AppPublisherURL=https://the-artmedium.github.io/ImageStream/
DefaultDirName={autopf}\LocalRAW
DefaultGroupName=LocalRAW
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=LocalRAW-Setup-Windows
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\LocalRAW.exe
LicenseFile=..\LICENSE

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\LocalRAW\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\LocalRAW"; Filename: "{app}\LocalRAW.exe"
Name: "{autodesktop}\LocalRAW"; Filename: "{app}\LocalRAW.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LocalRAW.exe"; Description: "Open LocalRAW now"; Flags: nowait postinstall skipifsilent
