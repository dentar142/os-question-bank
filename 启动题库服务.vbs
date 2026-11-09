' Start the question-bank proxy on 127.0.0.1:8765 without a console window.
' Pure ASCII on purpose: paths are resolved at runtime, so non-ASCII folder
' names do not get mangled by script encoding. Requires pythonw.exe on PATH.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
base = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = base
sh.Run "pythonw.exe """ & base & "\" & ChrW(&H9898) & ChrW(&H5E93) & ChrW(&H670D) & ChrW(&H52A1) & ".py"" --no-open", 0, False
