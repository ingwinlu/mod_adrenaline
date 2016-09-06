import os
import py_compile
import zipfile

WOTVersion = "0.9.15.1.1"
TARGET = "mod_adrenaline.zip"
SRC = "mod_adrenaline.py"
_COMPILED = SRC + 'c'

if os.path.exists(TARGET):
    os.remove(TARGET)

py_compile.compile("src/" + SRC)
fZip = zipfile.ZipFile(TARGET, "w")
fZip.write("src/" + _COMPILED, WOTVersion+"/scripts/client/gui/mods/"+_COMPILED)
fZip.write("src/" + "dlc.exe", WOTVersion+"/scripts/client/gui/mods/adrenaline/dlc.exe")
fZip.write("src/" + "ikpFlac.dll", WOTVersion+"/scripts/client/gui/mods/adrenaline/ikpFlac.dll")
fZip.write("src/" + "irrKlang.dll", WOTVersion+"/scripts/client/gui/mods/adrenaline/irrKlang.dll")
fZip.write("src/" + "ikpMP3.dll", WOTVersion+"/scripts/client/gui/mods/adrenaline/ikpMP3.dll")
fZip.write("src/" + "adrenaline.mp3", WOTVersion+"/scripts/client/gui/mods/adrenaline/adrenaline.mp3")

fZip.close()
