import json


def json_response(request, data=None, **kwargs):
    request.response.setHeader('Content-Type', 'application/json')
    request.response.setHeader('X-Theme-Disabled', 'True')
    return json.dumps(data or kwargs)
