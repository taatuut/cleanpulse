# clean clean, always clean
"Real-time insights for spotless performance". An application that focuses on reporting the cleaning activities of machines in a factory, including details such as the last cleaning time, duration, water usage, and energy usage. Relevant for CPG industry, like beer breweries and coffee-roasting factories.

## what we are aiming for
Real-time information into a high-tech industrial control room with multiple digital dashboards showing live data feeds. One dashboard highlights real-time cleaning activities of robotic and automated machines in a brewery and factory. Screens display animated timelines, sensor graphs, heatmaps of machine cleanliness, and event logs. Overlaid holographic UI elements show Solace PubSub+ messaging icons, AI analytics charts, and alerts. In the background, factory floors and brewing tanks are visible through glass walls, with autonomous cleaning robots in action. "Powered by CleanPulse AI".

## context of the demo
Components:
1. Solace Event Broker: To facilitate real-time event streaming and message routing.
2. Solace Micro Integration Component: For integrating energy consumption from machines and processing events.
3. Solace Agent Mesh: analysis of the machine energy usage, detect anormal patterns, analyse the electricity, water consumption, etc
* Event Generation:
	* Sensors on Machines: Each machine is equipped with sensors that generate events related to cleaning activities (e.g., start time, end time, water usage, energy consumption).
	* Event Broker: These events are published to the Solace Event Broker.
	* Micro Integration: some events need to have an intermediary component to do protocol bridging for instance, and MI are perfect fit
* Data Storage:
	* Database:  events are stored in a sqlite and neo4j database for historical analysis and reporting.
* Analytics: An analytics engine can be used to generate insights and reports on cleaning activities, such as trends in water and energy usage, frequency of cleanings, and compliance with cleaning schedules.
On the data in sqlite IsolationForest analysis is run periodically to detect outliers. In neo4j relations are created between the individual events showing the overall patterns and phenomenons.

## steps- concept, please add/change
- create application description and use ai event model wizard to create app with events
- follow outline at https://feeds.solace.dev/ to create feed (@magali, you had some ideas on topics and payload?)
- create feed(s) would be nice if these are semirandom so we cabn use ai to detect patterns in there, check if this is possible with feed
- create event mesh
- publish feed to mesh
- add ai agent as subscriber to detect patterns (like 'cleaning at night/weekend is cheaper because of energy cost', 'cleaning on friday uses way more chemicals because too long cleaning interval following Sun-Tue-Fri scheudle', just making these up) 
- publish or subscribe a analytics / dashboard

