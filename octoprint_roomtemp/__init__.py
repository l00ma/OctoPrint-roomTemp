# coding=utf-8

from __future__ import absolute_import

__author__ = "Frederic MOUTIN <looma@protonmail.ch>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2017 Frederic MOUTIN - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import re
import glob
import os

class RoomTempPlugin(octoprint.plugin.StartupPlugin,
					 octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.AssetPlugin,
					 octoprint.plugin.SettingsPlugin):

	def __init__(self):
		self.isRaspi = False
		self.displayRoomTemp = True
		self._checkTempTimer = None

	def on_after_startup(self):
		self.displayRoomTemp = self._settings.get(["displayRoomTemp"])

		if sys.platform == "linux2":
			with open('/proc/cpuinfo', 'r') as infile:
				cpuinfo = infile.read()
			# Match a line like 'Hardware   : BCM2709'
			match = re.search('^Hardware\s+:\s+(\w+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

			if match.group(1) == 'BCM2708' or match.group(1) == 'BCM2709' or match.group(1) == 'BCM2835':
				self.isRaspi = True
			else:
				self.isRaspi = False

			if self.isRaspi and self.displayRoomTemp:
				self.startTimer(30.0)
			
		if self.isRaspi == False:
			self._logger.info("This is not a Raspberry Pi - Plugin halted")
			sys.exit(1)

	def startTimer(self, interval):
		self._checkTempTimer = RepeatedTimer(interval, self.checkRoomTemp, None, None, True)
		self._checkTempTimer.start()

	def checkRoomTemp(self):
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')[0]
		device_file = device_folder + '/w1_slave'
		if os.path.isfile(device_file):
			lines = read_temp_raw(device_file)
			while lines[0].strip()[-3:] != 'YES':
				time.sleep(0.2)
				lines = read_temp_raw(device_file)
			equals_pos = lines[1].find('t=')
			if equals_pos != -1:
				temp_string = lines[1][equals_pos+2:]
				temp_c = float(temp_string) / 1000.0
				p = '{0:0.1f}'.format(temp_c)

			self._plugin_manager.send_plugin_message(self._identifier, dict(israspi=self.isRaspi, roomtemp=p))
		else:
			self._logger.info("No file temperature found !!")

	##~~ SettingsPlugin
	def get_settings_defaults(self):
		return dict(displayRoomTemp = self.displayRoomTemp)

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		self.displayRoomTemp = self._settings.get(["displayRoomTemp"])

		if self.displayRoomTemp:
			interval = 30.0
			self.startTimer(interval)
		else:
			if self._checkTempTimer is not None:
				try:
					self._checkTempTimer.cancel()
				except:
					pass
			self._plugin_manager.send_plugin_message(self._identifier, dict())

	##~~ TemplatePlugin API
	def get_template_configs(self):
		if self.isRaspi:
			return [
				dict(type="settings", template="roomtemp_settings_raspi.jinja2")
			]
		else:
			return []

	##~~ AssetPlugin API
	def get_assets(self):
		return {
			"js": ["js/roomtemp.js"],
			"css": ["css/roomtemp.css"],
			"less": ["less/roomtemp.less"]
		} 

	##~~ Softwareupdate hook
	def get_update_information(self):
		return dict(
			roomtemp=dict(
				displayName="Room Temperature Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="looma",
				repo="OctoPrint-roomTemp",
				current=self._plugin_version,

				# update method: pip w/ dependency links
				pip="https://github.com/looma/OctoPrint-roomTemp/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "Room Temperature Plugin"


def read_temp_raw(device_file):
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = RoomTempPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
