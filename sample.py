#!/usr/bin/python

from __future__ import print_function

from ZeoRawData.BaseLink import BaseLink
from ZeoRawData.Parser import Parser
from onkyo import Receiver

import math
import time
import urllib2

port = '/dev/ttyUSB0'
param = 'SleepStage'

bins = ['11-14', '2-4', '4-8', '8-13', '13-18', '18-21', '30-50']


class Act:
	gammaThreshold = 0.002

	def __init__(self):
		self.reset(True)

	def onSlice(self, slice):
		if not self.sampling:
			return
		if not slice['BadSignal']:
			if slice['FrequencyBins']['30-50'] < self.gammaThreshold:
				self.awakeSeconds = 0
				self.asleepSeconds += 1
			else:
				self.awakeSeconds += 1
				self.asleepSeconds = 0
		if self.asleepSeconds > 30:
			self.sleptSeconds += 1
		if self.awakeSeconds > 120 and self.sleptSeconds > 6 * 3600:
			self.wakeUp()

	def onEvent(self, logtime, version, event):
		if event == 'HeadbandUndocked':
			self.reset(True)
		if event == 'HeadbandDocked':
			# TODO(dichro): reset
			self.reset(False)
	
	def reset(self, sampling):
		self.sampling = sampling
		self.awakeSeconds = 0
		self.sleepingSeconds = 0
		self.sleptSeconds = 0
	
	def wakeUp(self):
		'''Turns on lights and plays music.'''
		print(time.ctime(), 'waking up after', self.sleptSeconds,
			'sleep; awake for', self.awakeSeconds)
		urllib2.urlopen('http://localhost:10443/wakeUp')
		Receiver().start()


class Log:
	def __init__(self, filebase):
		self.file = open(filebase + time.strftime('_%Y%m%d-%H%M%S.log'), 'w')

	def onSlice(self, slice):
		print(time.ctime(), slice, file=self.file)

	def onEvent(self, logtime, version, event):
		print(time.ctime(), event, file=self.file)


if __name__ == '__main__':
	parser = Parser()

	log = Log('/tmp/zeo')
	parser.addSliceCallback(log.onSlice)
	parser.addEventCallback(log.onEvent)

	act = Act()
	parser.addSliceCallback(act.onSlice)
	parser.addEventCallback(act.onEvent)

	link = BaseLink(port)
	link.addCallback(parser.update)
	link.start()

	while(True):
		time.sleep(60)
