import serial.tools.list_ports
from serial import Serial
import sys
import time
import os.path
import struct
ports = serial.tools.list_ports.comports()

def selectCOMPort(custom=None):
    if(custom!=None and len(custom)>0):
        val = custom
    else:
        val = input("\nEnter COM Port of MCU:")
    if any(x[0] == val for x in ports):
        return val
    else:
        return -1

def checkAvailability(no_print=False):
    ser.flushInput()
    ser.flushOutput()
    ser.write(b'ECHO')
    read_val = ser.read(size=4)
    if(not no_print):
        print(read_val)
    w = 'n'
    if(read_val == b"REDY"):
        if(not no_print):
            print("Device Ready!")
        return 1
    else:
        if(not no_print):
            w = input("Device not responding, try again? (y/n)")
    if w == 'y':
        ser.write(b'STOP')
        ser.read(4)
        return checkAvailability()
    else:
        return -1

def sendPrep(offset):
    ser.write(b'WRIT')
    ser.write(b'WRIT'+bin(offset))

def sendData(bdata32,len,timeout):
    if(len > 32):
        len = 32
    ser.write(b'IGNR'+bin(len)+bdata32)
    response = ser.read(size=4)
    print(response)

def readID(timeout):
    ser.write(b'STOP')
    tryf = timeout
    while(tryf != 0):
        if(checkAvailability(no_print=True)):
            ser.write(b'RDID');
            jedec_id = ser.read(4);
            jedec_id = hex(struct.unpack('<i',jedec_id)[0])
            return jedec_id
        else:
            tryf = tryf-1;
            time.sleep(1);
            continue
    return -1;


#main code executes from here

force = False
file = ""
in_port = ""
offset = 0x0;

for argv in sys.argv:
    if argv == '-f':
        force = True
    if "--file=" in argv:
        file = argv.split("=")[1]
        if(len(file)>0 and os.path.isfile(file)):
            print("file validated.")
        else:
            print("Invalid File Path\nPlease specify proper file to flash using --file=<file_path>")
            exit()
    if "--port=" in argv:
        in_port = argv.split("=")[1]
        if(len(in_port)<=0):
            print("Invalid Port, please specify as follows : --port=<port_name>")
            exit()
    if "--offset=" in argv:
        offset = argv.split("=")[1]
        if(len(offset)<=0):
            print("Invalid Offset, please specify proper offset as follows : --offset=<0x300000>")
            exit()
        try:
            offset = int(offset,16)
        except:
            print("Invali Offset Format! Please specify in HEX as follows : --offset=<0x300000>")

if (len(file) == 0 ):
    print("Please specify file to flash using --file=<file_path>")
    exit()

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

try_again = True;
g_port = ""
while try_again:
    if(len(in_port)==0):
        result = selectCOMPort()
    else:
        result = selectCOMPort(in_port)
    if(result == -1):
        x = input("Invalid port, try again (y/n)?")
        if x == 'y' or x == 'Y':
            try_again = True
            in_port=""
        else:
            try_again = False
            exit()
    else:
        try_again = False
        g_port = result
        print(f"Port {g_port} selected")

baud_rate = 9600
ser = Serial(g_port,baud_rate,timeout=5)
rfile = open(file,'r+b')
checkAvailability()
print("\ndevice details:")
print("jedec id    : " +hex(int(readID(5),16)>>16))
print("memory type : " +hex(int(readID(5),16)>>8 & 0xFF))
print("capacity    : " +hex(int(readID(5),16) & 0xFF))
if(not force):
    w = input("\nProceed? Your flash module will be erased!! (y/n)")
    if(not(w == 'y' or w == 'Y')):
        print("exiting...")
        exit()

print("Erasing chip... (This might take 15-30s)")
ser.write(b'ERAS')
ser.timeout = 60
res = ser.read(4)
ser.timeout = 5
if(res != b'PASS'):
    print(f"Erase chip operation failed! w/ response : {res}")
    ser.close()
    exit()
ser.write(b'WRIT')
ser.write(b'WRIT'+int.to_bytes(4,1,'big')+int.to_bytes(offset,4,'big'));
if(ser.read(4) == b'OKAY'):
    off = ser.read(4)
    off = hex(struct.unpack('<i',off)[0])
    print(f"offset {off} successfully written")
else:
    print("offset write error!")
    exit()

lena=1
tlen=0
print("Writing chip...")
ser.timeout = 15
while lena > 0:
    a = rfile.read(32)
    lena = len(a)
    if(lena == 0):
        break
    print(f"{tlen} bytes written, last {lena} bytes: {a}", end='\r')
    ser.write(b'IGNR'+int.to_bytes((lena&0xFF),1,'big')+a)
    result = ser.read(4)
    if(result!=b'PASS'):
        print(f"write failed after {tlen} bytes! Exiting... RESPONSE : {result}")
        ser.close()
        exit()
    tlen = tlen+lena

ser.write(b'STOP')
print("\nWrite completed")
ser.close()
# file.write(binascii.unhexlify(hex(num).rstrip('L').lstrip('0x')))
