Set WshShell = CreateObject("WScript.Shell")
appDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
appRoot = CreateObject("Scripting.FileSystemObject").GetParentFolderName(appDir)
WshShell.CurrentDirectory = appRoot
WshShell.Run Chr(34) & appDir & "\Launch-SDS.bat" & Chr(34), 0, False
