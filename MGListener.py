import threading
import time
import sys
import select
import math

#connect to the Arduino after StandardFirmata is loaded, use to communicate with light
from lighttest import ArduinoController

#Needed for newport motor controller
#from pylablib.devices import Newport
import newport_8742_dotnet as Newport 

# make sure the PicomotorStandAlone.py and mg_pico.py file is in the same directory as this file

import socket
# UDP socket thread to send over x and y values to mg_pico, leave as global vars pls
XY_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# set a port above 5000 and 127.0.0.1 refers to local host
server_address = ('127.0.0.1', 5001)  # Adjust address and port as needed

# second socket to serve to Picomotor StandAlone
Pico_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pico_server_address = ('127.0.0.1', 5002)

"""
This file can be used to capture UDP messages from MetaGuide indicating status of the guiding and many other values.
The core status message is emitted every 0.5s.
Other messages, such as GUIDING, are emitted when an event happens - such as the sending of a guide pulse.
The main MGListener class can be subclassed to perform user-specified operations on receipt of messages.
"""

if sys.version_info < (3, 0):
    print("This code requires Python Version 3")
    sys.exit(-1)

inits = open('inits_log.txt', 'a')

class MGListener(threading.Thread):
    """
    Listens to data messages from MetaGuide broadcast over UDP.
    Runs in separate thread and synchronizes with threadLock
    Default port is 1277 to match default in MetaGuide->Setup->Extra dialog
    """
    def __init__(self, port=1277, timeout=2, deadtime=20):

        # start threading if giving threading error, otherwise comment out
        # threading.Thread.__init__(self)

        self.port = port
        self.relay_port = port+1
        self.timeout = timeout
        self.deadtime = deadtime

        #lenslet variables
        self.x = -1             # x coordinate of centroid
        self.y = -1             # y
        self.x_init = 0        # initial x coordinate
        self.y_init = 0        # initial y coordinate
        self.initialized = False

        #relay variables
        self.relay_x = -1
        self.relay_y = -1
        self.relay_x_init = 0
        self.relay_y_init = 0
        self.relay_initialized = False


        self.ew = 0             # east/west component relative to center of screen
        self.ns = 0             # north/south
        self.ewcos = 0          # east/west component boosted by 1/cos(dec) for axis angle
        self.intens = 0         # intensity: 0 - 255
        self.fwhm = 0           # aligned fwhm arc-sec
        self.seeing = 0         # 2 sec. seeing fwhm arc-sec
        self.guidemode = 0      #
        self.de = 0             # e/w guide error, arc-sec
        self.dn = 0             # n/s
        self.locked = 0         # locked on star
        self.width = 0          # view width
        self.height = 0         # height
        self.calstate = 0       #
        self.tquiet = 9999      # time since no status msg received
        self.exposure = 0       # camera directshow exposure setting as power of 2 integer
        self.gain = 0           # camera directshow gain setting as integer
        self.minexposure = 0    # camera dshow min exposure setting
        self.maxexposure = 0    # camera dshow max exposure setting
        self.mingain = 0        #
        self.maxgain = 0        #
        self.msgtxt = ''        # full text of last msg
        self.msg = 'None'       # msg type
        self.westside = 0       # pier side is west
        self.ra = 0             #
        self.dec = 0            #
        self.tnow = 0           # tnow as system time
        self.time = 0           # time since current or previous log started
        self.wpulse = 0         # guide pulse, ms
        self.npulse = 0         #
        self.rarate = 0         # guide rate as frac. of sidereal
        self.decrate = 0        #
        self.raagg = 0          # aggression on 0-1 scale.  Can be > 1
        self.decagg = 0         #
        self.minmove = 0        # min guide pulse, ms
        self.maxmove = 0        # max guide pulse, ms
        self.decrev = 0         # resist dec reversal - arc-sec
        self.nsrev = 0          # n/s directions reversed
        self.ewrev = 0          # e/w reversed
        self.wangle = 0         # angle on screen of west
        self.parity = 0         # parity
        self.wx = 0             # rotation matrix elements
        self.wy = 0
        self.nx = 0
        self.ny = 0
        self.mountname = 'None' # ascom mount name - emitted only at start
        self.fl = 0
        self.pixsize = 0
        self.arcsecperpixel = 0
        self.guiding = 0
        self.mgversion = "0.0.0"
        self.guidefilterversion = "0.0.0"
        self.arcsecperpix = 0

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(False)
        except:
            print("Error creating lenslet socket")
            return
        try:
            self.relay_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.relay_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.relay_sock.setblocking(False)
        except:
            print("Error creating relay socket")
            return
        try:
            self.sock.bind(('', self.port))
        except:
            print("Error binding to lenslet port", self.port)
            return
        try:
            self.relay_sock.bind(('', self.relay_port))
        except:
            print("Error binding to relay port", self.relay_port)
            return

        self.listenMessages = True
        self.threadLock = threading.Lock()
        self.threadLock.acquire()
        threading.Thread.__init__(self)

    def stop(self):
        self.listenMessages = False
        # need to release the lock and don't care if already released
        try:
            self.threadLock.release()  #metacapture has no threadLock ?
        except:
            pass

    #def doit(self):
    #    """
    #    Subclass this class and insert your functionality here.
    #    """
    #    pass

    def isDead(self):
        print("MG is not responding")
        pass

    def timeSinceLastMsg(self):
        return self.tquiet

    def isAlive(self):
        return self.tquiet < self.deadtime

    def starOK(self):
        return self.x > 0 and self.y > 0 and self.intens > 20

    def allGood(self):
        return self.isAlive() and self.starOK()

    def isGuiding(self):
        return self.guidemode != 0

    def isLocked(self):
        return self.locked != 0

    def getXYI(self):
        return self.x, self.y, self.intens

    def guideError(self):
        if self.starOK():
            return math.sqrt(self.dn**2+self.de**2)
        return 999

    def run(self):
        """
        Worker thread - blocks on data from the socket with timeout
        """
        # print("Running MGListener thread")
        tlastmsg = time.time()
        loop_tracker = 0

        # attempt to give mg guide to find star and set x and y values
        time.sleep(5)

        while self.listenMessages:
            try:
                # non-blocking select with timeout so it doesn't get stuck
                ready = select.select([self.sock], [], [], self.timeout)
                if ready[0]:
                    bmsg, _ = self.sock.recvfrom(1024)

                else:
                    # print("No data received after timeout - keep going")
                    self.tquiet = time.time()-tlastmsg
                    if self.tquiet > self.deadtime:
                        self.isDead()
                    continue
            except:
                print("Error receiving from lenslet socket.  Continuing")
                self.tquiet = time.time()-tlastmsg
                continue

            try:
                ready_relay = select.select([self.relay_sock], [], [], self.timeout)
                if ready_relay[0]:
                    cmsg, _ = self.relay_sock.recvfrom(1024)
                else:
                    print("Relay socket timeout, no data received")
                    self.tquiet = time.time()-tlastmsg
                    if self.tquiet > self.deadtime:
                        self.isDead()
                    continue
            except:
                print("Error receiving from relay socket.  Continuing")
                self.tquiet = time.time()-tlastmsg
                continue


            # for lenslet data from metagudie
            msg = bmsg.decode('utf-8')
            msgs = msg.split()
            ntok = len(msgs)
            self.msgtxt = msg

            #for relay data from second metaguide instance
            relay_msg = cmsg.decode('utf-8')
            relay_msgs = relay_msg.split()
            relay_ntok = len(relay_msgs)
            self.relay_msgtext = relay_msg

            # corrupt message - ignore
            if ntok < 6:
                self.tquiet = time.time()-tlastmsg
                return

            # make sure it is a good packet
            if msgs[0] == 'OPENSCI' and msgs[1] == 'ASTRO' and msgs[3] == 'MG':
                typ = msgs[2]
                if typ == 'CAMERA':
                    if ntok < 11:
                        return
                    self.exposure = int(msgs[5])
                    self.gain = int(msgs[6])
                    self.minexposure = int(msgs[7])
                    self.maxexposure = int(msgs[8])
                    self.mingain = int(msgs[9])
                    self.maxgain = int(msgs[10])
                    self.msg = typ
                elif typ == 'STATUS':
                    if ntok < 23:
                        return
                    self.x = float(msgs[5])
                    self.y = float(msgs[6])
                    self.ew = float(msgs[7])
                    self.ns = float(msgs[8])
                    self.ewcos = float(msgs[9])
                    self.intens = float(msgs[10])
                    self.fwhm = float(msgs[11])
                    self.seeing = float(msgs[12])
                    self.guidemode = int(msgs[13])
                    self.de = float(msgs[14])
                    self.dn = float(msgs[15])
                    self.locked = int(msgs[16])
                    self.width = int(msgs[17])
                    self.height = int(msgs[18])
                    self.calstate = int(msgs[19])
                    self.westside = int(msgs[20])
                    self.ra = float(msgs[21])
                    self.dec = float(msgs[22])
                    if ntok > 23:
                        self.fl = float(msgs[23])
                        self.pixsize = float(msgs[24])
                        self.arcsecperpix = float(msgs[25])
                    if ntok > 26:
                        self.guiding = int(msgs[26])
                    if ntok == 29:
                        self.mgversion = msgs[27]
                        self.guidefilterversion = msgs[28]
                    # only update time of last message when status is received
                    tlastmsg = time.time()
                    self.tquiet = 0
                    self.msg = typ
                elif typ == 'GUIDE':
                    if ntok < 10:
                        return
                    self.tnow = float(msgs[5])  # timeGetTime() in seconds
                    self.time = float(msgs[6])  # time since log start in seconds
                    self.wpulse = int(msgs[7])  # pulse times milliseconds
                    self.npulse = int(msgs[8])
                    self.calstate = int(msgs[9])
                    self.msg = typ
                elif typ == 'GUIDEPARMS':
                    if ntok < 14:
                        return
                    self.rarate = float(msgs[5])
                    self.decrate = float(msgs[6])
                    self.raagg = float(msgs[7])
                    self.decagg = float(msgs[8])
                    self.minmove = float(msgs[9])
                    self.maxmove = float(msgs[10])
                    self.decrev = float(msgs[11])
                    self.nsrev = int(msgs[12])
                    self.ewrev = int(msgs[13])
                    self.msg = typ
                elif typ == 'CALINFO':
                    if ntok < 11:
                        return
                    self.wangle = float(msgs[5])
                    self.parity = int(msgs[6])
                    self.wx = float(msgs[7])
                    self.wy = float(msgs[8])
                    self.nx = float(msgs[9])
                    self.ny = float(msgs[10])
                    self.msg = typ
                elif typ == 'MOUNTNAME':
                    if ntok < 6:
                        return
                    self.mountname = msgs[5]
                    self.msg = typ
            else:
                self.tquiet = time.time()-tlastmsg
                return


            #for the relay secondary system
            if relay_msgs[0] == 'OPENSCI' and relay_msgs[1] == 'ASTRO' and relay_msgs[3] == 'MG':
                typ = relay_msgs[2]
                if typ == 'CAMERA':
                    if relay_ntok < 11:
                        return
                    self.relay_exposure = int(relay_msgs[5])
                    self.relay_gain = int(relay_msgs[6])
                    self.relay_minexposure = int(relay_msgs[7])
                    self.relay_maxexposure = int(relay_msgs[8])
                    self.relay_mingain = int(relay_msgs[9])
                    self.relay_maxgain = int(relay_msgs[10])
                    self.relay_msg = typ
                elif typ == 'STATUS':
                    if relay_ntok < 23:
                        return
                    self.relay_x = float(relay_msgs[5])
                    self.relay_y = float(relay_msgs[6])
                    self.relay_ew = float(relay_msgs[7])
                    self.relay_ns = float(relay_msgs[8])
                    self.relay_ewcos = float(relay_msgs[9])
                    self.relay_intens = float(relay_msgs[10])
                    self.relay_fwhm = float(relay_msgs[11])
                    self.relay_seeing = float(relay_msgs[12])
                    self.relay_guidemode = int(relay_msgs[13])
                    self.relay_de = float(relay_msgs[14])
                    self.relay_dn = float(relay_msgs[15])
                    self.relay_locked = int(relay_msgs[16])
                    self.relay_width = int(relay_msgs[17])
                    self.relay_height = int(relay_msgs[18])
                    self.relay_calstate = int(relay_msgs[19])
                    self.relay_westside = int(relay_msgs[20])
                    self.relay_ra = float(relay_msgs[21])
                    self.relay_dec = float(relay_msgs[22])
                    if relay_ntok > 23:
                        self.relay_fl = float(relay_msgs[23])
                        self.relay_pixsize = float(relay_msgs[24])
                        self.relay_arcsecperpix = float(relay_msgs[25])
                    if relay_ntok > 26:
                        self.relay_guiding = int(relay_msgs[26])
                    if relay_ntok == 29:
                        self.relay_mgversion = relay_msgs[27]
                        self.relay_guidefilterversion = relay_msgs[28]
                    # only update time of last message when status is received
                    tlastmsg = time.time()
                    self.relay_tquiet = 0
                    self.relay_msg = typ
                elif typ == 'GUIDE':
                    if relay_ntok < 10:
                        return
                    self.relay_tnow = float(relay_msgs[5])  # timeGetTime() in seconds
                    self.relay_time = float(relay_msgs[6])  # time since log start in seconds
                    self.relay_wpulse = int(relay_msgs[7])  # pulse times milliseconds
                    self.relay_npulse = int(relay_msgs[8])
                    self.relay_calstate = int(relay_msgs[9])
                    self.relay_msg = typ
                elif typ == 'GUIDEPARMS':
                    if relay_ntok < 14:
                        return
                    self.relay_rarate = float(relay_msgs[5])
                    self.relay_decrate = float(relay_msgs[6])
                    self.relay_raagg = float(relay_msgs[7])
                    self.relay_decagg = float(relay_msgs[8])
                    self.relay_relay_minmove = float(relay_msgs[9])
                    self.relay_maxmove = float(relay_msgs[10])
                    self.relay_decrev = float(relay_msgs[11])
                    self.relay_nsrev = int(relay_msgs[12])
                    self.relay_ewrev = int(relay_msgs[13])
                    self.relay_msg = typ
                elif typ == 'CALINFO':
                    if relay_ntok < 11:
                        return
                    self.relay_wangle = float(relay_msgs[5])
                    self.relay_parity = int(relay_msgs[6])
                    self.relay_wx = float(relay_msgs[7])
                    self.relay_wy = float(relay_msgs[8])
                    self.relay_nx = float(relay_msgs[9])
                    self.relay_ny = float(relay_msgs[10])
                    self.relay_msg = typ
                elif typ == 'MOUNTNAME':
                    if relay_ntok < 6:
                        return
                    self.relay_mountname = relay_msgs[5]
                    self.relay_msg = typ
            else:
                self.relay_tquiet = time.time() - tlastmsg
                return

            # only get here if a good message was received and parsed
            # now invoke the user's function in a subclass
            if loop_tracker == 0 and (self.x > 0 or self.y > 0):
                if self.x != -1.00 and self.relay_x != -1.00:
                    self.firstxy()
                    loop_tracker = loop_tracker + 1

            self.doit()

            # Release the lock and don't care if already released
            try:
                self.threadLock.release()
            except:
                pass
        XY_sock.close()
        Pico_sock.close()

