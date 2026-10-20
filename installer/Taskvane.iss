; Taskvane installer (Inno Setup 6). Built by build.ps1, which passes /DAppVersion=x.y.z
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "Taskvane"
#define AppExe "Taskvane.exe"

[Setup]
AppId={{915F6E67-524F-4F03-9FD9-8ABCA6D39DD9}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Taskvane
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#AppName}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
SetupIconFile=..\assets\icon.ico
WizardStyle=modern
WizardSizePercent=110
OutputDir=..\release
OutputBaseFilename=Taskvane-{#AppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
; Program Files + the elevated scheduled task need admin rights during setup.
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; PawnIO (installed separately, for CPU sensors) needs Windows 10 1809 (RS5) or later.
MinVersion=10.0.17763
; We close the app ourselves (it may be running elevated) with Taskvane.exe --quit.
CloseApplications=no
InfoBeforeFile=welcome.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"
Name: "alwaysadmin"; Description: "Always start Taskvane as administrator, so CPU sensors work without a UAC prompt"; GroupDescription: "CPU sensors:"
Name: "autostart"; Description: "Start Taskvane when I sign in to Windows"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
Source: "..\dist\Taskvane\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; 1.2.0 bundled PawnIO's setup; upgrades shouldn't keep it.
Type: filesandordirs; Name: "{app}\_internal\lib\pawnio"

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; Comment: "Live CPU, GPU, memory, temperatures and power"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
; Startup options go through the app itself (elevated scheduled task and/or Run entry).
Filename: "{app}\{#AppExe}"; Parameters: "--set-startup {code:AdminFlag} {code:AutostartFlag}"; StatusMsg: "Configuring startup..."; Flags: runhidden waituntilterminated
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
Filename: "{app}\{#AppExe}"; Parameters: "--quit"; Flags: runhidden waituntilterminated; RunOnceId: "QuitApp"
Filename: "{app}\{#AppExe}"; Parameters: "--set-startup 0 0"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveStartup"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function AdminFlag(Param: String): String;
begin
  if WizardIsTaskSelected('alwaysadmin') then Result := '1' else Result := '0';
end;

function AutostartFlag(Param: String): String;
begin
  if WizardIsTaskSelected('autostart') then Result := '1' else Result := '0';
end;

function WebView2Installed(): Boolean;
var
  V: String;
begin
  Result :=
    (RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', V) and (V <> '') and (V <> '0.0.0.0')) or
    (RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', V) and (V <> '') and (V <> '0.0.0.0'));
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  if not WebView2Installed() then
  begin
    if MsgBox('Taskvane needs the Microsoft Edge WebView2 Runtime, which is not installed on this PC ' +
              '(it is built into Windows 11 and most Windows 10 PCs).' + #13#10#13#10 +
              'Open the download page now? You can install it and run this setup again.',
              mbConfirmation, MB_YESNO) = IDYES then
      ShellExec('open', 'https://developer.microsoft.com/microsoft-edge/webview2/', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    Result := False;
  end;
end;

// Close a running copy (possibly elevated) before files are replaced.
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  Code: Integer;
begin
  Result := '';
  if FileExists(ExpandConstant('{app}\{#AppExe}')) then
  begin
    Exec(ExpandConstant('{app}\{#AppExe}'), '--quit', '', SW_HIDE, ewWaitUntilTerminated, Code);
    Sleep(2000);
  end;
end;

// Offer to remove settings and logs on uninstall.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  // Never in silent mode: /SUPPRESSMSGBOXES would answer Yes, and scripted/winget
  // uninstalls must not delete user data.
  if (CurUninstallStep = usPostUninstall) and not UninstallSilent() and DirExists(ExpandConstant('{userappdata}\Taskvane')) then
    if MsgBox('Also delete your Taskvane settings and logs?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      DelTree(ExpandConstant('{userappdata}\Taskvane'), True, True, True);
end;
