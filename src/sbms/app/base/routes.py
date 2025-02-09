import os
import re
import json
import asyncio
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi import Request, APIRouter, HTTPException, Query

from ... import config, util
from .controllers import api_handlers

router = APIRouter()

######################################## API for Model Case ########################################

@router.get(config.API_MC_GET_STATUS)
async def get_model_case_status(case_id: str = Query(..., description='case-id')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_MC_GET_STATUS], case_id)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.get(config.API_MC_GET_RESULT)
async def get_model_case_result(case_id: str = Query(..., description='case-id')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_MC_GET_RESULT], case_id)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.get(config.API_MC_GET_ERROR)
async def get_model_case_error(case_id: str = Query(..., description='case-id')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_MC_GET_ERROR], case_id)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.get(config.API_MC_GET_PRE_ERROR_CASES)
async def get_pre_error_cases(case_id: str = Query(..., description='case-id')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_MC_GET_PRE_ERROR_CASES], case_id)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.delete(config.API_MC_DELETE_DELETE)
async def delete_model_case(case_id: str = Query(..., description='case-id')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_MC_DELETE_DELETE], case_id)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.post(config.API_MCS_POST_STATUS)
async def get_model_cases_status(request: Request):
    
    payload = await request.json()
    status, response = await asyncio.to_thread(api_handlers[config.API_MCS_POST_STATUS], payload)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.get(config.API_MCS_GET_TIME)
async def get_model_cases_call_time():
    
    response = await asyncio.to_thread(api_handlers[config.API_MCS_GET_TIME])
    return response

@router.post(config.API_MCS_POST_SERIALIZATION)
async def get_model_cases_serialization(request: Request):
    
    payload = await request.json()
    status, response = await asyncio.to_thread(api_handlers[config.API_MCS_POST_SERIALIZATION], payload)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.post(config.API_MCS_POST_DELETE)
async def delete_model_cases(request: Request):
    
    payload = await request.json()
    status, response = await asyncio.to_thread(api_handlers[config.API_MCS_POST_DELETE], payload)
    if status == 200:
        return response
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

######################################## API for File System ########################################

@router.get(config.API_FS_GET_DISK_USAGE)
async def get_disk_usage():
    
    return await asyncio.to_thread(api_handlers[config.API_FS_GET_DISK_USAGE])

@router.get(config.API_FS_GET_RESULT_FILE)
async def get_model_case_file(case_id: str = Query(..., description='case-id'), filename: str = Query(..., description='filename')):
    
    status, response = await asyncio.to_thread(api_handlers[config.API_FS_GET_RESULT_FILE], case_id, filename)
    
    if status == 200:
        return StreamingResponse(util.generate_large_file(response), 
                                 media_type='application/octet-stream',
                                 headers={'Content-Disposition': f'attachment; filename={response}'})
    if status == 404:
        raise HTTPException(status_code=404, detail=response)

@router.get(config.API_FS_GET_RESULT_ZIP)
async def download_processed_zip(request: Request, case_id: str = Query(..., description='case-id'), filename: str = Query(..., description='filename')):
    
    file_path = os.path.join(config.DIR_MODEL_CASE, case_id, 'result', filename)

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"status": 404, "message": "File not found"})

    range_header = request.headers.get('Range')

    if not range_header:
        return FileResponse(file_path, filename="gridInfo.zip", media_type="application/zip")

    match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
    file_size = os.path.getsize(file_path)

    if not match:
        return JSONResponse(status_code=416, content={"status": 416, "message": "Invalid Range"})

    start, end = match.groups()
    start = int(start)
    end = int(end) if end else file_size - 1
    end = min(end, file_size - 1)
    content_length = end - start + 1

    if start >= file_size or end >= file_size or start > end:
        return JSONResponse(status_code=416, content={"status": 416, "message": "Invalid Range"})

    def file_reader():
        with open(file_path, 'rb') as f:
            f.seek(start)
            yield f.read(content_length)

    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Content-Length': str(content_length),
        'Content-Type': 'application/zip'
    }
    return StreamingResponse(file_reader(), status_code=206, headers=headers)

######################################## API for Models ########################################

@router.get(config.API_MR)
async def set_model_runner_get(category: str, model_name: str, request: Request):
    
    if request.method == "GET":
        status, response = await asyncio.to_thread(api_handlers[config.API_MR], f'{config.API_VERSION}/{category}/{model_name}', request.query_params)
    
    if status == 200:
        return response
    raise HTTPException(status_code=status, detail=response)

@router.post(config.API_MR)
async def set_model_runner_post(category: str, model_name: str, request: Request):
    
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        request_json = await request.json()
    else:
        form = await request.form()
        request_json = json.loads(form['json'])
        request_json.update(form)

    status, response = api_handlers[config.API_MR](f'{config.API_VERSION}/{category}/{model_name}', request_json)
    
    if status == 200:
        return response
    raise HTTPException(status_code=status, detail=response)
