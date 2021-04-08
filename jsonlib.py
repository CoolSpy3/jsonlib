import json
import threading
import os

files = {}
locks = {}
openLocks = {}

def checkExists(alias):
	if alias not in files:
		raise ValueError('No json file is registered with alias: "' + alias + '"')

def registerFile(file, alias):
	try:
		checkExists(alias)
		if files[alias] != file:
			raise ValueError('"' + alias + '" already exists and is mapped to file: "' + files[alias] + '"');
	except ValueError:
		pass
	files[alias] = file
	locks[alias] = threading.Lock()

def closeFile(alias):
	checkExists(alias)
	locks[alias].acquire()
	try:
		checkExists(alias)
		files.pop(alias, None)
		locks.pop(alias, None)
	finally:
		locks[alias].release()

def open(alias):
	checkExists(alias)
	locks[alias].acquire()
	try:
		file = open(files[alias], "r")
	    data = json.load(file)
	    file.close()
	    openLocks[data] = alias
	    return data
    except Exception as e:
		locks[alias].release()
		raise e

def release(data, save=False):
	if data not in openLocks:
		raise ValueError("The provided dictionary does not match any open locks")
	alias = openLocks[data]
	checkExists(alias)
	try:
		if save:
			os.remove(files[data])
	        file = open(files[alias], "w")
	        file.write(json.dumps(data, indent = 4))
	        file.close()
    except Exception as e:
		locks[alias].release()
		raise e