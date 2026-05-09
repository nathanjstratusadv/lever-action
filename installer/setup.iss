; Lever Action Installer Script
; Generated for Inno Setup 6

#define Version GetEnv('Version')
#define SourceDir GetEnv('DistDir')
#define ProjectDir GetEnv('ProjectDir')

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName=Lever Action
AppVersion={#Version}
AppPublisher=Lever Action
AppPublisherUrl=https://github.com/nathan-johnson/lever_action
AppSupportUrl=https://github.com/nathan-johnson/lever_action/issues
AppUpdatesUrl=https://github.com/nathan-johnson/lever_action/releases
DefaultDirName={localappdata}\LeverAction
DefaultGroupName=Lever Action
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputDir={#ProjectDir}\dist\
OutputBaseFilename=LeverAction-Setup
SetupIconFile={#ProjectDir}\reticle.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
ChangesAssociations=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lever Action"; Filename: "{app}\lever_action.exe"; IconFilename: "{app}\lever_action.exe"; IconIndex: 0
Name: "{userdesktop}\Lever Action"; Filename: "{app}\lever_action.exe"; IconFilename: "{app}\lever_action.exe"; IconIndex: 0; Tasks: desktopicon

[Run]
Filename: "{app}\lever_action.exe"; Description: "{cm:LaunchProgram,Lever Action}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
