#!/user/bin/env python

import sys
import time
import RPi.GPIO as io
import subprocess
import logging

THRESHOLD_FILTER = 4
THRESHOLD_ON = 4
THRESHOLD_OFF = 180
PIR_PIN = 17

io.setmode(io.BCM)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y.%d.%m_%H:%M:%S',level=logging.INFO,filename='/var/log/pir_monitor.log')
#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y.%d.%m_%H:%M:%S',level=logging.DEBUG,filename='/var/log/pir_monitor.log')
#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y.%d.%m_%H:%M:%S',level=logging.DEBUG,stream=sys.stdout)


def main():

	io.setup(PIR_PIN, io.IN, pull_up_down = io.PUD_DOWN)

	current_time = time.time()
	last_change = current_time
	last_status = io.input(PIR_PIN)
	last_threshold_change = current_time
	last_threshold_status = 1
	last_monitor_change = current_time
	last_monitor_status = 1

	logging.debug('starting pir monitor script')
	logging.debug('pir was {} for 0 seconds'.format(last_status))

	while True:
		current_time = time.time()
		status = io.input(PIR_PIN)

		if last_status != status:
			duration = current_time - last_change
			logging.debug('pir was {} for {:.2f} seconds'.format(last_status,duration))
			last_status = status
			last_change = current_time
		if ((last_threshold_status != last_status) and ((current_time - last_change) > THRESHOLD_FILTER)):
			duration = current_time - last_threshold_change
			logging.debug('filtered pir was {} for {:.2f} seconds'.format(last_threshold_status,duration))
			last_threshold_status = last_status
			last_threshold_change = last_change
		if ((last_threshold_status != last_monitor_status) and ((last_monitor_status == 0 and (current_time - last_threshold_change) > THRESHOLD_ON) or (last_monitor_status == 1 and (current_time - last_threshold_change) > THRESHOLD_OFF))):
			last_monitor_status = last_threshold_status
			subprocess.call('vcgencmd display_power {}'.format(last_monitor_status),shell=True)
			logging.info('switching monitor to {} after {:.2f} seconds'.format(last_monitor_status,current_time - last_monitor_change))
			last_monitor_change = current_time
		time.sleep(.25)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		io.cleanup()
