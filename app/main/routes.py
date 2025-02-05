import os
import re
import json
from flask import request, abort, Response, jsonify, send_file

from . import bp
from ... import util
from ... import config
from .controllers import handle_mr, api_handlers

######################################## API for Model Case ########################################

@bp.route(config.API_MC_GET_STATUS, methods=[ 'GET' ])
def get_model_case_status():
    
    case_id = request.args.get('id', type=str)
    
    status, response = api_handlers[config.API_MC_GET_STATUS](case_id)
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)

@bp.route(config.API_MC_GET_RESULT, methods=[ 'GET' ])
def get_model_case_result():
    
    case_id = request.args.get('id', type=str)
    status, response = api_handlers[config.API_MC_GET_RESULT](case_id)
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)
        
@bp.route(config.API_MC_GET_ERROR, methods=[ 'GET' ])
def get_model_case_error():
    
    case_id = request.args.get('id', type=str)
    status, response = api_handlers[config.API_MC_GET_ERROR](case_id)
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)

@bp.route(config.API_MC_GET_PRE_ERROR_CASES, methods=[ 'GET' ])
def get_pre_error_cases():
    
    case_id = request.args.get('id', type=str)
    status, resposne = api_handlers[config.API_MC_GET_PRE_ERROR_CASES](case_id)
    if status == 200:
        return resposne
    if status == 404:
        abort(404, description=resposne)

@bp.route(config.API_MC_DELETE_DELETE, methods = [ 'DELETE' ])
def delete_model_case():
    
    case_id = request.args.get('id', type=str)
    status, response = api_handlers[config.API_MC_DELETE_DELETE](case_id)
    
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)
        
@bp.route(config.API_MCS_POST_STATUS, methods=[ 'POST' ])
def get_model_cases_status():
    
    status, response = api_handlers[config.API_MCS_POST_STATUS](request.get_json())
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)

@bp.route(config.API_MCS_GET_TIME, methods=[ 'GET' ])
def get_model_cases_call_time():
    
    response = api_handlers[config.API_MCS_GET_TIME]()
    return response

@bp.route(config.API_MCS_POST_SERIALIZATION, methods=[ 'POST' ])
def get_model_cases_serialization():
    
    status, response = api_handlers[config.API_MCS_POST_SERIALIZATION](request.get_json())
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)

@bp.route(config.API_MCS_POST_DELETE, methods = [ 'POST' ])
def delete_model_cases():
    
    status, response = api_handlers[config.API_MCS_POST_DELETE](request.get_json())
    
    if status == 200:
        return response
    if status == 404:
        abort(404, description=response)

######################################## API for File System ########################################

@bp.route(config.API_FS_GET_DISK_USAGE, methods=[ 'GET' ])
def get_disk_usage():
    return api_handlers[config.API_FS_GET_DISK_USAGE]()

@bp.route(config.API_FS_GET_RESULT_FILE, methods=[ 'GET' ])
def get_model_case_file():
    
    case_id = request.args.get('id', type=str)
    filename = request.args.get('name', type=str)
    status, response = api_handlers[config.API_FS_GET_RESULT_FILE](case_id, filename)
    
    if status == 200:
        return Response(util.generate_large_file(response), 
                        mimetype='application/octet-stream',
                        headers={'Content-Disposition': f'attachment; filename={response}'})
    if status == 404:
        abort(404, description=response)

@bp.route(config.API_FS_GET_RESULT_ZIP, methods=[ 'GET' ]) 
def download_processed_zip():

    # Calculate the download path
    case_id = request.args.get('id', type=str)
    filename = request.args.get('name', type=str)
    file_path = os.path.join(config.DIR_MODEL_CASE, case_id, 'result', filename)
    
    # Case file not found
    if not os.path.exists(file_path):
        return jsonify({
            'status': 404,
            'message': 'File not found'
        }), 404
    
    range_header = request.headers.get('Range', None)

    # Case file transfer by whole
    if not range_header:
        return send_file(file_path, as_attachment=True, download_name='gridInfo.zip')

    # Case file transfer by range
    match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
    file_size = os.path.getsize(file_path)

    if not match:
        return jsonify({
            'status': 416, # requested range not satisfiable
            'message': 'Invalid Range'
        }), 416

    # Calc the chunk range
    start, end = match.groups()
    start = int(start)
    end = int(end) if end else file_size - 1
    end = min(end, file_size - 1)
    content_length = end - start + 1

    if start >= file_size or end >= file_size or start > end:
        return jsonify({
            'status': 416,
            'message': 'Invalid Range'
        }), 416
    
    response = Response()
    response.status_code = 206 # partial content
    response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response.headers['Content-Length'] = str(content_length)
    response.headers['Content-Type'] = 'application/zip'
    with open(file_path, 'rb') as f:
        f.seek(start)
        response.data = f.read(content_length)

    return response

######################################## API for Models ########################################

@bp.route(config.API_MR, methods=[ 'GET', 'POST' ])
def set_model_runner(category: str, model_name: str):
    
    if request.method == 'GET':
        status, response = handle_mr(f'{config.API_VERSION}/{category}/{model_name}', request.args.to_dict())
    elif request.method == 'POST':
        if len(request.files) == 0:
            request_json = request.get_json()
        else:
            form_json = json.loads(request.form['json'])
            request_json = form_json
            request_json.update(request.files.to_dict())
        status, response = handle_mr(f'{config.API_VERSION}/{category}/{model_name}', request_json)
        
    if status == 200:
        return response


if __name__ == '__main__':

    print("--------------------------------------")
    bp.run(host='0.0.0.0', port=config.APP_PORT, debug=config.APP_DEBUG)
