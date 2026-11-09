' Start the question-bank proxy on 127.0.0.1:8765 without a console window.
' Pure ASCII on purpose: paths are resolved at runtime, so non-ASCII folder
' names do not get mangled by script encoding.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
base = fso.GetParentFolderName(WScript.ScriptFullName)
pyw  = "C:\Users\Neko_thinkbook\AppData\Local\Programs\Python\Python311\pythonw.exe"
cmd  = """" & pyw & """ """ & base & "\" & ChrW(&H9898) & ChrW(&H5E93) & ChrW(&H670D) & ChrW(&H52A1) & ".py" & """ --no-open"
sh.CurrentDirectory = base
sh.Run cmd, 0, False
