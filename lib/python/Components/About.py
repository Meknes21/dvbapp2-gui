from Tools.Directories import resolveFilename, SCOPE_SYSETC
from Tools.HardwareInfo import HardwareInfo
from os import path
import sys
import os
import time

def getVersionString():
	return getImageVersionString()

def getImageVersionString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "version":
				version = splitted[1].replace('\n','')
		file.close()
		return version
	except IOError:
		return "unavailable"

def getEnigmaVersionString():
	import enigma
	enigma_version = enigma.getEnigmaVersionString()
	return enigma_version

def getKernelVersionString():
	try:
		f = open("/proc/version","r")
		kernelversion = f.read().split(' ', 4)[2].split('-',2)[0]
		f.close()
		return kernelversion
	except:
		return _("unknown")

def getBuildVersionString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "build":
				version = splitted[1].replace('\n','')
		file.close()
		return version
	except IOError:
		return "unavailable"

def getLastUpdateString():
	try:
		if os.path.isfile('/var/lib/opkg/status'):
			st = os.stat('/var/lib/opkg/status')
		else:
			st = os.stat('/usr/lib/ipkg/status')
		tm = time.localtime(st.st_mtime)
		if tm.tm_year >= 2011:
			return time.strftime("%Y-%m-%d %H:%M:%S", tm)
	except:
		pass
	return _("unavailable")

def getDriversString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "drivers":
				#YYYY MM DD hh mm
				#2005 11 29 01 16
				string = splitted[1].replace('\n','')
				year = string[0:4]
				month = string[4:6]
				day = string[6:8]
				date = '-'.join((year, month, day))
		file.close()
		return date
	except IOError:
		return "unavailable"

def getDriversVersionString():
	try:
		if (os.path.isfile("/proc/stb/info/boxtype") and os.path.isfile("/proc/stb/info/version")):
			  if ((open("/proc/stb/info/chipset").read().strip()) == "bcm7405"):
			    return open("/proc/stb/info/chipset").read().strip().replace("7405", "7413") + "-" + open("/proc/stb/info/version").read().strip()
			  else:
			    return open("/proc/stb/info/chipset").read().strip() + "-" + open("/proc/stb/info/version").read().strip()
	except:
		pass
	return "Unavailable"  

def getHardwareTypeString():                                                    
	try:
		if (os.path.isfile("/proc/stb/info/boxtype") and os.path.isfile("/proc/stb/info/version")): 
			return open("/proc/stb/info/boxtype").read().strip().upper()
		if os.path.isfile("/proc/stb/info/boxtype"):                            
			return open("/proc/stb/info/boxtype").read().strip().upper() + " (" + open("/proc/stb/info/board_revision").read().strip() + "-" + open("/proc/stb/info/version").read().strip() + ")"
		if os.path.isfile("/proc/stb/info/vumodel"):                            
			return "VU+" + open("/proc/stb/info/vumodel").read().strip().upper() + "(" + open("/proc/stb/info/version").read().strip().upper() + ")" 
		if os.path.isfile("/proc/stb/info/model"):                              
			return open("/proc/stb/info/model").read().strip().upper()      
	except:
		pass
	return "Unavailable" 
	
def getImageTypeString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "build_type":
				image_type = splitted[1].replace('\n','') # 0 = release, 1 = experimental
		file.close()
		if image_type == '0':
			image_type = _("Release")
		else:
			image_type = _("Experimental")
		return image_type
	except IOError:
		return "unavailable"

def getImageDistroString():
	try:
		file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
		lines = file.readlines()
		file.close()
		for x in lines:
			splitted = x.split('=')
			if splitted[0] == "comment":
				distro =  splitted[1].replace('\n','')
		return distro
	except IOError:
		return "unavailable"

import socket, fcntl, struct

def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info  = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])

def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr']    = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr']  = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k,v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	return ifreq

def getIfTransferredData(ifname):
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			f.close()
			return (rx_bytes, tx_bytes)

def getChipSetString():
	try:
		f = open('/proc/stb/info/chipset', 'r')
		chipset = f.read()
		f.close()
		return chipset
	except IOError:
		return "unavailable"

# For modules that do "from About import about"
about = sys.modules[__name__]
