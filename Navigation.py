from enigma import eServiceCenter, eServiceReference, eTimer, pNavigation, getBestPlayableServiceReference, iPlayableService
from Components.ParentalControl import parentalControl
from Components.config import config
from Tools.BoundFunction import boundFunction
from Tools.StbHardware import setFPWakeuptime, getFPWakeuptime, getFPWasTimerWakeup
from time import time
import RecordTimer
import PowerTimer
import SleepTimer
import Screens.Standby
import NavigationInstance
import ServiceReference
from Screens.InfoBar import InfoBar, MoviePlayer
from os import path

# TODO: remove pNavgation, eNavigation and rewrite this stuff in python.
class Navigation:
	def __init__(self, nextRecordTimerAfterEventActionAuto=False, nextPowerManagerAfterEventActionAuto=False):
		if NavigationInstance.instance is not None:
			raise NavigationInstance.instance

		NavigationInstance.instance = self
		self.ServiceHandler = eServiceCenter.getInstance()

		import Navigation as Nav
		Nav.navcore = self

		self.pnav = pNavigation()
		self.pnav.m_event.get().append(self.dispatchEvent)
		self.pnav.m_record_event.get().append(self.dispatchRecordEvent)
		self.event = [ ]
		self.record_event = [ ]
		self.currentlyPlayingServiceReference = None
		self.currentlyPlayingService = None
		self.RecordTimer = RecordTimer.RecordTimer()
		self.PowerTimer = PowerTimer.PowerTimer()
		if getFPWasTimerWakeup():
			if nextRecordTimerAfterEventActionAuto:
				# We need to give the system the chance to fully startup,
				# before we initiate the standby command.
				self.standbytimer = eTimer()
				self.standbytimer.callback.append(self.gotostandby)
				self.standbytimer.start(15000, True)
				# We need to give the systemclock the chance to sync with the transponder time,
				# before we will make the decision about whether or not we need to shutdown
				# after the upcoming recording has completed
				self.recordshutdowntimer = eTimer()
				self.recordshutdowntimer.callback.append(self.checkShutdownAfterRecording)
				self.recordshutdowntimer.start(30000, True)
			elif nextPowerManagerAfterEventActionAuto:
				# We need to give the system the chance to fully startup,
				# before we initiate the standby command.
				self.standbytimer = eTimer()
				self.standbytimer.callback.append(self.gotostandby)
				self.standbytimer.start(15000, True)
# 		self.SleepTimer = SleepTimer.SleepTimer()

	def gotostandby(self):
		from Tools import Notifications
		Notifications.AddNotification(Screens.Standby.Standby)

	def checkShutdownAfterRecording(self):
		if len(self.getRecordings()) or abs(self.RecordTimer.getNextRecordingTime() - time()) <= 360:
			if not Screens.Standby.inTryQuitMainloop: # not a shutdown messagebox is open
				RecordTimer.RecordTimerEntry.TryQuitMainloop(False) # start shutdown handling

	def checkShutdownAfterPowerManager(self):
		if abs(self.PowerTimer.getNextPowerManagerTime() - time()) <= 360:
			if not Screens.Standby.inTryQuitMainloop: # not a shutdown messagebox is open
				PowerTimer.PowerTimerEntry.TryQuitMainloop(False) # start shutdown handling

	def dispatchEvent(self, i):
		for x in self.event:
			x(i)
		if i == iPlayableService.evEnd:
			self.currentlyPlayingServiceReference = None
			self.currentlyPlayingService = None

	def dispatchRecordEvent(self, rec_service, event):
