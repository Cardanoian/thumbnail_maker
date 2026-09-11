#define MyAppName "썸네일 JPG 변환기"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "포항원동초등학교 김지원"
#define MyAppExeName "ThumbnailMaker.exe"

[Setup]
AppId={{E7C3D91A-4B2F-4A6E-9C11-8F0D2A1B7E44}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright=© {#MyAppPublisher}
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=© {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
DefaultDirName={autopf}\ThumbnailMaker
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=ThumbnailMaker_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\ThumbnailMaker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "지금 실행"; Flags: nowait postinstall skipifsilent