![hitech industrial control room with multiple digital dashboards showing live data feeds featuring real-time cleaning activities](https://github.com/user-attachments/assets/f9e7a312-6471-4631-a278-fd53e49e5218)

## Context
This demo is developed for Solace SKO FY26 on macOS using Python (3.10.6+) and Colimna. Some terminal commands need to be adjusted to run on Linux or Windows. 

## Repo
`git clone https://github.com/taatuut/cleanpulse.git`

## Setup

### Set environment variables
Check `sample.env` and copy/create `.env` with own values, then run:

```
source .env
```

Add relevant application information to configuration file `config.json`.

### Python

Create and source a Python virtual environment, this demo use `~/.venv`.

Open a terminal and run:

```
mkdir -p ~/.venv && python3 -m venv ~/.venv && source ~/.venv/bin/activate
```

Install Python modules (optional: `upgrade pip`)

```
python3 -m pip install --upgrade pip
python3 -m pip install requests lxml solace-pubsubplus pyyaml pandas scikit-learn neo4j dash plotly solace-agent-mesh
```

### Solace Agent Mesh - SAM

Run `solace-agent-mesh --version` to verify your SAM installation. Will respond with something like `solace-agent-mesh, version 0.2.3`.

Create SAM project folder and go there with `mkdir -p ezsam && cd ezsam && touch .empty`.

Run `solace-agent-mesh init` and follow the prompts to create your project.

In the web interface select [ Get Started Quickly ] and click [ Next ]

In next screen enter details as below and click [ Next ]

```
OpenAI Compatible Provider
https://lite-llm.mymaas.net/
<LiteLLM_API_key>
azure-gpt-4o
```

Output will look something like:

```
solace-agent-mesh init
Initializing Solace Agent Mesh
Would you like to configure your project through a web interface in your browser? [Y/n]: 
Step 1 of 1: Initilize in web
Web configuration portal is running at http://127.0.0.1:5002
Complete the configuration in your browser to continue...
Configuration received from portal
Project files have been created.
Created the following gateway template files:
  - ./configs/gateways/rest_api/rest-api.yaml
  - ./configs/gateways/rest_api/gateway.yaml
Solace Agent Mesh has been initialized
Review the `solace-agent-mesh` config file and make any necessary changes.
To get started, use the `solace-agent-mesh add` command to add agents and gateways
```

Now add the SQL Database plugin to your SAM project:

```
solace-agent-mesh plugin add sam_sql_database --pip -u git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-sql-database

Module 'sam_sql_database' not found. Attempting to install 'git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-sql-database' using pip...
Collecting git+https://github.com/SolaceLabs/solace-agent-mesh-core-plugins#subdirectory=sam-sql-database
  Cloning https://github.com/SolaceLabs/solace-agent-mesh-core-plugins to /private/var/folders/f5/dymfy2kx71l1wqwygnkz4fw40000gn/T/pip-req-build-98llfgm2
  Running command git clone --filter=blob:none --quiet https://github.com/SolaceLabs/solace-agent-mesh-core-plugins /private/var/folders/f5/dymfy2kx71l1wqwygnkz4fw40000gn/T/pip-req-build-98llfgm2
  Resolved https://github.com/SolaceLabs/solace-agent-mesh-core-plugins to commit da3096ba4103afa0fa399e29f4b2b044bbd49f5c
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting mysql-connector-python>=8.3.0 (from sam_sql_database==0.0.1)
  Using cached mysql_connector_python-9.3.0-cp313-cp313-macosx_14_0_arm64.whl.metadata (7.5 kB)
Collecting psycopg2-binary>=2.9.9 (from sam_sql_database==0.0.1)
  Using cached psycopg2_binary-2.9.10-cp313-cp313-macosx_14_0_arm64.whl.metadata (4.9 kB)
Requirement already satisfied: sqlalchemy>=2.0.25 in /Users/emilzegers/.venv/lib/python3.13/site-packages (from sam_sql_database==0.0.1) (2.0.40)
Requirement already satisfied: typing-extensions>=4.6.0 in /Users/emilzegers/.venv/lib/python3.13/site-packages (from sqlalchemy>=2.0.25->sam_sql_database==0.0.1) (4.14.0)
Using cached mysql_connector_python-9.3.0-cp313-cp313-macosx_14_0_arm64.whl (15.2 MB)
Using cached psycopg2_binary-2.9.10-cp313-cp313-macosx_14_0_arm64.whl (3.3 MB)
Building wheels for collected packages: sam_sql_database
  Building wheel for sam_sql_database (pyproject.toml) ... done
  Created wheel for sam_sql_database: filename=sam_sql_database-0.0.1-py3-none-any.whl size=19297 sha256=050bc62bec55753b807232fe1afa859b3c149a391f3b020935a5cec3ac713445
  Stored in directory: /private/var/folders/f5/dymfy2kx71l1wqwygnkz4fw40000gn/T/pip-ephem-wheel-cache-s08ku__0/wheels/9c/33/11/590d2ff34c9055bbfa77cedcedd2230315b2f160ff6fb09705
Successfully built sam_sql_database
Installing collected packages: psycopg2-binary, mysql-connector-python, sam_sql_database
Successfully installed mysql-connector-python-9.3.0 psycopg2-binary-2.9.10 sam_sql_database-0.0.1
Successfully added plugin 'sam_sql_database'.
```

Then create an agent instance based on the SQL database template:

```
sam add agent energy_usage_info --copy-from sam_sql_database:sql_database

Copied agent 'energy_usage_info' from plugin 'sam_sql_database' at: ./configs/agents
```

To build and start the Solace Agent Mesh service, run `sam run -b`. You can use `sam` as a shorthand for `solace-agent-mesh` in all commands. See appendix for output.

Go to the interface (http://localhost:5001/) and ask the following questions, 1-3 are for verficiation.

1.
How many plants does Dummython company has?

2.
Create a table summarizing number of machine per building per plant for company Dummython. 

3.
What is the total number of machines at Dummython company.

4.
CURL
Based on analysis of a combined ranking of the metrics for the levels of dust, sticky stuff and odor at the machines, using the representing values in columns sri, dli and odi, determine top 3 of machines for all buildings and plants that need to be stopped for cleaning maintenance and create a curl POST request command to send the machine ids, and the estimated number of minutes the cleaning will take in json format to http://localhost:54322/ Provide the complete curl command as response.

POST
Based on analysis of a combined ranking of the metrics for the levels of dust, sticky stuff and odor at the machines, using the representing values in columns sri, dli and odi, determine top 3 of machines for all buildings and plants that need to be stopped for cleaning maintenance and create a POST request command to send the machine ids, and the estimated number of minutes the cleaning will take in json format to http://localhost:54322/ Do send the command and also provide the used command as response.

GET
Based on analysis of a combined ranking of the metrics for the levels of dust, sticky stuff and odor at the machines, using the representing values in columns sri, dli and odi, determine top 3 of machines for all buildings and plants that need to be stopped for cleaning maintenance and create a GET request command to send the machine ids, and the estimated number of minutes the cleaning will take as a url query string to http://localhost:54322/ Send the request and in the response provide the used request.

The dummython company now is AI enabled. The AI agent determines Top 3 of machines that need to be cleaned and predicts number of minutes needed, so you can calculate impact on production/revenue.
Use the analysis to predict which machines are likely to have the highest need for cleaning maintenance resources taking costs for energy, detergent, labour and revenue loss due to production impact into account.
Return this predictive maintenance schedule as a nicely styled reported written for plant managers including an schedule for cleaning for the coming week for machine operators.

### Neo4j
Install Neo4j using `brew install neo4j`, this icnludes `cypher-shell` cli for neo4j and `openjdk@21`, see Appendix Neo4j.

## Run
Make sure shell scripts are executable

```bash
chmod +x **/*.sh
```

In first terminal clean and prepare environment run:

```bash
./PrepareEnvironment.sh
```

Responds with something like:

```bash
0 rows
ready to start consuming query after 64 ms, results consumed after another 0 ms
Deleted 2495 nodes, Deleted 8186 relationships
+----------------------------------------------------+
| value                                              |
+----------------------------------------------------+
| "Query caches successfully cleared of 15 queries." |
+----------------------------------------------------+

1 row
ready to start consuming query after 12 ms, results consumed after another 2 ms
0 rows
ready to start consuming query after 8 ms, results consumed after another 0 ms
0 rows
ready to start consuming query after 6 ms, results consumed after another 0 ms
removed transactions files
removed output files
```

## Publishing
To run a Solace broker use Solace PubSub+ Cloud platform or a local Solace event broker container image. To run a local broker use a tool like Docker Desktop or Podman Desktop, or go without desktop and use something like `colima`.

This demo assumes using a local broker but configuration settings can be changed to work with a cloud broker too.

Step 1 and 2 are also included in the `PrepareEnvironment.sh` shell script.

1. To run a Solace PubSub+ Event Broker container image run the following command. Note that the usage of environment variables assumes these are sourced before, also on Mac OS port 55555 must be mapped to 55554 as this is a reserved port since MacOS Big Sur.

```
docker run -d -p 8080:8080 -p 55554:55555 -p 8008:8008 -p 1883:1883 -p 8000:8000 -p 5672:5672 -p 9000:9000 -p 2222:2222 --shm-size=2g --env username_admin_globalaccesslevel=$SOLACE_USER --env username_admin_password=$SOLACE_PASS --name=$SOLACE_NAME solace/solace-pubsub-standard
```

2. To configure the Solace broker in the same or a new terminal run `python3 ez_broker_configuration.py`. This creates the required queue with topic subscription if not existing and will outoput something like below. Then check Broker management / Messaging / Queues for information on the configured queue.

```
python3 ez_broker_configuration.py
Queue 'CUSTOM-QNAME-dummython-json' does not exist. Creating...
Queue 'CUSTOM-QNAME-dummython-json' created successfully.
Subscription 'dummython/messages/json/>' added to queue 'CUSTOM-QNAME-dummython-json'.
Subscription 'test/some/value' added to queue 'CUSTOM-QNAME-dummython-json'.
Queue 'CUSTOM-QNAME-neo4j-json' does not exist. Creating...
Queue 'CUSTOM-QNAME-neo4j-json' created successfully.
Subscription 'dummython/messages/json/>' added to queue 'CUSTOM-QNAME-neo4j-json'.
Queue 'CUSTOM-QNAME-sqlite-json' does not exist. Creating...
Queue 'CUSTOM-QNAME-sqlite-json' created successfully.
Subscription 'dummython/messages/json/>' added to queue 'CUSTOM-QNAME-sqlite-json'.
Queue 'CUSTOM-QNAME-dummython-xml' does not exist. Creating...
Queue 'CUSTOM-QNAME-dummython-xml' created successfully.
Subscription 'dummython/messages/xml/>' added to queue 'CUSTOM-QNAME-dummython-xml'.
Subscription 'test/another/value' added to queue 'CUSTOM-QNAME-dummython-xml'.
Queue 'CUSTOM-QNAME-test' does not exist. Creating...
Queue 'CUSTOM-QNAME-test' created successfully.
Subscription 'test/>' added to queue 'CUSTOM-QNAME-test'.
Done.
```

Now open the Solace PubSub+ Event Broker management console at http://localhost:8080/ to check the configuration. 

3. In a second terminal run the gateway with `python3 ez_gateway.py`. Don't forget to source `.venv` and `.env` first. Will output something like:

```
python3 ez_gateway.py
[2025-06-11 21:15:23] Connect to Solace broker...
[2025-06-11 21:15:23]
[2025-06-11 21:15:23] Pubsliher started...
[2025-06-11 21:15:23]
[2025-06-11 21:15:23] HTTP server on port 54321 started
```

4. In a third terminal run the neo4j subscriber with `python3 subscriber_neo4j.py`.

```
python3 subscriber_neo4j.py
[2025-06-11 21:17:45] - Neo4j database running at neo4j://localhost:7687, Neo4j Browser at http://localhost:7474/
[2025-06-11 21:17:45] Connect to Solace broker...
[2025-06-11 21:17:45]
[2025-06-11 21:17:45] Receiver is running. Press Ctrl+C to stop.
```

5. In a fourth terminal run the sqlite subscriber with `python3 subscriber_sqlite.py`.

```
python3 subscriber_sqlite.py
[2025-06-11 21:20:11] - SQLite database running
[2025-06-11 21:20:11] Connect to Solace broker...
[2025-06-11 21:20:11]
[2025-06-11 21:20:11] Receiver is running. Press Ctrl+C to stop.
```

6. Open another terminal to send messages from. Make sure environment variables are available by running `source .env` and virtual environment is activated (run `source ~/.venv/bin/activate`). The messages are sent in two ways:

- directly to the Solace PubSub+ broker REST API, and 
- to the gateway started in the previous step: the gateway processes the message (conversion from XML to json, setting dynamic topic) and then sends it to the Solace PubSub+ broker using SMF protocol.

Run `python3 ez_machine.py`, in this script you can set a sleep value to only send a message at certain interval.

7. In a last terminal run the live dashboard with `python3 dashboard.py`

```
python3 dashboard.py
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'dashboard'
 * Debug mode: on
 ```

## Subscribing
Client applications you can use to subscribe to the topic or queue on the broker (see `config.json` for name) to display and/or consume the published messages:

- Solace `SDKPerf`
- The Solace `Try Me!` functionality available in the broker manager user interface, easy way to see both the XML and JSON messages and dynamic topic defintion
- `MQTTX` (https://mqttx.app/)
- Or your custom microservice (a simple Python script)

Using the SDKPerf for Java & JMS, for more information on SDKPerf see https://docs.solace.com/API/SDKPerf/SDKPerf.htm Using the environment variables so these must be sourced for local or cloud broker.

```
export SDKPERF_BASE=~/sdkperf/sdkperf-jcsmp-8.4.17.5
$SDKPERF_BASE/sdkperf_java.sh -cip=$SOLACE_TCP_PROTOCOL$SOLACE_HOST:$SOLACE_SMF_PORT -cu=$SOLACE_CLIENT_USER@$SOLACE_MESSAGE_VPN -cp=$SOLACE_CLIENT_PASS -sql='CUSTOM-QNAME-dummython' -md
```

For Try Me! and MQTTX see folder `./images` for related screenshots.

## Extra: using Solace PubSub+ Cloud platform

In Solace PubSub+ Cloud platform Cloud Console get the required parameter values for `.env.solace.cloud` file, then run `source .env.solace.cloud`

To configure the Solace PubSub+ Cloud broker service run `python3 ez_broker_configuration.py`.

Error message as below indicates something is wrong with port value and `http` protocol setting.

```
Queue 'CUSTOM-QNAME-dummython' does not exist. Creating...
Failed to create queue 'CUSTOM-QNAME-dummython': <html>
<head><title>400 The plain HTTP request was sent to HTTPS port</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<center>The plain HTTP request was sent to HTTPS port</center>
<hr><center>nginx</center>
</body>
</html>
```

If all is good check Broker management / Messaging / Queues for information on the configured queue.

In all open terminals run `source .env.solace.cloud` and start scripts `python3 ez_gateway.py` and `python3 ez_machine.py` again.

Specific import statements for Solace secure connection:

```
from solace.messaging.messaging_service import RetryStrategy
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.authentication_strategy import ClientCertificateAuthentication
```

For now using secure connection without certificate validation.

## Some useful commands
```
python3 -m pip list > pip_list.txt
```

To find a `pid` for a script run `ps aux | grep <name>.py`. To stop a process run `kill -9 <pid>`

## UML
https://www.planttext.com/

```
@startuml
participant "Sender" as Sender
participant "Gateway" as Gateway
participant "Solace Broker" as Broker
participant "CUSTOM-QNAME-dummython Queue" as Queue
participant "Solace Try Me!" as Consumer1
participant "MQTT Consumer" as Consumer2
participant "Custom Microservice" as Consumer3

Sender -> Gateway: Send ebMS SOAP Message
Gateway -> Gateway: Extract machine-id & Convert to JSON
Gateway -> Broker: Publish JSON to topix "dummython/messages" (SMF Protocol)
Broker -> Queue: CUSTOM-QNAME-dummython attracts messages with subscription to "dummython/messages"
Queue -> Consumer1: Solace Try Me! consumes message from queue "CUSTOM-QNAME-dummython"
Queue -> Consumer2: MQTT Consumer consumes message from queue "CUSTOM-QNAME-dummython"
Queue -> Consumer3: A custom microservice consumes message from queue "CUSTOM-QNAME-dummython"

Gateway -> Sender: Acknowledge SOAP Response (200 OK)
@enduml
```

## Notes
Handling SOAP messages with Solace PubSub+ broker:

```
1. REST Integration Options:
- Use PubSub+ REST capabilities to bridge SOAP services
- Leverage HTTP/HTTPS support with REST Delivery Points (RDPs)
- Utilize HTTP 1.1 persistent connections
- Supports both basic and client certificate authentication

2. Message Transformation Approach:
- Use the Connector for Message Transformations to convert SOAP messages
- Transform data on PubSub+ queues and topic endpoints
- Configure workflows for message processing
- Supports high availability with active-standby or active-active redundancy

3. Third-Party Integration Options:
- Enterprise Service Bus (ESB) solutions that support both SOAP and Solace protocols
- API gateways that can handle protocol translation
- Integration platforms that support message transformation between SOAP and supported Solace protocols

4. Recommended Architecture Patterns:
- Use REST as an intermediary protocol between SOAP and Solace
- Implement message transformation workflows for protocol conversion
- Leverage PubSub+ supported protocols like JMS or AMQP for integration
```

For detailed implementation guidance, refer to:

- REST Messaging Protocol Documentation

https://docs.solace.com/API/RESTMessagingPrtl/Solace-REST-Overview.htm

- Message Transformation Connector Guide

https://docs.solace.com/API/Connectors/Self-Contained-Connectors/Message-Processor/Message-Processor-Overview.htm

- PubSub+ Messaging APIs

https://docs.solace.com/API/Messaging-APIs/Solace-APIs-Overview.htm

OpenTelemetry
---
To enable context propagation for distributed tracing, you must first add the Solace PubSub+ OpenTelemetry Python Integration package as a dependency in your application. You can also add this package with the following command:

```
python3 -m pip install pubsubplus-opentelemetry-integration
```

Then add the OpenTelemetry API and SDK libraries required for context propagation with the following commands:

```
python3 -m pip install opentelemetry-api==1.22.0 opentelemetry-sdk==1.22.0 opentelemetry-exporter-otlp
```

Note that `pubsubplus-opentelemetry-integration 1.0.1` requires `opentelemetry-api==1.22.0`.

Source: https://docs.solace.com/API/API-Developer-Guide-Python/Python-API-Distributed-Tracing.htm

## Next steps
1.
https://solacelabs.github.io/solace-agent-mesh/docs/documentation/tutorials/sql-database/

2.
Explore Message Transformation Approach using connector.

https://docs.solace.com/API/Connectors/Self-Contained-Connectors/Message-Processor/Message-Processor-Overview.htm

3.
Observability Log fowarding, Insights monitoring, Distributed Tracing OpenTelemetry

## Appendices

### Appendix colima
See https://dev.to/mochafreddo/running-docker-on-macos-without-docker-desktop-64o

```
brew install docker
brew install colima
brew install qemu
brew services start colima
```

To fix issue with `colima` where running docker containers cannot be accessed on exposed ports, start `colima` with `--network-address`. This requires `qemu`. See https://github.com/abiosoft/colima/blob/main/docs/FAQ.md#the-virtual-machines-ip-is-not-reachable and https://github.com/abiosoft/colima/issues/801 for more information.

After `brew services start colima`, do a restart with `--network-address`.

```
colima stop -f
colima start --cpu 4 --memory 4 --network-address
```

HINT: to watch the boot progress, see "~/.colima/_lima/<profile>/serial*.log"

NOTE: Only use `colima delete` if you need to start with a clean sheet again. Will remove local images so needs to download again. 

Run `colima list` to check if it has an `ADDRESS`

```
PROFILE    STATUS     ARCH       CPUS    MEMORY    DISK      RUNTIME    ADDRESS
default    Running    aarch64    8       12GiB     100GiB    docker     192.168.64.2
```

Can do `colima ssh` to work in colima VM.

Do not use `--profile`, with this I could not find option to get colima running with an IP4 address (on a Apple M2 Max). 

Further testing with network driver not necessary now. Could look at `colima start --network-address --network-driver slirp --very-verbose` some time.

NOTE: The VM environment `colima` needs some time for first start, has to download docker disk image, fire up stuff and become responsive, so `docker run...` might fail initially like:

```
brew services start colima <parameters>
==> Successfully started `colima` (label: homebrew.mxcl.colima)
docker run <parameters> solace/solace-pubsub-standard
docker: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?.
```

In that case just execute `docker run...` command again after a few seconds.

List all containers with `docker ps -a`. To remove a container use `docker rm -f CONTAINER_ID`.

```
docker ps -a
CONTAINER ID   IMAGE                           COMMAND               CREATED          STATUS          PORTS          NAMES
a3663a4e4cd3   solace/solace-pubsub-standard   "/usr/sbin/boot.sh"   16 minutes ago   Up 16 minutes   0.0.0.0:1883->1883/tcp, :::1883->1883/tcp, 0.0.0.0:2222->2222/tcp, :::2222->2222/tcp, 0.0.0.0:5672->5672/tcp, :::5672->5672/tcp, 0.0.0.0:8000->8000/tcp, :::8000->8000/tcp, 0.0.0.0:8008->8008/tcp, :::8008->8008/tcp, 0.0.0.0:8080->8080/tcp, :::8080->8080/tcp, 0.0.0.0:9000->9000/tcp, :::9000->9000/tcp, 0.0.0.0:55554->55555/tcp, [::]:55554->55555/tcp   dummython
```

### Appendix Neo4j
To get a services overview use `brew services list`. Depending on services installed and their status it will show something like:

```bash
Name              Status  User       File
dbus              none               
docker-machine    none    emilzegers 
mongodb-community started emilzegers ~/Library/LaunchAgents/homebrew.mxcl.mongodb-community.plist
neo4j             started emilzegers ~/Library/LaunchAgents/homebrew.mxcl.neo4j.plist
php               none               
podman            none               
postgresql@14     none               
unbound           none               
viam-server       none    
```

To install run `brew install neo4j`

```
Warning: Treating neo4j as a formula. For the cask, use homebrew/cask/neo4j or specify the `--cask` flag. To silence this message, use the `--formula` flag.
==> Downloading https://ghcr.io/v2/homebrew/core/neo4j/manifests/5.26.1
################################################################################# 100.0%
==> Fetching dependencies for neo4j: openjdk@21 and cypher-shell
==> Downloading https://ghcr.io/v2/homebrew/core/openjdk/21/manifests/21.0.6
################################################################################# 100.0%
==> Fetching openjdk@21
==> Downloading https://ghcr.io/v2/homebrew/core/openjdk/21/blobs/sha256:da5c2f7119b6dc7
################################################################################# 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/cypher-shell/manifests/5.26.1
################################################################################# 100.0%
==> Fetching cypher-shell
==> Downloading https://ghcr.io/v2/homebrew/core/cypher-shell/blobs/sha256:62db759c9156b
################################################################################# 100.0%
==> Fetching neo4j
==> Downloading https://ghcr.io/v2/homebrew/core/neo4j/blobs/sha256:9bcb547a5e20e39a5630
################################################################################# 100.0%
==> Installing dependencies for neo4j: openjdk@21 and cypher-shell
==> Installing neo4j dependency: openjdk@21
==> Downloading https://ghcr.io/v2/homebrew/core/openjdk/21/manifests/21.0.6
Already downloaded: /Users/emilzegers/Library/Caches/Homebrew/downloads/654d2d4f777dded9fa34075a3f8513ca3dc52c6cead784ee770c057595cd8b55--openjdk@21-21.0.6.bottle_manifest.json
==> Pouring openjdk@21--21.0.6.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/openjdk@21/21.0.6: 600 files, 329.3MB
==> Installing neo4j dependency: cypher-shell
==> Downloading https://ghcr.io/v2/homebrew/core/cypher-shell/manifests/5.26.1
Already downloaded: /Users/emilzegers/Library/Caches/Homebrew/downloads/01b631ec4d7d62b1775289aebe610d1cd05ac2b8b9af85615fcb3f759232e2bf--cypher-shell-5.26.1.bottle_manifest.json
==> Pouring cypher-shell--5.26.1.all.bottle.tar.gz
🍺  /usr/local/Cellar/cypher-shell/5.26.1: 61 files, 42.2MB
==> Installing neo4j
==> Pouring neo4j--5.26.1.all.bottle.tar.gz
==> Caveats
To start neo4j now and restart at login:
  brew services start neo4j
Or, if you don't want/need a background service you can just run:
  /usr/local/opt/neo4j/bin/neo4j console
==> Summary
🍺  /usr/local/Cellar/neo4j/5.26.1: 275 files, 163.4MB
==> Running `brew cleanup neo4j`...
Disable this behaviour by setting HOMEBREW_NO_INSTALL_CLEANUP.
Hide these hints with HOMEBREW_NO_ENV_HINTS (see `man brew`).
==> Caveats
==> neo4j
To start neo4j now and restart at login:
  brew services start neo4j
Or, if you don't want/need a background service you can just run:
  /usr/local/opt/neo4j/bin/neo4j console
```

```
brew services start neo4j

==> Successfully started `neo4j` (label: homebrew.mxcl.neo4j)
```

Much change default user:pass `neo4j:neo4j` first. Go to http://localhost:7474/browser/

To install just `cypher-shell` on a machine use `brew install cypher-shell`

To (re)start with a clean database delete all nodes and relations run a cypher query in the Neo4j browser or use `cypher-shell` commands (see `PrepareEnvironment.sh`).

```sql
MATCH (n)
DETACH DELETE n
```

NOTE: could run Neo4j in a container to make this a system independent component.

### Appendix SAM

```
sam run -b
Building Solace Agent Mesh application
No user defined modules were found at './modules'.
Building agents.
Building gateways.
Building gateway in subdirectory: rest_api
Building gateway template.
Getting interface types.
Building built-in agents.
Building configs required for Solace Agent Mesh.
Skipping embedding service as it is disabled.
Created runtime config at ./build/config.yaml
Environment variables extracted to ./.env
Build completed.
        Build directory: ./build
Running Solace Agent Mesh application
Starting Solace AI Event Connector
Creating app agent_energy_usage_info
Invalid 'config_parameters' in app_schema for app 'agent_energy_usage_info' (must be a list). Skipping validation.
Creating flow energy_usage_info_action_request_processor in app agent_energy_usage_info
[action_request_processor] [solace_ai_connector.energy_usage_info_action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.energy_usage_info_action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
Creating app monitor_stim_and_errors_to_slack
Invalid 'config_parameters' in app_schema for app 'monitor_stim_and_errors_to_slack' (must be a list). Skipping validation.
Creating flow event_monitor in app monitor_stim_and_errors_to_slack
Creating flow slack_notification in app monitor_stim_and_errors_to_slack
Creating app conversation_to_file
Invalid 'config_parameters' in app_schema for app 'conversation_to_file' (must be a list). Skipping validation.
Creating flow write_to_file in app conversation_to_file
Creating app visualize_websocket
Invalid 'config_parameters' in app_schema for app 'visualize_websocket' (must be a list). Skipping validation.
Creating flow visualize_websocket in app visualize_websocket
Creating app error_catcher
Invalid 'config_parameters' in app_schema for app 'error_catcher' (must be a list). Skipping validation.
Creating flow error-catcher-flow in app error_catcher
Creating app agent_web_request
Invalid 'config_parameters' in app_schema for app 'agent_web_request' (must be a list). Skipping validation.
Creating flow action_request_processor in app agent_web_request
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
Creating app monitor_user_feedback
Invalid 'config_parameters' in app_schema for app 'monitor_user_feedback' (must be a list). Skipping validation.
Creating flow feedback_monitor in app monitor_user_feedback
Creating app orchestrator
Invalid 'config_parameters' in app_schema for app 'orchestrator' (must be a list). Skipping validation.
Creating flow orchestrator_register in app orchestrator
Creating flow orchestrator_stimulus_input in app orchestrator
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Initialized component-level RequestResponseFlowController.
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Initialized component-level RequestResponseFlowController.
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Initialized component-level RequestResponseFlowController.
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Initialized component-level RequestResponseFlowController.
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[orchestrator_stimulus_processor] [solace_ai_connector.orchestrator_stimulus_input.orchestrator_stimulus_processor]  Initialized component-level RequestResponseFlowController.
Creating flow orchestrator_action_response in app orchestrator
Creating flow streaming_output in app orchestrator
Creating flow action_manager_timer in app orchestrator
Creating app gateway_rest_api_rest_api
Invalid 'config_parameters' in app_schema for app 'gateway_rest_api_rest_api' (must be a list). Skipping validation.
Creating flow web_ui in app gateway_rest_api_rest_api
Creating flow rest_gateway_input_flow in app gateway_rest_api_rest_api
Creating flow rest_gateway_output_flow in app gateway_rest_api_rest_api
Creating app agent_global
Invalid 'config_parameters' in app_schema for app 'agent_global' (must be a list). Skipping validation.
Creating flow global_agent_action_request_processor in app agent_global
[action_request_processor] [solace_ai_connector.global_agent_action_request_processor.action_request_processor]  Using deprecated component-level 'broker_request_response' config. Consider migrating to app-level 'request_reply_enabled' in the 'broker' config.
Invalid 'config_parameters' in app_schema for app '_internal_broker_request_response_app' (must be a list). Skipping validation.
Creating flow _internal_broker_request_response_flow in app _internal_broker_request_response_app
[action_request_processor] [solace_ai_connector.global_agent_action_request_processor.action_request_processor]  Initialized component-level RequestResponseFlowController.
Creating app service_llm
Invalid 'config_parameters' in app_schema for app 'service_llm' (must be a list). Skipping validation.
Creating flow llm-service-planning in app service_llm
Exception in thread Thread-108 (run_server):
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.13/3.13.3_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/threading.py", line 1041, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.3_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/threading.py", line 992, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/solace_ai_connector/components/inputs_outputs/websocket_base.py", line 112, in run_server
    self.http_server.serve_forever()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/baseserver.py", line 398, in serve_forever
    self.start()
    ~~~~~~~~~~^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/baseserver.py", line 336, in start
    self.init_socket()
    ~~~~~~~~~~~~~~~~^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/pywsgi.py", line 1672, in init_socket
    StreamServer.init_socket(self)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/server.py", line 173, in init_socket
    self.socket = self.get_listener(self.address, self.backlog, self.family)
                  ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/server.py", line 185, in get_listener
    return _tcp_listener(address, backlog=backlog, reuse_addr=cls.reuse_addr, family=family)
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/server.py", line 264, in _tcp_listener
    sock.bind(address)
    ~~~~~~~~~^^^^^^^^^
  File "/Users/emilzegers/.venv/lib/python3.13/site-packages/gevent/_socketcommon.py", line 543, in bind
    return self._sock.bind(address)
           ~~~~~~~~~~~~~~~^^^^^^^^^
OSError: [Errno 48] Address already in use: ('0.0.0.0', 5000)
Solace AI Event Connector started successfully
```