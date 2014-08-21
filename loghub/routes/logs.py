from flask import request, jsonify
from loghub import app
from loghub.modules import logs
from loghub.routes.responses import generic_responses, log_responses

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

@app.route('/API/v1/applications/<APP_TOKEN>/', methods=['POST'])
def logging(APP_TOKEN):
    credential = request.headers.get('X-Authorization', None)
    
    if not credential:
        return jsonify(log_responses[55])

    credential_id = credential.split()[1]
    entry = jsonize_request()
    module_response = logs.logging.apply_async(
                                            [APP_TOKEN,entry],
                                            queue="loghub",
                                            routing_key="loghub"
                                            ).get()

    
    if isinstance(module_response, dict):
        response = generic_responses[20].copy()
        response["data"] = entry
        return jsonify(response)

    if not isinstance(module_response, int):
        return jsonify(generic_responses[19])


    if isinstance(module_response, int):
        return jsonify(log_responses[module_response])

@app.route('/API/v1/logs', methods=['GET'])
def query_log(limit=None,level=None,keyword=None,newerThan=None,olderThan=None):
    credential = request.headers.get('X-Authorization',None)
    
    if not credential:
        return jsonify(log_responses[55])

    credential_id = credential.split()[1]

    module_response = logs.query_log.apply_async([credential_id,
                                        limit, level,
                                        keyword, newerThan,
                                        olderThan],
                                        queue="loghub",
                                        routing_key="loghub"
                                        ).get()
    print(module_response)

    if isinstance(module_response, int):
        return jsonify(log_responses[module_response])
    
    for entry in module_response:
        entry["_id"] = str(entry["_id"])

    if isinstance(module_response, list):
        response = generic_responses[20].copy()    
        response["data"] = {}
        response["data"]["entries"] = module_response
    
        return jsonify(response)

    if module_response == 19:
        return jsonify(generic_responses[19])

    

    
