import os
import py_compile
import zipfile

WOTVersion = "0.9.15.1.1"
TARGET = "wotadrenaline.zip"
FILE = "mod_wotadrenaline.py"
_COMPILED = FILE + 'c'

if os.path.exists(TARGET):
    os.remove(TARGET)

py_compile.compile("src/" + SRC)
fZip = zipfile.ZipFile(TARGET, "w")
fZip.write(_COMPILED, WOTVersion+"/scripts/client/gui/mods/"+_COMPILED)
#fZip.write("data/mod_wotxp.json", WOTVersion+"/scripts/client/gui/mods/mod_wotxp.json")
fZip.close()
