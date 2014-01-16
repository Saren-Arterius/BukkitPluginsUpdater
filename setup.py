from cx_Freeze import setup, Executable

includes = ["pyquery", "cssselect", "lxml", "lxml._elementpath", "lxml.etree"]
includefiles = []
eggsacutibull = Executable(
    script = "main.py",
    initScript = None,
    base = 'Win32GUI',
    targetName = "main.exe",
    compress = True,
    copyDependentFiles = True,
    appendScriptToExe = False,
    appendScriptToLibrary = False,
    icon = None
    )

setup(
        name = "Main",
        version = "0.0.1",
        author = 'Bukkit plugins updater',
        description = "Main",
        options = {"build_exe": {"includes": includes, "include_files": includefiles}},
        executables = [eggsacutibull]
        )