class MyListener(MGListener):
    """
    Simple example showing how to subclass MGListener to act on data from MetaGuide
    """
    def firstxy(self):
        time.sleep(0.01)
        self.x_init = self.x
        self.y_init = self.y

        self.relay_x_init = self.relay_x
        self.relay_y_init = self.relay_y

        #testing
        print('inital relay coordinates are x,y:' + str((round(self.relay_x_init, 4))) +', '+ str(round(self.relay_y_init, 4)))

        inits.write('initials lenslet pixels (x,y): ' + str(round(self.x_init, 4)) + ', ' + str(round(self.y_init, 4)))

        #think about relay inits write file, for the return home feature
        #inits.write('initials relay pixels (x,y): ' + str(round(self.relay_x_init, 4)) + ', ' + str(round(self.relay_y_init, 4)))

        self.initialized = True
        self.relay_initialized = True

        #print("Initial X, Y of the star are: ", self.x_init, self.y_init")


    def doit(self):
        delta_x = self.x - self.x_init
        delta_y = self.y - self.y_init
        #print("x:" + str(self.x) + " y: " + str(self.y) + " delt x: " + str(delta_x) + " delt y: " + str(delta_y))
        #print("%s : %s"%(self.msg, self.msgtxt))

        # Send delt_x and delt_y
        message = f'{delta_x},{delta_y},{self.x},{self.y}'

        # if self.x != -1 and self.initialized:
        #     XY_sock.sendto(message.encode(), server_address)
        #     Pico_sock.sendto(message.encode(), pico_server_address)

        XY_sock.sendto(message.encode(), server_address)
        Pico_sock.sendto(message.encode(), pico_server_address)

