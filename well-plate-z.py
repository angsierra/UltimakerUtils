#!/usr/bin/python

import re
import sys

'''
Usage: well-plate-z.py {z_height} < old.gcode > new.gcode

Example: Usage: well-plate-z.py 100 < old.gcode > new.gcode

Raises nozzle to z_height between printing each of several objects.
Assumes gcode was generated by Cura 14.06.X, using "Tools|Print one at
a time".

Background discussion at:
http://umforum.ultimaker.com/index.php?/topic/6332-how-do-you-print-multiple-objects-and-change-z-height-between-moves/

NO WARRANTY, USE AT YOUR OWN RISK -- this might not work at all, and
could break your machine.  Test carefully, with one finger on the
power switch.


'''


'''
Each new object start looks like this:

	...
	G92 E0
	G10
	G0 F9000 ... Z11.50
	G0 X110.50 Y139.00
	;Layer count: 39
	;LAYER:0
	G0 X106.67 Y135.05 Z0.20
	...

We want it to look like this:

	...
	G92 E0
	G10
	G0 F9000 ... Z11.50
	G0 Z{z_height}
	G0 X110.50 Y139.00
	;Layer count: 39
	;LAYER:0
	G0 X106.67 Y135.05 
	G0 X106.67 Y135.05 Z0.20
	...


'''

z_height = float(sys.argv[1])

state = 'init'
part = 1
for line in sys.stdin:
	line = line.rstrip()
	if state == 'init':
		# G0 F9000 X106.81 Y103.91 Z0.20
		# G0 X106.67 Y135.05 Z0.20
		m = re.match('^(G0.+)Z\S+$', line)
		if m:
			print "G0 Z%f" % z_height
			print "%s" % (m.group(1))
			state = 'pass'
			print "; part=%d, state=%s" % (part, state)
	elif state == 'pass':
		if line == "G10":
			part += 1
			state = 'before_layer'
			print "; part=%d, state=%s" % (part, state)
	elif state == 'before_layer':
		# G0 X74.90 Y105.38
		m = re.match('^(G0\s*X\S+\s*Y\S+)$', line)
		if m:
			print "G0 Z%f" % z_height
			state = 'init'
			print "; part=%d, state=%s" % (part, state)
		elif line.startswith("M25"):
			print "G0 Z%f" % z_height
			state = 'end'
			print "; part=%d, state=%s" % (part, state)
	print line