#		print "record_event", rec_service, event
		for x in self.record_event:
			x(rec_service, event)

	def playService(self, ref, checkParentalControl = True, forceRestart = False):
		oldref = self.currentlyPlayingServiceReference
		if ref and oldref and ref == oldref and not forceRestart:
			print "ignore request to play already running service(1)"
			return 0
		print "playing", ref and ref.toString()
		if path.exists("/proc/stb/lcd/symbol_signal") and config.lcd.mode.getValue() == '1':
			try:
				if ref.toString().find('0:0:0:0:0:0:0:0:0') == -1:
					signal = 1
				else:
					signal = 0
				open("/proc/stb/lcd/symbol_signal", "w").write(str(signal))
			except:
				open("/proc/stb/lcd/symbol_signal", "w").write("0")
		elif path.exists("/proc/stb/lcd/symbol_signal") and config.lcd.mode.getValue() == '0':
			open("/proc/stb/lcd/symbol_signal", "w").write("0")

		if ref is None:
			self.stopService()
			return 0
		if not checkParentalControl or parentalControl.isServicePlayable(ref, boundFunction(self.playService, checkParentalControl = False)):
			if ref.flags & eServiceReference.isGroup:
				if not oldref:
					oldref = eServiceReference()
				playref = getBestPlayableServiceReference(ref, oldref)
				print "playref", playref
				if playref and oldref and playref == oldref and not forceRestart:
					print "ignore request to play already running service(2)"
					return 0
				if not playref or (checkParentalControl and not parentalControl.isServicePlayable(playref, boundFunction(self.playService, checkParentalControl = False))):
					self.stopService()
					return 0
			else:
				playref = ref
			if self.pnav:
				self.pnav.stopService()
				self.currentlyPlayingServiceReference = playref
				self.currentlyPlayingSelectedServiceReference = ref
				InfoBarInstance = InfoBar.instance
				if InfoBarInstance is not None:
					InfoBarInstance.servicelist.servicelist.setCurrent(ref)
				if self.pnav.playService(playref):
					print "Failed to start", playref
					self.currentlyPlayingServiceReference = None
				return 0
		else:
			self.stopService()
		return 1

	def getCurrentlyPlayingServiceReference(self, selected = True):
		if selected and self.currentlyPlayingServiceReference:
			return self.currentlyPlayingSelectedServiceReference
		return self.currentlyPlayingServiceReference

	def isMovieplayerActive(self):
		MoviePlayerInstance = MoviePlayer.instance
		if MoviePlayerInstance is not None and self.currentlyPlayingServiceReference.toString().find('0:0:0:0:0:0:0:0:0') != -1:
			from Screens.InfoBarGenerics import setResumePoint
			setResumePoint(MoviePlayer.instance.session)
			MoviePlayerInstance.close()

	def recordService(self, ref, simulate=False):
		service = None
		if not simulate: print "recording service: %s" % (str(ref))
		if isinstance(ref, ServiceReference.ServiceReference):
			ref = ref.ref
		if ref:
			if ref.flags & eServiceReference.isGroup:
				ref = getBestPlayableServiceReference(ref, eServiceReference(), simulate)
			service = ref and self.pnav and self.pnav.recordService(ref, simulate)
			if service is None:
				print "record returned non-zero"
		return service

	def stopRecordService(self, service):
		ret = self.pnav and self.pnav.stopRecordService(service)
		return ret

	def getRecordings(self, simulate=False):
		return self.pnav and self.pnav.getRecordings(simulate)

	def getCurrentService(self):
		if not self.currentlyPlayingService:
			self.currentlyPlayingService = self.pnav and self.pnav.getCurrentService()
		return self.currentlyPlayingService

	def stopService(self):
		if self.pnav:
			self.pnav.stopService()
		self.currentlyPlayingServiceReference = None
		if path.exists("/proc/stb/lcd/symbol_signal"):
			open("/proc/stb/lcd/symbol_signal", "w").write("0")

	def pause(self, p):
		return self.pnav and self.pnav.pause(p)

	def shutdown(self):
		self.RecordTimer.shutdown()
		self.ServiceHandler = None
		self.pnav = None

	def stopUserServices(self):
		self.stopService()
