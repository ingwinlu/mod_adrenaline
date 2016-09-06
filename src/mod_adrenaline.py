"""
mod_adrenaline

@author: winlu
"""

exec 'eJytUsFu2zAMvfsreLMcGO69ww7dWmwG1iWI0/ZQDIEsyY5WWXIpeln/flJSJ14TDBswnki+R/GJZIOuA+eLntMGdNc7JNBeagTugSdNhJfK37Y4oq5XtlKCtLORU+85H3T74NDIkbVt162iBTo5CLpX6F/pTZI0DqEGbaFmaVFcxM6++NmZNHtMFzFIvxU/uBmUZ9llAq+mG+CsLrivCLVtJ8hoHN7DkfAOalT8KUmkakCy5xy2OahJGQZ6kMiJkO2gA0IBMbyrJYcZz2E2e7qEZ4b5GB2ZflKfh7ogkl56xTALQwTrCHoM80J6AWW8OkSMsmyvTP2zMh8ALTpFGyfZH2X+T52CNYMVE5ExadmMY+t33bbRO7OVyOvYhltpFJ7BR4vPj7T4hd/fPSlDRQNa6JI3CZskwnDv4WG+Wt+tyi/VseXt/LoKA0wv0uK705Y9hjmlXqDuyafBFUYrS9HrnAxXeOy6uFp9DpX8kLi/WVbl/GvI0dAbxTreM20ph4Zlhe+NpnDbaTZZwae7cv33AtpBn9MxD32X5fXN2zMQTGanrHW1ulqVH0/Jar9VA6F/nYPIQe4Oo/kFHXkf/w=='.decode('base64').decode('zlib')

import BigWorld
import os
import ResMgr
import subprocess
import threading
from CurrentVehicle import g_currentVehicle
from gui.app_loader.loader import _AppLoader
from gui.shared import g_itemsCache
from pprint import pprint
from Vehicle import Vehicle

g_versionMod = '0.1'
g_versionWot = '0.9.15.1.1'
g_mp3Player = None
g_mp3File = None
g_selectedTank = None
g_warnActive = False
g_hasAdrenalineRush = False


def initialize():
    global g_mp3Player
    global g_mp3File
    print('mod_adrenaline v.%s (%s)' % (g_versionMod, g_versionWot))
    globalPath = getGlobalPath()
    modPath = os.path.normpath(os.path.join(globalPath, os.path.join('scripts', 'client', 'gui', 'mods', 'adrenaline')))
    g_mp3Player = os.path.join(modPath, 'dlc.exe')
    g_mp3File = os.path.join(modPath, 'adrenaline.mp3')
    tankCheckCallback()


def getGlobalPath():
    globalPath = None
    res = ResMgr.openSection('../paths.xml')
    sb = res['Paths']
    values = sb.values()[0:2]
    for val in values:
        path = val.asString + '/'
        if os.path.isdir(path):
            globalPath = path
    return globalPath


def tankCheckCallback():
    global g_selectedTank
    if g_currentVehicle.isInHangar:
        currentTank = g_currentVehicle.item
        if g_selectedTank is not currentTank and currentTank is not None:
            onCurrentVehicleChanged(currentTank)
            g_selectedTank = currentTank
    BigWorld.callback(0.1, tankCheckCallback)


def onCurrentVehicleChanged(currentTank):
    global g_hasAdrenalineRush

    tankmen = g_itemsCache.items.getTankmen()
    for tankman in tankmen.itervalues():
        if tankman.isInTank and tankman.vehicleInvID != currentTank.invID:
            continue
        if tankman.vehicleInvID == currentTank.invID and \
          'loader_desperado' in tankman.skillsMap:
            desperado = tankman.skillsMap['loader_desperado']
            if desperado.isActive and desperado.isEnable:
                g_hasAdrenalineRush = True
                return
    g_hasAdrenalineRush = False
    return


def healthWatcher_start():
    global g_warnActive
    g_warnActive = True

def healthWatcher_reset():
    global g_warnActive
    g_warnActive = False


def ADR_new_onHealthChanged(self, newHealth, attackerId, attackReasonID):
    ADR_orig_onHealthChanged(self, newHealth, attackerId, attackReasonID)

    global g_warnActive
    if BigWorld.player().playerVehicleID == self.id:
        health_current = self.health * 1.0
        health_max = self.typeDescriptor.maxHealth * 1.0
        if self.isAlive() and \
                health_current / health_max < 0.1 and \
                g_warnActive and \
                g_hasAdrenalineRush:
            g_warnActive = False
            BigWorld.callback(0.1, do_notify)


ADR_orig_onHealthChanged = Vehicle.onHealthChanged
Vehicle.onHealthChanged = ADR_new_onHealthChanged


def do_notify():
    pprint('mod_adrenaline: adrenaline rush active')
    audio_thread=threading.Thread(target=external_audio_player)
    audio_thread.start()


def external_audio_player():
    proc = subprocess.STARTUPINFO()
    proc.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc.wShowWindow = subprocess.SW_HIDE
    audio_path = g_mp3Player + ' -p ' + g_mp3File
    subprocess.Popen(audio_path, startupinfo=proc)


@WOT_UTILS.OVERRIDE(_AppLoader, 'showBattle')
def hooked_showBattle(baseMethod, baseObject):
    baseMethod(baseObject)
    healthWatcher_start()


@WOT_UTILS.OVERRIDE(_AppLoader, 'destroyBattle')
def hooked_destroyBattle(baseMethod, baseObject):
    baseMethod(baseObject)
    healthWatcher_reset()


initialize()
