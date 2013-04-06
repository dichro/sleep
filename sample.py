#!/usr/bin/python

from __future__ import print_function

from ZeoRawData.BaseLink import BaseLink
from ZeoRawData.Parser import Parser

import time

port = '/dev/ttyUSB0'
param = 'SleepStage'

bins = ['11-14', '2-4', '4-8', '8-13', '13-18', '18-21', '30-50']
class callback:
	accumulator = {}

	def onSlice(self, slice):
		for bin in bins:
			self.accumulator[bin] = self.accumulator.get(bin, 0) + slice['FrequencyBins'].get(bin, 0)
		if slice['SleepStage'] is None:
			return
		print(time.ctime(), slice['BadSignal'], slice['SleepStage'], slice['SQI'], slice['Impedance'],
		       [self.accumulator.get(x, 0) for x in bins])
		self.accumulator = {}

	def onEvent(self, logtime, version, event):
		print(time.ctime(), event)

cb = callback()

parser = Parser()
parser.addSliceCallback(cb.onSlice)
parser.addEventCallback(cb.onEvent)

link = BaseLink(port)
link.addCallback(parser.update)
link.start()

while(True):
	time.sleep(60)
