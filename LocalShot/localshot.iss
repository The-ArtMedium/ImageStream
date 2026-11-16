; LocalShot Windows installer (built by GitHub Actions)
#ifndef AppVersion
  #define AppVersion "1.1.0"
#endif

[Setup]
AppId={{765AB5EF-2EFA-4145-A888-9BAAD95FA232}
AppName=LocalShot
AppVersion={#AppVersion}
AppPublisher=The Art Medium (ImageStream)
AppPublisherURL=https://the-artmedium.github.io/ImageStream/
DefaultDirName={autopf}\LocalShot
DefaultGroupName=LocalShot
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=..\installer-out
OutputBaseFilename=LocalShot-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=LocalShot

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\LocalShot\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\LocalShot"; Filename: "{app}\LocalShot.exe"
Name: "{autodesktop}\LocalShot"; Filename: "{app}\LocalShot.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LocalShot.exe"; Description: "Open LocalShot now"; Flags: nowait postinstall skipifsilent
