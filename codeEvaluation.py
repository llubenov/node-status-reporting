import sys, fileinput, datetime
from itertools import tee, chain

class NotificationLine:
	"""
		This class represents how each line from the input files is going to be constructed.
	"""
	def __init__(self, monitorReceivedTimestamp=0, nodeGeneratedTimestamp=0, nodeNotificator= "", message="", notificatedCharacter=""):
		self.monitorReceivedTimestamp = monitorReceivedTimestamp
		self.nodeGeneratedTimestamp = nodeGeneratedTimestamp
		self.nodeNotificator = nodeNotificator
		self.message = message
		self.notificatedCharacter = notificatedCharacter

# Generate a new status based on the message.
def generateStatus(status):
	if status != None:
		if str(status) == "FOUND" or str(status) == "HELLO":
			return "ALIVE"
		elif str(status) == "LOST":
			return "DEAD"
		else:
			return "UNKNOWN"

# A check to see if the first two inputs from each line represent timestamps.
def checkTimestamps(receivedTimestamp, generatedTimestamp):
	try:
		if len(str(generatedTimestamp)) == 13 and len(str(receivedTimestamp)) == 13:
			return True
	except ValueError:
		return False

# The generateAllObjects is used to generate an object for every line 
# that is later going to be processed.
def generateAllObjects(allLines):
	allNotificationLines = []
	for lineNum, line in enumerate(allLines,1):
		split_line = line.split()
		# If the line contains the appropriate amount of parameters.
		if len(split_line) <= 5 and len(split_line) > 1:
			monitorReceivedTimestamp = split_line[0]
			nodeGeneratedTimestamp = split_line[1]
			# Check if the two timestamps are correct.
			if checkTimestamps(monitorReceivedTimestamp, nodeGeneratedTimestamp):
				# Create a new object for each line.
				allNotificationLines.append(NotificationLine(*split_line))
			else: 
				print("Incorrect timestamp at %s." % lineNum)
				sys.exit(1)
		else:
			print("Error occured on line %s." % lineNum)
			sys.exit(1)

	return allNotificationLines

# The createEntry function creates the new characters with their status.
def createEntry(character, status):
	generatedCharacter = {
		'monitorTimestamp' : character.monitorReceivedTimestamp,
		'notificator' : character.nodeNotificator,
		'status' : status,
		'notificatedCharacter' : character.notificatedCharacter,
		'message' : character.message,
		'nodeGeneratedTimestamp' : character.nodeGeneratedTimestamp
	}

	return generatedCharacter

# The generateOutput function is used to generate and display the required output in the console.
def generateOutput(character):
	for prop in character.items():
		if prop[1]["status"] != "UNKNOWN":
			print(prop[0] + " " + prop[1]["status"] + " " + prop[1]["monitorTimestamp"] + " " + prop[1]["notificator"] + " " + prop[1]["message"] + " " + prop[1]["notificatedCharacter"])
		else:
			print(prop[1]["status"])

# The checkCurrentAndPrevious function is used to return tuples of previous and current notification lines.
def checkCurrentAndPrevious(currentObject):
	# Create 2 independent iterators over the sequence.
    previous, current = tee(currentObject, 2)
    previous = chain([None], previous)

    return zip(previous, current)

# The processFile function sets the notificator and notificated characters with their 
# corresponding values by reading the file from top to bottom.
# It looks to see if the examined line has a later timestamp than the previous one and if it does not
# it sets the previous one to "UNKNOWN".
def processFile(allTextLines):
	allCharacters = {}
	allObjects = generateAllObjects(allTextLines)
	allowedMessages = ["LOST", "FOUND"]
	lastTimestampRecorded = None

	for previous, obj in checkCurrentAndPrevious(allObjects):
		if previous != None and len(allObjects) > 1:
		# Check if the current timestamp, which the monitor has received is bigger than the previous one
			if previous.monitorReceivedTimestamp < obj.monitorReceivedTimestamp:
				# Notificator always set to ALIVE. 
				allCharacters[obj.nodeNotificator] = createEntry(obj, generateStatus(obj.message))

				# Check for "lost" and "found" messages.
				if obj.message in allowedMessages:
					allCharacters[obj.notificatedCharacter] = createEntry(obj, generateStatus(obj.message))

			# Set the notificator that has a later timestamp than the next one 
			# and if there is a notificated character to unknown, while creating the current object. 
			else:
				allCharacters[previous.nodeNotificator] = createEntry(previous, "UNKNOWN")
				allCharacters[obj.nodeNotificator] = createEntry(obj, generateStatus(obj.message))
				if previous.notificatedCharacter != "":
					allCharacters[previous.notificatedCharacter] = createEntry(previous, "UNKNOWN")
				elif obj.notificatedCharacter != "":
					allCharacters[obj.notificatedCharacter] = createEntry(obj, generateStatus(obj.message))

		# If there is just one notification line.
		else:
			allCharacters[obj.nodeNotificator] = createEntry(obj, generateStatus(obj.message))

	generateOutput(allCharacters)


# The main function will look at the different arguments that are passed 
# from the command line and will process the files one after another. 
def main(argv):	
	if len(argv) > 1:
		for file in argv[1:]:
			try:
				allLines = open(file).readlines()
				if len(allLines) == 0:
					print("File is empty.")
				processFile(allLines)

			except FileNotFoundError:
				print("File %s does not exist." % file)

	else:
		print("Error: Please ensure that you have entered at least 1 argument" + "\n"
			"Example: python <python file name .py> <filename .txt>")
		sys.exit(1)

if __name__ == "__main__":
	main(sys.argv)
