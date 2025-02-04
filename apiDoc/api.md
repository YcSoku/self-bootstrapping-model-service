# Self-Bootstrapping Model Service (SBMS)

A parallelizable framework designed for the execution of complex geographical model services on a single backend machine.

---

## What Is <font color=red>Async</font>

Some of the SBMS APIs are marked with <font color=red>**Async**</font>. It means that, if a model case, related to a specific async api request, has not existed, model will run asynchronously and return response with  content "NONE" at once.

---

## Model Case

### Get Status of Model Case

Get the status of a specific model case.

```
GET /v0/mc/status?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
  	"status": "UNLOCK" || "LOCK" || "NONE" || "RUNNING" || "COMPLETE" || "ERROR"
}
```

<font color=red> **404** Model Case ID Not Found </font>   



### Get Status of Model Cases

Get the status of specific model cases.

```
POST /v0/mcs/status
```

**Request body schema**: application/json

```json
{
    "case-ids": [
        "{ case-id-0 }",
        "{ case-id-1 }",
        "{ case-id-n }"
    ]
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
  	"{ case-id-0 }": "UNLOCK" || "LOCK" || "NONE" || "RUNNING" || "COMPLETE" || "ERROR",
  	"{ case-id-1 }": "UNLOCK" || "LOCK" || "NONE" || "RUNNING" || "COMPLETE" || "ERROR",
  	"{ case-id-n }": "UNLOCK" || "LOCK" || "NONE" || "RUNNING" || "COMPLETE" || "ERROR"
}
```

<font color=red> **404** Model Case ID Not Found </font>  



### Get Call Time of Model Cases

Get the id and the last call time (Unix Epoch) of all model cases. The response array is sorted by the call time from the newest to oldest.

```
GET /v0/mcs/time
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "timestamps": [
        {
            "id": "{ case-id }",
            "time": "{ unix-timestamp }",
            "status": "LOCK" || "UNLOCK"
        }
    ]
}
```



### Get Serialized Content of Model Cases

Get the serialized content (request url and body) of model cases.

```
POST /v0/mcs/serialization
```

**Request body schema**: application/json

```json
{
    "case-ids": [
        "{ case-id-0 }",
        "{ case-id-1 }"
    ]
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "serialization-list": [
        {
            "id": "{ case-id }",
            "serialization": {
                "url": "{ request-url }",
                "json": "{ request-json }"
            }
        }
    ]
}
```

<font color=red> **404** Model Case ID Not Found </font>  



### Get Model Case Result

Get the result of a specific model case.

```
GET /v0/mc/result?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
  	"result": "{ model-case-result-json }"
}
```

<font color=red> **404** Model Case ID Not Found </font>  



### Get Error Log

Get the error log of a specific model case.

```
GET /v0/mc/error?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: text/plain

```txt
"{ error-log }"
```

<font color=red> **404** Model Case ID Not Found </font> 



### Get Preceding Error Cases

Get ids of preceding error cases that a specific model case dependences (The response list also contains the model case itself).

```
GET /v0/mc/pre-error-cases?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-list": [
        "{ case-ids }"
    ]
}
```

<font color=red> **404** Model Case ID Not Found </font> 



### Delete Model Case

Delete a specific model case.

```
DELETE /v0/mc?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

<font color=red> **404** Model Case ID Not Found </font>  



### Delete Model Cases

Delete model cases.

```
POST /v0/mcs
```

**Request body schema**: application/json

```json
{
    "case-ids": [
        "{ case-id }"
    ]
}
```

#### Responses  

<font color=green> **200** OK </font>  

<font color=red> **404** Model Case ID Not Found </font>  

---

## File

### Get Disk Usage

Get the size of the storage utilization (GB).

```
GET /v0/fs/usage
```

#### Response

<font color=green> **200** OK </font>

**Response schema**: application/json

```json
{
  	"usage": "{ disk-usage-giga-bytes }"
}
```


### Get Result File by Case ID

Get a result file in a specific model case through file's name.

```
GET /v0/fs/result/file?id="{ case-id }"&name="{ filename }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/octet-stream

<font color=red> **404** Filename Not Found </font>  

<font color=red> **404** Model Case ID Not Found </font>  


### Get Resource File by Directory

Get a resoruce file by directory.

```
GET /v0/fs/resource/file?name="{ file-directory }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/octet-stream

