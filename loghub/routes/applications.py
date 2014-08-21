from flask import request, jsonify, abort
from loghub import app
from loghub.modules import applications
from loghub.routes.responses import generic_responses, applications_responses


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



@app.route('/API/v1/applications', methods=['POST'])
def register_app():
    credential = request.headers.get('X-Authorization',None)
    if not credential:
        return jsonify(applications_responses[43])
    credential_id = credential.split()[1]
    data = jsonize_request()
    if "name" not in data:
        return applications_responses[42]
    
    module_response = applications.register_app.apply_async([data["name"], credential_id],
                                                    queue="loghub",
                                                    routing_key="loghub"
                                                    ).get()


    module_response["_id"] = str(module_response["_id"])

    if isinstance(module_response, int):
        if module_response == 19:
            return jsonify(generic_responses[19])
    
    if isinstance(module_response, dict):
        response = generic_responses[20].copy()        
        response["data"] =  module_response        
        return jsonify(response)

    if not isinstance(module_response, int):
        return jsonify(generic_responses[19])

    else:
        return jsonify(applications_responses[module_response])


@app.route('/API/v1/applications', methods=['GET'])
def get_apps():
    credential = request.headers.get('X-Authorization', None)
    
    if not credential:
        return jsonify(applications_responses[43])

    credential_id = credential.split()[1]
    module_response = applications.get_apps.apply_async([credential_id],
                                                    queue="loghub",
                                                    routing_key="loghub"
                                                    ).get()
    if module_response == 19:
        return jsonify(generic_responses[module_response])
    if isinstance(module_response, int):
        return jsonify(applications_responses[module_response])

    elif isinstance(module_response, list):
        response = generic_responses[20].copy()
        response["data"] = module_response
        return jsonify(response)
    else:
        return jsonify(applications_responses[19])

@app.route('/API/v1/applications/<APP_TOKEN>/', methods=['GET'])
def get_app(APP_TOKEN):
    credential = request.headers.get('X-Authorization', None)
    
    if not credential:
        return jsonify(applications_responses[43])

    credential_id = credential.split()[1]
    
    module_response = applications.get_app.apply_async([credential_id, APP_TOKEN],
                                                    queue= "loghub",
                                                    routing_key= "loghub"
                                                    ).get()
    
    if module_response == 19:
        return jsonify(generic_responses[module_response])
    if isinstance(module_response, int):
        return jsonify(applications_responses[module_response])

    elif isinstance(module_response, dict):
        response = generic_responses[20].copy()
        response["data"] = module_response
        return jsonify(response)
    else:
        return jsonify(applications_responses[19])



@app.route('/API/v1/applications/<APP_TOKEN>/', methods=['DELETE'])
def delete_apps(APP_TOKEN):
    credential = request.headers.get('X-Authorization', None)
    
    if not credential:
        return jsonify(applications_responses[43])
    credential_id = credential.split()[1]

    module_response = applications.delete_apps.apply_async([APP_TOKEN, credential_id],
                                                    queue="loghub",
                                                    routing_key="loghub"
                                                    ).get()
    
    if  isinstance(module_response, dict):
        response = generic_responses[20].copy()
        module_response["_id"] = str(module_response["_id"])
        response["data"] =  module_response      
        return jsonify(response)

    if isinstance(module_response, int):
        return jsonify(applications_responses[module_response])
    else:
        return jsonify(generic_responses[19])

@app.route('/API/v1/applications/<APP_TOKEN>/token', methods=['PUT'])
def reset_app_token(APP_TOKEN):
    credential = request.headers.get('X-Authorization', None)
    credential_id = credential.split()[1]
    if not credential_id:
        return jsonify(applications_responses[47])
    module_response = applications.reset_app_token.apply_async( [APP_TOKEN, credential_id],
                                                        queue="loghub",
                                                        routing_key="loghub"
                                                        ).get()
    
    if isinstance(module_response, dict):
        response = generic_responses[20].copy()
        module_response["_id"] = str(module_response["_id"])
        response["data"] =  module_response      
        return jsonify(response)
        
    if isinstance(module_response, int):
        return jsonify(applications_responses[module_response])