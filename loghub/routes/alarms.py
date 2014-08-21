from flask import request, jsonify, abort
from loghub import app
from loghub.modules import alarms
from loghub.routes.responses import *

def jsonize_request():
	datatype = request.headers.get("Content-Type", None)
	if not datatype:
		abort(404)
	elif datatype == "application/x-www-form-urlencoded":
		data = dict(request.form)
		for each in data.keys():
			data[each] = data[each][0]
	elif datatype == "application/json":
		data = dict(request.json)
	else:
		return abort(400)
	return data


@app.route('/API/v1/alarms', methods = ['POST'])
def register_alarm():
	credential_line = request.headers.get("X-Authorization", None)
	if not credential_line:
		return jsonify(users_responses[35])
	try:
		credential_id = credential_line.split()[1]
	except:
		abort(400)
	alarm = jsonize_request()
	
	module_response = alarms.register_alarm.apply_async( [credential_id, alarm],
												queue="loghub",
												routing_key="loghub"
												).get()
	if isinstance(module_response, dict):
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)

	elif isinstance(module_response, int):
		if module_response == 36:
			return jsonify(users_responses[36])

		elif module_response == 63:
			return jsonify(alarm_responses[63])

		elif module_response == 61:
			return jsonify(alarm_responses[61])

@app.route('/API/v1/alarms', methods=['GET'])
def get_alarms():
	credential_line = request.headers.get("X-Authorization", None)
	
	if not credential_line:
		return jsonify(users_responses[35])
	credential_id = credential_line.split()[1]
	module_response = alarms.get_alarms.apply_async([credential_id],
										queue="loghub",
										routing_key="loghub"
										).get()
	if isinstance(module_response, int):
		if module_response == 36:
			return users_responses[36]
	else:
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)

@app.route('/API/v1/alarms/<alarm_id>', methods=['GET'])
def get_alarm_by_id(alarm_id):
	credential_line = request.headers.get("X-Authorization", None)
	if not credential_line:
		return jsonify(users_responses[35])
	credential_id = credential_line.split()[1]
	module_response = alarms.get_alarm_by_id.apply_async([credential_id, alarm_id],
										queue="loghub",
										routing_key="loghub"
										).get()
	if isinstance(module_response, int):
		if module_response < 70 and module_response >= 60:
			return jsonify(alarm_responses[module_response])
	else:
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)


@app.route('/API/v1/alarms/<alarm_id>', methods=['DELETE'])
def delete_alarm(alarm_id):
	credential_line = request.headers.get("X-Authorization", None)
	if not credential_line:
		return jsonify(users_responses[35])
	credential_id = credential_line.split()[1]
	module_response = alarms.delete_alarm.apply_async([credential_id, alarm_id],
												queue="loghub",
												routing_key="loghub"
												).get()
	if isinstance(module_response, int):
		if module_response == 35:
			return jsonify(users_responses[35])
		elif module_response == 65:
			return jsonify(alarm_responses[65])

	elif isinstance(module_response, dict):
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)
