# BIM2TWIN - Integration with ThingIn platform

This repository contains the first version of the API to communicate with Digital Twin Platform (DTP),
i.e., [Thing'in](https://thinginthefuture.bim2twin.eu). The purpose of this document is to explain the code and its
usage.

The code was extracted from the internal code of WP3.

## Setting up the environment

The integration code has been written in python, and the environment has been set up using conda.

We recommend create conda environment:

```conda env create -n DTP_V1 python=3.9```

activate conda environment and install packages by:

```
conda activate DTP_V1
pip install -r requirements.txt
```

Once the conda environment is set up and activated, we are ready to run the code.

## Authentication

DTP_API will automatically get the authentication token from [Thing'in](https://thinginthefuture.bim2twin.eu). It will
prompt you to enter your Thing'in credentials. The Thing'in token expires after 24hrs; thus, you only will be asked to
enter your credentials again when the current token is expired.

## Logged information

Currently, the program is using two logs: the general log stored in `global.log`, and the second `db_session_x.log`,
used or storing information about database changing queries. The second log can be used to revert changes done on the
database. In order to revert to the last session, it is necessary to call the program with the argument `-r` followed by
the path to the file. In principle, the database can also be restored from the general log file, but this option has not
been sufficiently tested. `db_session_x.log` will be stored in `sessions` folder in log path (`LOG_DIR` in
`DTP_config.xml`).

**Note that, the general log file `global.log`, contains also raw HTTP requests, together with the authentication
token. Session is logged only for `create_DTP_API`, `link_DTP_API` and `update_DTP_API`.**

### Example of the general log file

```
9-Oct-22 15:57:34 : INFO : New session has been started.
09-Oct-22 15:57:34 : INFO : Work folder set to: C:\Users\kpluta\Projects\BIM2TWIN-WP3\DTP\integration_v1
09-Oct-22 15:57:34 : INFO : XML config set to: C:\Users\kpluta\Projects\BIM2TWIN-WP3\DTP\integration_v1\DTP_config.xml
09-Oct-22 15:57:34 : INFO : PCD set to: C:\Users\kpluta\Projects\BIM2TWIN-WP3\DTP\integration_v1\tests\dummy_GA_PCD.ply
09-Oct-22 15:57:34 : INFO : Running in the simulator mode.
09-Oct-22 15:57:34 : INFO : DTP_API - START SESSION
09-Oct-22 15:57:34 : INFO : HTTP request: 
-----------START-----------
POST https://api.thinginthefuture.bim2twin.eu/avatars/find

Content-Type: application/json

Accept: application/json

Authorization: Bearer <token_removed>

Content-Length: 170


{
   "query":{
      "$domain":"http://bim2twin.eu/general_assembly_wp3/",
      "$classes":"https://w3id.org/bot#Element",
      "https://www.bim2twin.eu/ontology/Core#isAsDesigned":true
   }
}
-----------END-----------
09-Oct-22 15:57:34 : DEBUG : Starting new HTTPS connection (1): api.thinginthefuture.bim2twin.eu:443
09-Oct-22 15:57:34 : DEBUG : https://api.thinginthefuture.bim2twin.eu:443 "POST /avatars/find HTTP/1.1" 308 284
09-Oct-22 15:57:34 : DEBUG : https://api.thinginthefuture.bim2twin.eu:443 "POST /avatars/find/ HTTP/1.1" 200 2227
09-Oct-22 15:57:34 : INFO : Response code: 200
```

### Example of the db session log file

```
10-Oct-22 13:49:01 : DTP_API - START SESSION
10-Oct-22 13:49:12 : DTP_API - NEW_ELEMENT_IRI: http://bim2twin.eu/general_assembly_wp3/asbuiltelement0021
10-Oct-22 13:49:13 : DTP_API - NEW_BLOB: ad6f0631-6c01-4aa6-a62a-600e9be1f087
10-Oct-22 13:49:13 : DTP_API - NEW_LINK_ELEMENT_BLOB: 4a93f8c6-9a51-5682-b787-94de731965eb, ad6f0631-6c01-4aa6-a62a-600e9be1f087
10-Oct-22 13:49:35 : DTP_API - END SESSION
```

## Control via YAML configuration file

Configuration file is used to generalize the integration and push certain information from the code to the
external configuration file to make the implementation general and easy to maintain.

### DTP configuration file

`DTP_config.yaml` is defined as DTP configuration file and has following:

* `DTP_DOMAIN` : the domain used for the session
* `KPI_DOMAIN` : the KPI domain used for the session
* `LOG_DIR` : Log directory

## Code structure

```
├── DTP_API.py                              # Base API class for mixin classes
├── dtp_apis
│   ├── count_DTP_API.py                    # Mixin count API class
│   ├── create_DTP_API.py                   # Mixin create API class
│   ├── fetch_DTP_API.py                    # Mixin fetch API class
│   ├── link_DTP_API.py                     # Mixin link API class
│   ├── revert_DTP_API.py                   # Mixin revert API class
│   └── send_DTP_API.py                     # Mixin send API class
├── DTP_config.py                           # Configuration parser class
├── DTP_config.yaml                         # DTP configuration file
├── uri_mappings.yaml                       # Onotology and Thing'in API mappings
├── examples                                # API examples
├── helpers.py                              # shared functions
├── multiprocessing_logging.py              # enables multiprocessing
├── README.md
├── requirements.txt                        # requirments for DTP API
└── thingin_token.txt                       # store Thing'in token here

```

## Creating IRI for new as-performed nodes

Below is the rule to generate iri for a new as-performed node from an as-planned node iri. `create_as_performed_iri`
function in `helpers.py` can help you create as-performed iri from as-planned iri.

| As-planned type | As-planned IRI                           | As-performed IRI                          |
|-----------------|:-----------------------------------------|:------------------------------------------|
| Element         | http://bim2twin.eu/domain/ifc-xyz        | http://bim2twin.eu/domain/asbuilt-xyz     |
| Task            | http://bim2twin.eu/domain/task123        | http://bim2twin.eu/domain/action123       |
| Activity        | http://bim2twin.eu/domain/activity123    | http://bim2twin.eu/domain/operation123    |
| Work package    | http://bim2twin.eu/domain/workpackage123 | http://bim2twin.eu/domain/construction123 |

## Examples

Please see the `examples` folder for sample code to use DTP APIs. Please note session logging in examples are for
demonstration, session logger will be only used in `create_DTP_API`, `link_DTP_API` and `update_DTP_API`.

Count task nodes connected to a node identified by `activity_node_iri`

```shell
python3 count_activity_tasks.py --config_path ../DTP_config.yaml
```

Fetch operation nodes connected to a node identified by `constr_node_iri`

```shell
python3 fetch_construction_operation.py --config_path ../DTP_config.yaml
```

Fetch all activity node in the graph

```shell
python3 fetch_all_activity.py --config_path ../DTP_config.yaml
```

Create as-built from as-designed node

```shell
python3 asdesigned_to_asbuilt.py --config_path ../DTP_config.yaml
```

Revert a session with log file

```shell
python3 revert_session.py --config_path ../DTP_config.yaml --revert /path/to/sessions/db_session-dd-tt.log
```