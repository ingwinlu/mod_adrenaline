"""
mod_adrenaline

@author: winlu
"""

import BigWorld
import os
import ResMgr
import subprocess
import threading
from Avatar import PlayerAvatar
from CurrentVehicle import g_currentVehicle
from gui.app_loader.loader import _AppLoader
from gui.shared import g_itemsCache
from pprint import pprint
from Vehicle import Vehicle

"""
XFW Library (c) www.modxvm.com 2013-2016
https://bitbucket.org/XVM/xfw/raw/4c3f96558359a66f510192aebacd2af785561ae9/src/python/mods/xfw/python/xfw/events.py
"""

# EventHook
class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler


#####################################################################
# Register events

def _RegisterEvent(handler, cls, method, prepend=False):
    evt = '__event_%i_%s' % ((1 if prepend else 0), method)
    if hasattr(cls, evt):
        e = getattr(cls, evt)
    else:
        newm = '__orig_%i_%s' % ((1 if prepend else 0), method)
        setattr(cls, evt, EventHook())
        setattr(cls, newm, getattr(cls, method))
        e = getattr(cls, evt)
        m = getattr(cls, newm)
        setattr(cls, method, lambda *a, **k: __event_handler(prepend, e, m, *a, **k))
    e += handler

def __event_handler(prepend, e, m, *a, **k):
    try:
        if prepend:
            e.fire(*a, **k)
            r = m(*a, **k)
        else:
            r = m(*a, **k)
            e.fire(*a, **k)
        return r
    except:
        logtrace(__file__)

def _override(cls, method, newm):
    orig = getattr(cls, method)
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))

def _OverrideMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = lambda *a, **k: handler(orig, *a, **k)
    _override(cls, method, newm)

def _OverrideStaticMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = staticmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)

def _OverrideClassMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = classmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)


#####################################################################
# Decorators

def _hook_decorator(func):
    def decorator1(*a, **k):
        def decorator2(handler):
            func(handler, *a, **k)
        return decorator2
    return decorator1

registerEvent = _hook_decorator(_RegisterEvent)
overrideMethod = _hook_decorator(_OverrideMethod)
overrideStaticMethod = _hook_decorator(_OverrideStaticMethod)
overrideClassMethod = _hook_decorator(_OverrideClassMethod)

""" XFW import end """

g_versionWot = '0.9.17.0'
g_versionMod = '0.1'
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


@overrideMethod(Vehicle, 'onEnterWorld')
def healthWatcher_start(orig, *args, **kwargs):
    global g_warnActive
    g_warnActive = True
    return orig(*args, **kwargs)


@overrideMethod(PlayerAvatar, '_PlayerAvatar__destroyGUI')
def healthWatcher_reset(orig, *args, **kwargs):
    global g_warnActive
    g_warnActive = False
    return orig(*args, **kwargs)


@overrideMethod(Vehicle, 'onHealthChanged')
def adrenaline_onHealthChanged(orig, self, newHealth, attackerId, attackReasonID):
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
    return orig(self, newHealth, attackerId, attackReasonID)


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

initialize()
