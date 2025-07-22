[Setup]
; ชื่อโปรแกรม
AppName=SIENG - Secure Incognito ENcryption Guard
; เวอร์ชัน
AppVersion=1.0
; ผู้พัฒนา
AppPublisher=Mik And Max
; เว็บไซต์
;AppPublisherURL=https://yourwebsite.com 
; ลิงก์เว็บไซต์โปรแกรม
;AppSupportURL=https://yourwebsite.com 
; ลิงก์อีเมล
AppUpdatesURL=65011212031@msu.ac.th

; โฟลเดอร์เริ่มต้น (เช่น Program Files)
DefaultDirName={pf}\SIENG
; ชื่อโฟลเดอร์ใน Start Menu
DefaultGroupName=SIENG
; ไอคอนโปรแกรม
SetupIconFile=myicon_in.ico
; ขนาดไฟล์ติดตั้ง
OutputBaseFilename=SIENG_Installer
; ภาษาที่รองรับ
UsePreviousAppSettingsDuringSetup=True
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "thai"; MessagesFile: "compiler:Languages\Thai.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\sieng_app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "audioexample\*"; DestDir: "{app}\audioexample"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "photoexample\*"; DestDir: "{app}\photoexample"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tabs\*"; DestDir: "{app}\tabs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "vdio\*"; DestDir: "{app}\vdio"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commondesktop}\SIENG"; Filename: "{app}\sieng_app.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{group}\SIENG"; Filename: "{app}\sieng_app.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Visit Our Website"; Filename: "https://yourwebsite.com "

[Run]
Filename: "{app}\sieng_app.exe"; Description: "Launch SIENG"; Flags: nowait postinstall skipifsilent