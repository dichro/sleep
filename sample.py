#!/usr/bin/python

from __future__ import print_function

from ZeoRawData.BaseLink import BaseLink
from ZeoRawData.Parser import Parser

import time

port = '/dev/ttyUSB0'
param = 'SleepStage'

bins = ['11-14', '2-4', '4-8', '8-13', '13-18', '18-21', '30-50']

class Act:
	tracking = True

	def onSlice(self, slice):
		if not self.tracking:
			return
		try:
			gamma = slice['FrequencyBins']['30-50']
		except KeyError, e:
			print(e, slice)
		print(gamma)

	def onEvent(self, logtime, version, event):
		if event == 'HeadbandUndocked':
			self.tracking = True
		if event == 'HeadbandDocked':
			# TODO(dichro): reset
			self.tracking = False


class Log:
	def __init__(self, filebase):
		self.file = open(filebase + time.strftime('_%Y%m%d-%H%M%S.log'), 'w')

	def onSlice(self, slice):
		print(time.ctime(), slice, file=self.file)

	def onEvent(self, logtime, version, event):
		print(time.ctime(), event, file=self.file)


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
