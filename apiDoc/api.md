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

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/octet-stream

<font color=red> **404** Model Case ID Not Found </font>  


---


## First Example 

### Hello (<font color=red>Async</font>)

Hello SBMS

```
POST /v0/fe/hello
```

**Request body schema**: application/json

```json
{
    "name": "{ string-name }"
}
```

**Example**

``````json
{
    "name": "SBMS"
}
``````

#### Responses  

<font color=green> **200** OK </font>  

**Response schema**: application/json

```json
{
    "case-id": "{ case-id }",
  	"model": "{ model-name }",
    "message": "{ string-message }" || "NONE"
}
```

