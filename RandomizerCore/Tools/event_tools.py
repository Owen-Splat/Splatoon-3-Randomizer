from io import BytesIO
import evfl
import tempfile


def invertList(l):
	"""Converts a list into a dict of {value: index} pairs"""
	return {l[i]: i for i in range(len(l))}


def readFlow(data):
	"""Reads the flow from the eventflow data and returns it"""
	
	flow = evfl.EventFlow()
	flow.read(bytes(data))

	return flow


def writeFlow(flow):
	"""returns the given flow as bytes"""
	
	with BytesIO() as f:
		flow.write(f)
		f.seek(0)
		data = f.read()
	
	return data


def findEvent(flowchart, name):
	"""Finds and returns an event from a flowchart given a name as a string. Returns None if not found"""

	if name == None:
		return

	for event in flowchart.events:
		if event.name == name:
			return event

	return None


def findEntryPoint(flowchart, name):
	"""Finds and returns an entry point from a flowchart given a name as a string. Returns None if not found"""

	if name == None:
		return

	for ep in flowchart.entry_points:
		if ep.name == name:
			return ep

	return None


def insertEventAfter(flowchart, previous, new):
	"""Change the previous event or entry point to have {new} be the next event 
	{previous} is the name of the event/entry point, {new} is the name of the event to add 
	Return True if any event or entry point was modified and False if not"""

	newEvent = findEvent(flowchart, new)

	prevEvent = findEvent(flowchart, previous)
	if prevEvent:
		prevEvent.data.nxt.v = newEvent
		prevEvent.data.nxt.set_index(invertList(flowchart.events))

		return True

	entry_point = findEntryPoint(flowchart, previous)
	if entry_point:
		entry_point.main_event.v = newEvent
		entry_point.main_event.set_index(invertList(flowchart.events))
		return True

	return False
