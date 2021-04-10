import contextlib
import json
import os
import threading
import typing

files = {}
locks = {}
openLocks = {}

def checkExists(alias: str) -> None:
	if alias not in files:
		raise ValueError('No json file is registered with alias: "' + alias + '"')

def registerFile(file: str, alias: str) -> None:
	try:
		checkExists(alias)
		if files[alias] != file:
			raise ValueError('"' + alias + '" already exists and is mapped to file: "' + files[alias] + '"');
	except ValueError:
		pass
	files[alias] = file
	locks[alias] = threading.Lock()

def closeFile(alias: str) -> None:
	checkExists(alias)
	locks[alias].acquire()
	try:
		checkExists(alias)
		files.pop(alias, None)
		locks.pop(alias, None)
	finally:
		locks[alias].release()

def open(alias: str) -> dict[any, any]:
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

def save(data: dict[any, any]) -> None:
	if data not in openLocks:
		raise ValueError("The provided dictionary does not match any open locks")
	alias = openLocks[data]
	checkExists(alias)
	os.remove(files[data])
	file = open(files[alias], "w")
	file.write(json.dumps(data, indent = 4))
	file.close()


def release(data: dict[any, any]) -> None:
	if data not in openLocks:
		raise ValueError("The provided dictionary does not match any open locks")
	alias = openLocks[data]
	checkExists(alias)
	locks[alias].release()

@contextlib.contextmanager
def open_json(alias: str) -> typing.ContextManager[dict[any, any]]:
	data = open(alias)
	try:
		yield data
	finally:
		release(data)
