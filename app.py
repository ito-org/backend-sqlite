#!/usr/bin/env python3
from flask import Flask, Response, request, g
import binascii
import db

app = Flask(__name__)

DATABASE = 'temp.db'

def get_db_connection():
	con = getattr(g, '_con', None)
	if con is None:
		con = g._database = db.prepare_db(DATABASE)
	return con

@app.teardown_appcontext
def close_connection(exception):
	con = getattr(g, '_con', None)
	if con is not None:
		con.close()


@app.route('/post_uuids', methods=["POST"])
def post_uuids():
	UUID_LENGTH = 16
	print(request.content_type)
	assert request.content_type == 'application/octet-stream'
	data = request.get_data()
	assert len(data) % UUID_LENGTH == 0

	uuids = (data[i:i + UUID_LENGTH] for i in range(0, len(data), UUID_LENGTH))
	db.insert_into_db(get_db_connection(), uuids)

	return ""


@app.route('/get_uuids', methods=["GET"])
def get_uuids():
	# TODO handle invalid uuid length 
	request_uuid = request.args.get('uuid', '')
	request_uuid = binascii.unhexlify(request_uuid)
	
	data = db.query_subsequent(get_db_connection(), request_uuid)
	
	if request.accept_mimetypes['application/json']:
		def generator():
			yield "["
			first_uuid = next(data)
			if first_uuid:
				yield '"{}"'.format(first_uuid.hex())
				for uuid in data:
					yield ', "{}"'.format(uuid.hex())
			yield "]"
		return Response(generator(), mimetype="application/json")
	if request.accept_mimetypes['application/octet-stream']:
		return Response((uuid for uuid in data), mimetype="application/octet-stream")