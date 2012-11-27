from enigma import eDVBResourceManager
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN
from Tools.HardwareInfo import HardwareInfo
from os import path

SystemInfo = { }

#FIXMEE...
def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d"%(idx), 'f'):
		idx += 1
	return idx

SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds

SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["FrontpanelDisplayGrayscale"] = fileExists("/dev/dbox/oled0")
SystemInfo["OledDisplay"] = fileExists(resolveFilename(SCOPE_SKIN, 'skin_display220_picon.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'skin_display220_no_picon.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'skin_display255_picon.xml')) or fileExists(resolveFilename(SCOPE_SKIN, 'skin_display255_no_picon.xml'))
SystemInfo["DeepstandbySupport"] = HardwareInfo().get_device_name() != "dm800"
SystemInfo["HDMICEC"] = (path.exists("/dev/hdmi_cec") or path.exists("/dev/misc/hdmi_cec0")) and fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo")
SystemInfo["SABSetup"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/SABnzbd/plugin.pyo")
