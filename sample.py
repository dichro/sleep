#!/usr/bin/python

from __future__ import print_function

from ZeoRawData.BaseLink import BaseLink
from ZeoRawData.Parser import Parser

import math
import time

port = '/dev/ttyUSB0'
param = 'SleepStage'

bins = ['11-14', '2-4', '4-8', '8-13', '13-18', '18-21', '30-50']

class Estimator:
	'''Normal estimator, completely wrong: should be bimodal Poisson.'''
	count = 0
	sum = 0.0
	sumsq = 0.0
	
	def mean(self):
		return self.sum / self.count
	
	def sigma(self):
		mean = self.mean()
		variance = (self.sumsq - 2*mean*self.sum + self.count*mean*mean)/(self.count - 1)
		return math.sqrt(variance)

	def p(self, value):
		try:
			return (value - self.mean()) / self.sigma()
		except ZeroDivisionError, e:
			return None

	def add(self, value):
		p = self.p(value)
		self.count += 1
		self.sum += value
		self.sumsq += value*value
		return p


class Act:
	estimator = Estimator()

	def onSlice(self, slice):
		if self.estimator is None:
			return
		try:
			gamma = slice['FrequencyBins']['30-50']
			p = self.estimator.add(gamma)
			print(gamma, p)
		except KeyError, e:
			print(e, slice)

	def onEvent(self, logtime, version, event):
		if event == 'HeadbandUndocked':
			self.estimator = Estimator()
		if event == 'HeadbandDocked':
			# TODO(dichro): reset
			self.estimator = None


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
