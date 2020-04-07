#!/usr/bin/env python3
import sqlite3

def prepare_db(path):
	con = sqlite3.connect(path)
	c = con.cursor()

	c.execute('''CREATE TABLE IF NOT EXISTS 
	infections (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		uuid BLOB NOT NULL UNIQUE ON CONFLICT IGNORE
	)''')
	c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uuid ON infections (uuid)''')
	c.close()
	return con

def _convert_to_uuid_bytes(uuid):
	if type(uuid) == str:
		return uuid.encode("UTF-8")
	if type(uuid) == bytes:
		return uuid
	raise ValueError("Invalid uuid type")

def insert_into_db(con, uuids):
	"""
	:param uuids: 16-byte bytes objects
	"""

	# filter out all uuids with the improper length and convert them to tuples
	uuids = ((_convert_to_uuid_bytes(uuid),) for uuid in uuids if len(uuid) == 16)
	c = con.cursor()
	c.executemany('''INSERT OR IGNORE INTO infections(uuid) VALUES (?)''', uuids)
	con.commit()

#def query_all():
#	c = con.cursor()
#	c.execute('''SELECT uuid FROM infections''')
#	return c

def query_subsequent(con, uuid):
	c = con.cursor()
	c.execute('''SELECT uuid FROM infections WHERE id > (SELECT IFNULL((SELECT id FROM infections WHERE uuid = ?), 0))''', (uuid,))
	return (_convert_to_uuid_bytes(row[0]) for row in c)

#def get_id(uuid):
#	c = con.cursor()
#	c.execute('''SELECT IFNULL((SELECT id FROM infections WHERE uuid = ?), 0)''', (uuid,))
#	return c.fetchone()[0]
