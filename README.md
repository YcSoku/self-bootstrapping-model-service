# self-bootstrapping-model-service (SBMS)
A parallelizable framework designed for the execution of complex geographical model services on a single backend machine. **SBMS** leverages implicit and self-organizing relationships, avoiding the need for a pre-defined global DAG, by dynamically coordinating model execution through local node dependencies and state-driven control.

To bridge the model using requests，the model scheduling and the calculated resource, a core class named **Model Case Reference (MCR)** is designed and applied. The instance of this class can transfer a model using request and its related runtime-dependent parameters (usually found in the request body) from the web-server layer to a specific model case folder. Consequently, any requests using the same model with the same parameters can be directed to the same model running case.

```mermaid
graph LR

        subgraph BMSAPIS[<b>APIS</b>]
            API0>API 0]
            API1>API 1]
            APIN>API...]
        end

        subgraph Models[<b>Models</b>]
            Model0[Model 0]
            Model1[Model 1]
            ModelN[Model...]
        end

        subgraph ModelRequests[<b>Model Using Requests</b>]
            Request0([Model Request 0])
            Request1([Model Request 1])
            Request2([Model Request 2])
            RequestN([Model Request...])
        end

        CaseID0(((<b>Case ID</b>)))

        subgraph ModelCaseReferences[<b>Model Case References</b>]
            MCR0((MCR 0))
            MCR1((MCR 1))
            MCRN((MCR...))
        end
        
        subgraph CaseContent[<b>Model Case Content In Disk</b>]
            Identity[identity.json]
            Response[response.json]
            subgraph Result[<b>Result</b>]
                File0[File 0]
                File1[File 1]
                FileN[File...]
            end
            subgraph Status[<b>Status</b>]
                StatusFile[StatusFile]
            end
        end

        subgraph Resource[<b>Resource</b>]
            subgraph DEMFiles[e.g. DEM Resource]
                DEM0[DEM Resource 0]
                DEM1[DEM Resource 1]
                DEMN[DEM Resource...]
            end
            
        end

    API0-->Request0
    Request0-.-|SAME API and REQUEST BODY|Request2
    API0-->Request2


    MCR0--o|PARSE REQUEST and USE|Model0

    MCR0--o|PARSE REQUEST and INPUT|DEM0
    MCR0--o|PARSE REQUEST and INPUT|DEM1
    MCR0-->|OUTPUT|Result
    MCR0-->|SERIALIZE|Identity
    MCR0-->|GENERATE after MODEL RUNNING COMPLETE|Response

    Request0-->|GENERATE from URL and REQUEST BODY|CaseID0
    Request2-->|GENERATE from URL and REQUEST BODY|CaseID0
    CaseID0-->MCR0
    MCR0==x|POINT TO|CaseContent
    MCR0-->|REFLECT MODEL RUNNING STATUS|Status

    style BMSAPIS fill:none
    style Models fill:none
    style ModelRequests fill:none
    style ModelCaseReferences fill:none
    style CaseContent fill:none
    style Resource fill:none
    style Result fill:none
    style Status fill:none
    style DEMFiles fill:none
```

**NOTE**

The basic condition for MCR to be **EFFECTIVE** is that when the model and parameters have not changed, the results of multiple runs are **COMPLETELY CONSISTENT**.

## Launch server

- Dependencies:
  
```
    FastAPI
    Portalocker
```

- Run: 
  
```
    python "run.py"
```
