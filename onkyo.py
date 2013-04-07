import eiscp
import time

class Receiver:
	receiver = None

	def __init__(self):
		for receiver in eiscp.eISCP.discover(timeout=4):
			self.receiver = receiver
			break

	def do(self, cmd):
		try:
			print self.receiver.raw(cmd)
		except ValueError, v:
			pass

	def start(self):
		'''Powers up receiver and plays Spotify. Blocks for minutes gradually
		bringing volume up.'''
		self.do('PWR01') # power on
		time.sleep(5)
		self.do('MVL01') # volume 1
		self.do('SLI2B') # input net
		self.do('NSV0A0') # spotify
		self.do('NSTPRS')
		# it appears to be impossible to retrieve the names of playlists
		# or the name of the thing that the cursor is pointing to,
		# although the cursor *position* is available. O_o So just start
		# playing and hope for the best.
		for i in xrange(2, 40):
			self.do('MVL%02X' % i)
			time.sleep(5)
