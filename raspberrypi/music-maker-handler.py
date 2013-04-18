# This code is copyright ...... under the GPL v2.
# This code is derived from scratch_gpio_handler by Simon Walters, which
# is derived from scratch_handler by Thomas Preston
# Version 0.1: It's kind of working.

from array import *
import threading
import socket
import time
import sys
import struct
import serial
import io
import datetime as dt
import logging

'''
from Tkinter import Tk
from tkSimpleDialog import askstring
root = Tk()
root.withdraw()
'''

PORT = 42001
DEFAULT_HOST = '127.0.0.1'
BUFFER_SIZE = 240 #used to be 100
SOCKET_TIMEOUT = 1
DEVICES = ['/dev/ttyACM0']
#DRUM_DEVICE = '/dev/ttyACM0'
#GUITAR_DEVICE = '/dev/ttyUSB1'
#MARACAS_DEVICE = '/dev/ttyACM1'
ARDUINO_BAUD_RATE = 57600

BROADCAST_NAMES = {'guitar': 'guitar', 
    'drum': {0: 'cymbal',
        1: 'hihat',
        2: 'slowdrum',
        3: 'snare',
        4: 'tomtom'},
    'maracas': 'maracas'}

SENSOR_NAMES = {'guitar': 'guitar_pitch'}

#DRUM_INSTRUMENT_NAMES = {0: 'cymbal',
    #1: 'hihat',
    #2: 'slowdrum',
    #3: 'snare',
    #4: 'tomtom'}

#DRUM_VALUE_NAMES = {0: 'drum-volume',
    #1: 'drum-volume',
    #2: 'drum-volume',
    #3: 'drum-volume',
    #4: 'drum-volume'}

#GUITAR_INSTRUMENT_NAMES = {0: 'guitar'}
#GUITAR_VALUE_NAMES = {0: 'guitar_pitch'}

#MARACAS_INSTRUMENT_NAMES = {0: 'maracas', 2: 'maracas'}
#MARACAS_VALUE_NAMES = {0: 'maracas_vigour', 2: 'maracas_vigour'}

logging.basicConfig(level = logging.INFO)
#logging.basicConfig(level = logging.DEBUG)

class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ScratchSender(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.scratch_socket = socket
        self._stop = threading.Event()
        
    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stop.set()
        threading.Thread.join(self, timeout)

    #def stop(self):
        #self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        # Detect sensors here
        while not self.stopped():
            time.sleep(0.01) # be kind to cpu - not certain why :)

    def send_scratch_command(self, cmd):
        n = len(cmd)
        a = array('c')
        a.append(chr((n >> 24) & 0xFF))
        a.append(chr((n >> 16) & 0xFF))
        a.append(chr((n >>  8) & 0xFF))
        a.append(chr(n & 0xFF))
        self.scratch_socket.send(a.tostring() + cmd)


class ArduinoListener(threading.Thread):
    def __init__(self, device, speed, sender, instruments, values):
        threading.Thread.__init__(self)
        self.arduino_device = serial.Serial(device, speed, timeout=0.5)
        self._stop = threading.Event()
        self.scratch_sender = sender
        self.instruments = instruments
        self.values = values  

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stop.set()
        threading.Thread.join(self, timeout)

    #def stop(self):
        #self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        self.arduino_device.readline() # discard the first (partial) line
        while not self.stopped():
            logging.debug('Thread waiting for a signal')
            try:
                device_line = self.arduino_device.readline()
                if device_line :
                    instrument, instrument_value_string = device_line.rstrip().split(',', 1)
                    instrument_value = int(instrument_value_string)
                    logging.info('Instrument: %s, Value: %d' % (instrument, instrument_value))
                    if instrument in self.values:
                        try:
                            logging.info("sensor-update %s %d" % (self.values[instrument], (instrument_value * 100) / 1024))
                            self.scratch_sender.send_scratch_command("sensor-update %s %d" % (self.values[instrument], (instrument_value * 100) / 1024))
                        except KeyError:
                            # Do nothing
                            pass
                    if isinstance(self.instruments[instrument], dict):
                        broadcast = self.instruments[instrument][instrument_value]
                    else:
                        broadcast = self.instruments[instrument]
                    try:
                        logging.info("broadcast %s" % broadcast)
                        self.scratch_sender.send_scratch_command('broadcast %s' % broadcast)
                    except KeyError:
                        # Do nothing
                        pass

            except serial.SerialException:
                logging.error('Serial exception')
        logging.debug('Thread run() exiting')



def create_socket(host, port):
    while True:
        try:
            logging.info('Connecting to Scratch')
            scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            scratch_sock.connect((host, port))
            break
        except socket.error:
            logging.warning("There was an error connecting to Scratch!")
            logging.warning("I couldn't find a Mesh session at host: %s, port: %s" % (host, port) )
            time.sleep(3)
            #sys.exit(1)

    return scratch_sock

def cleanup_threads(threads):
    logging.debug("Stopping %d threads" % len(threads))
    #for thread in threads:
        #thread.stop()
    #logging.debug("Threads stopped")
    for thread in threads:
        thread.join()
    logging.debug("Threads joined")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = DEFAULT_HOST


cycle_trace = 'start'
while True:
    if (cycle_trace == 'disconnected'):
        logging.info("Scratch disconnected")
        cleanup_threads(listeners + sender)
        time.sleep(1)
        cycle_trace = 'start'

    if (cycle_trace == 'start'):
        # open the socket
        logging.info('Connecting to Scratch...')
        the_socket = create_socket(host, PORT)
        logging.info('Connected to Scratch')
        the_socket.settimeout(SOCKET_TIMEOUT)
        sender = ScratchSender(the_socket)
        #listeners = []
        #for device in DEVICES:
          #listeners.append(ArduinoListener(device, ARDUINO_BAUD_RATE, sender, BROADCAST_NAMES, SENSOR_NAMES))
          
        listeners = [ArduinoListener(device, ARDUINO_BAUD_RATE, sender, BROADCAST_NAMES, SENSOR_NAMES) for device in DEVICES]
        cycle_trace = 'running'
        logging.info("Listeners running....")
	sender.start()
	for listener in listeners:
          listener.start()

    # wait for ctrl+c
    try:
        #just pause
        time.sleep(0.1)
    except KeyboardInterrupt:
        logging.warning("Interrrupted")
        cleanup_threads(listeners + [sender])
        sys.exit()

