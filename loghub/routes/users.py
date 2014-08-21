from flask import request, jsonify, abort
from loghub import app
from loghub.modules import users
from loghub.routes.responses import generic_responses, users_responses
from functools import wraps

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
		abort(400)
	return data


def check_email(f):
	@wraps(f)
	def wrapped1(*args, **kwargs):
		data = jsonize_request()
		if "email" not in data:
			return jsonify(users_responses[33])
		elif "@" not in data["email"] or "." not in data["email"]:
			return jsonify(users_responses[34])
		return f(*args, **kwargs)
	return wrapped1


def check_password(f):
	@wraps(f)
	def wrapped2(*args, **kwargs):
		data = jsonize_request()
		if "password" not in data:
			return 37
		if len(data["password"]) < 6:
			return jsonify(users_responses[38])
		else:
			return f(*args, **kwargs)
	return wrapped2


@app.route('/API/v1/users', methods=['POST'])
@check_email
@check_password
def create_user():
	data = jsonize_request()
	module_response = users.create_user.apply_async([data["email"], data["password"]],
												queue="loghub",
												routing_key="loghub"
												).get()

	if isinstance(module_response, int):
		if module_response in users_responses:
			return jsonify(users_responses[module_response])
		else:
			return jsonify(users_responses[30])	
	response = generic_responses[20].copy()
	response["data"] = module_response
	return jsonify(response)



@app.route('/API/v1/user/<data>', methods=['GET'])
def get_user(data):
	data = dict([each.split("=") for each in data.split("&")])
	if "email" not in data:
		return jsonify(users_responses[33])
	elif "@" not in data["email"] or "." not in data["email"]:
		return jsonify(users_responses[34])

	module_response = users.get_user.apply_async([data["email"], data["password"]],
											queue="loghub",
											routing_key="loghub"
											).get()
	
	if not isinstance(module_response, dict):
		if isinstance(module_response, int):
			if module_response in users_responses:
				return jsonify(users_responses[module_response])
			else:
				return jsonify(users_responses[30])
	response = generic_responses[20].copy()
	response["data"] = module_response
	return jsonify(response)


@app.route('/API/v1/user/credential', methods=['POST'])
@check_email
@check_password
def reset_credential_id():
	data = jsonize_request()
	module_response = users.reset_credential_id.apply_async([data["email"], data["password"]],
													queue="loghub",
													routing_key="loghub"
													).get()
	if isinstance(module_response, int):
		return jsonify(users_responses[module_response])
	elif isinstance(module_response, dict):
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)
	else:
		return jsonify(generic_responses[19])


@app.route('/API/v1/user/password', methods=['PUT'])
@check_password
def change_user_password():
	credential_line = request.headers.get("X-Authorization", None)
	
	if not credential_line:
		return jsonify(users_responses[35])
	credential_id = credential_line.split()[1]
	
	data = jsonize_request()
	
	if "new_password" not in data:
		return jsonify(users_responses[37])
	module_response = users.change_user_password.apply_async([credential_id,
												 data["password"], 
												 data["new_password"]],
												 queue="loghub",
												 routing_key="loghub"
												 ).get()

	if isinstance(module_response, dict):
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)
	elif isinstance(module_response, int):
		return jsonify(users_responses[module_response])

@app.route('/API/v1/user/email', methods=['PUT'])
def change_user_email():
	credential_line = request.headers.get("X-Authorization", None)
	if not credential_line:
		return jsonify(users_responses[35])
	credential_id = credential_line.split()[1]
	data = jsonize_request()
	if "new_email" not in data:
		return jsonify(users_responses[33])
	elif "@" not in data["new_email"] or "." not in data["new_email"]:
		return jsonify(users_responses[34])
	
	module_response = users.change_user_email.apply_async([credential_id,
											  data["password"],
											  data["new_email"]],
											  queue="loghub",
											  routing_key="loghub"
											  ).get()
	if isinstance(module_response, dict):
		response = generic_responses[20].copy()
		response["data"] = module_response
		return jsonify(response)

	if isinstance(module_response, int):
		return jsonify(users_responses[module_response])


@app.route('/API/v1/auth/remember', methods=['POST'])
@check_email
def remember_account():
	data = jsonize_request()
	module_response = users.remember_account.apply_async([data["email"]],
													queue="loghub",
													routing_key="loghub"
													).get()
	if module_response == 20:
		response = generic_responses[20].copy()
		response["data"] = data
		return jsonify(response)
	else:
		return jsonify(users_responses[module_response])


@app.route('/API/v1/auth/reset_password', methods=['POST'])
@check_email
def reset_user_password():
	data = jsonize_request()
	if "code" not in data: 
		return jsonify(users_responses[39])
	if "new_password" not in data:
		return jsonify(users_responses[37])

	module_response = users.reset_user_password.apply_async([data["email"], 
										  data["new_password"],
										  data["code"]],
										  queue="loghub",
										  routing_key="loghub"
										  ).get()
	if module_response == 20:
		response = generic_responses[20].copy()
		response["data"] = data
		return jsonify(response)
	else:
		return jsonify(users_responses[module_response])