class MGMonitor(threading.Thread):
    """
    Handles data caught by MGListener and does something with the data.

    Runs in separate thread and blocks on threadLock for new data
    """
    def __init__(self, mgl):
        self.mgl = mgl
        self.mgl.threadLock.acquire()
        threading.Thread.__init__(self)

    def dumpState(self):
        """
        This call can be replaced by whatever you want to do with the info from MG
        """
        print(self.mgl.x, self.mgl.y, self.mgl.ew, self.mgl.ns, self.mgl.intens, self.mgl.fwhm, self.mgl.de, self.mgl.dn, self.mgl.sock)

    def run(self):
        """
        Worker thread - blocks waiting for new data caught by MGListener
        """
        while True:
            self.mgl.threadLock.acquire()
            if not self.mgl.listenMessages:
                return
            #self.dumpState()

if __name__ == '__main__':
    """
    Simple example showing how you can subclass MGListener to act on your own doit() function when a UDP message is received
    """
    # Set up another UDP socket to send delta x and delta y to mg_pico


    ml = MyListener()
    ml.start()
    input("Press to end\n")
    ml.stop()
    ml.join()

    #return

    """
    Alternate approach

    Start an instance of MGListener and MGMonitor in separate threads.

    Make sure to start the MGListener with the correct UDP port - as set in the MetaGuide->Setup->Extra page
    The MGMonitor contains an instance of MGListener and they share a lock
    """

    """
    mgl = MGListener(1277)
    mgl.start()
    mgm = MGMonitor(mgl)
    mgm.start()
    input("Press enter to end program\n\n")
    mgl.stop()
    mgl.join()
    mgm.join()
    return
    """
