#!/usr/bin/python

from ZeoRawData.BaseLink import BaseLink
from ZeoRawData.Parser import Parser

import time

port = '/dev/ttyUSB0'
param = 'SleepStage'

class callback:
	lastParam = ''

	def onSlice(self, slice):
		if slice[param] == self.lastParam:
			return
		self.lastParam = slice[param]
		print time.ctime(), self.lastParam

	def onEvent(self, logtime, version, event):
		print time.ctime(), event

cb = callback()

parser = Parser()
parser.addSliceCallback(cb.onSlice)
parser.addEventCallback(cb.onEvent)

link = BaseLink(port)
link.addCallback(parser.update)
link.start()

while(True):
	time.sleep(60)
