import win32api
import win32con
import win32com.client

"""
This script shows how to use windows messaging to control MetaGuide and make it respond to commands
"""

idlog        = win32api.RegisterWindowMessage("MG_RemoteLog")
idunlog      = win32api.RegisterWindowMessage("MG_RemoteUnLog")
idsaveimage  = win32api.RegisterWindowMessage("MG_RemoteSaveImage")
idmark       = win32api.RegisterWindowMessage("MG_RemoteMarkLog")
idguide      = win32api.RegisterWindowMessage("MG_RemoteGuide")
idunguide    = win32api.RegisterWindowMessage("MG_RemoteUnGuide")
idsetshift   = win32api.RegisterWindowMessage("MG_RemoteSetShift")
idstartshift = win32api.RegisterWindowMessage("MG_RemoteShift")
idstopshift  = win32api.RegisterWindowMessage("MG_RemoteUnShift")
idexit       = win32api.RegisterWindowMessage("MG_RemoteExit")
iddither     = win32api.RegisterWindowMessage("MG_RemoteDither")
idmeridianflip = win32api.RegisterWindowMessage("MG_RemoteMeridianFlip")
idrotatorangle = win32api.RegisterWindowMessage("MG_RemoteRotatorAngle")
# me attempt : idlock       = win32api.RegisterWindowMessage('MG_Lock')

# example to shift by +10"/hour in RA and -10"/hour in Dec:
# Rate is based on 10000 + SignedArcSecPerHour
win32api.PostMessage(win32con.HWND_BROADCAST, idsetshift, 10010, 9990)

# start shift (this assumes you are guiding)
win32api.PostMessage(win32con.HWND_BROADCAST, idstartshift, 0, 0)
print("now shifting at +10, -10 arc-sec per hour")
win32api.Sleep(5000)

# stop shift
win32api.PostMessage(win32con.HWND_BROADCAST, idstopshift, 0, 0)

# save image
win32api.PostMessage(win32con.HWND_BROADCAST, idsaveimage, 0, 0)
win32api.Sleep(2000)

# start log
win32api.PostMessage(win32con.HWND_BROADCAST, idlog, 0, 0)
win32api.Sleep(2000)

# mark the log with two separate numbers to indicate events in the log
win32api.PostMessage(win32con.HWND_BROADCAST, idmark, 9998, 0)
win32api.Sleep(2000)

win32api.PostMessage(win32con.HWND_BROADCAST, idmark, 9999, 0)
win32api.Sleep(2000)

# stop the log
win32api.PostMessage(win32con.HWND_BROADCAST, idunlog, 0, 0)
win32api.Sleep(2000)

#shut down MG
win32api.PostMessage(win32con.HWND_BROADCAST, idexit, 0, 0)
