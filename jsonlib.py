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

def _do_open_json(alias: str) -> dict[any, any]:
	checkExists(alias)
	locks[alias].acquire()
	try:
		file = open(files[alias], "r")
		data = json.load(file)
		file.close()
		openLocks[alias] = data
		return data
	except Exception as e:
		locks[alias].release()
		raise e

def save(data: dict[any, any]) -> None:
	alias = None
	for tmp in openLocks:
		if openLocks[tmp] is data:
			alias = tmp
	if alias == None:
		raise ValueError("The provided dictionary does not match any open locks")
	checkExists(alias)
	os.remove(files[alias])
	file = open(files[alias], "w")
	file.write(json.dumps(data, indent = 4))
	file.close()


def release(data: dict[any, any]) -> None:
	alias = None
	for tmp in openLocks:
		if openLocks[tmp] is data:
			alias = tmp
	if alias == None:
		raise ValueError("The provided dictionary does not match any open locks")
	checkExists(alias)
	locks[alias].release()

class open_json:
	def __init__(self, *args):
		self.args = args

	def __enter__(self):
		self.result = self(*self.args)
		return self.result

	def __call__(self, *args):
		return _do_open_json(*args)

	def __exit__(self, type, value, traceback):
		try:
			release(self.result)
		except RuntimeError:
			pass