<font color=red> **404** Filename Not Found </font>  

<font color=red> **404** Model Case ID Not Found </font>  


### Get Result File Zip

Get a zip of the result files in a specific model case.

```
GET /v0/fs/result/zip?id="{ case-id }"
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/octet-stream

<font color=red> **404** Model Case ID Not Found </font>  


---


## Riverbed Evolution  

### Calculate Region Flush (<font color=red>Async</font>)

Calculate the flush result by dem resource at two timepoints within a specific region or the full area. 

- If "region-geometry" in request body is "NONE", server will calculate the global flush.

```
POST /v0/re/region-flush
```

**Request body schema**: application/json

```json
{
    "bench-id": "{ dem-file-name }",
    "ref-id": "{ dem-file-name }",
    "region-geometry": "{ GeoJson }" || "NONE"
}
```

**Example**

``````json
{
    "bench-id": "199801_dem/w001001.adf",
    "ref-id": "200408_dem/w001001.adf",
    "region-geometry": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "properties": {
            "name": "Example Polygon"
          },
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [121.35857784308524,31.660508611487913],
                [121.29264135171792,31.576285441022137],
                [121.45748258013526,31.57394482076768],
                [121.3860513811536,31.508383603511106],
                [121.50693494865948,31.56458175211411],
                [121.35857784308524,31.660508611487913]
              ]
            ]
          }
        }
      ]
  	}
}
``````

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
    "raw-tif": "{ file-name }" || "NONE",
    "extent-json": "{ file-name }" || "NONE",
    "visualization-png": "{ file-name }" || "NONE",
}
```

<font color=red> **404** Dem Resource Not Found </font>  



### Calculate Section View (<font color=red>Async</font>)

Calculate the section view and slope ratio by a specific dem resource.

```
POST /v0/re/section-view
```

**Request body schema**: application/json

```json
{
    "dem-id": "{ dem-file-name }",
    "section-geometry": "{ GeoJson }"
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
    "raw-json": "{ file-name }" || "NONE",
    "visualization-txt": "{ file-name }" || "NONE"
    "interval": "{ number }" || "NONE"
}
```

<font color=red> **404** Dem Resource Not Found </font>  



### Calculate Section Contrast (<font color=red>Async</font>)

Calculate the flush from the perspective of section and provide a section views at two timepoints.

```
POST /v0/re/section-contrast
```

**Request body schema**: application/json

```json
{
    "bench-id": "{ dem-file-name }",
  	"ref-id": "{ dem-file-name }",
    "section-geometry": "{ GeoJson }"
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
    "raw-txt": "{ file-name }" || "NONE"
    "interval": "{ number }" || "NONE"
}
```

<font color=red> **404** Dem Resource Not Found </font>  



### Calculate River Volume (<font color=red>Async</font>)

Calculate the river volume within a specific region.

```
POST /v0/re/river-volume
```

**Request body schema**: application/json

```json
{
  	"dem-id": "{ dem-file-name }",
    "region-geometry": "{ GeoJson }",
    "water-depth": "{ number-water-depth }"
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
  	"raw-tif": "{ file-name }" || "NONE",
    "extent-json": "{ file-name }" || "NONE",
  	"visualization-png": "{ file-name }" || "NONE",
    "volume-summary-txt": "{ file-name }" || "NONE",
}
```

<font color=red> **404** Dem Resource Not Found </font>  



### Calculate Region Contour (<font color=red>Async</font>)

Calculate the contour lines within a specific region or the full area. 

- If "region-geometry" in request body is "NONE", server will calculate the global flush contour lines.

```
POST /v0/re/region-contour
```

**Request body schema**: application/json

```json
{
  	"bench-id": "{ dem-file-name }",
  	"ref-id": "{ dem-file-name }",
    "region-geometry": "{ GeoJson }"
}
```

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
  	"raw-shp": "{ file-name }" || "NONE",
    "visualization-geojson": "{ file-name }" || "NONE"
}
```

<font color=red> **404** Dem Resource Not Found </font>  
