# cleanpulse
"Real-time insights for spotless performance". an application that focuses on reporting the cleaning activities of machines in a factory, including details such as the last cleaning time, duration, water usage, and energy usage. Relevant for CPG, like beer breweries and coffee-roasting factories.

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
`git clone https://github.com/taatuut/<todo>.git`

## Setup

### Python

Create and source a Python virtual environment, this demo use `~/.venv`.

Open a terminal and run:

```
mkdir -p ~/.venv
python3 -m venv ~/.venv
source ~/.venv/bin/activate
```

Install Python modules (optional: `upgrade pip`)

```
python3 -m pip install --upgrade pip
python3 -m pip install requests lxml solace-pubsubplus pyyaml pandas scikit-learn neo4j
```

### Neo4j
Install Neo4j using `brew install neo4j`, this icnludes `cypher-shell` cli for neo4j and `openjdk@21`, see Appendix Neo4j.

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

To (re)start with a clean database delete all nodes and relations run a cypher query in the Neo4j browser or use `cypher-shell` commands (see `PrepareEnvironment.sh`).

```sql
MATCH (n)
DETACH DELETE n
```

NOTE: could run Neo4j in a container to make this a system independent component.

### Sample data
File `./data/saml/SAML-D.zip` from https://www.kaggle.com/datasets/berkanoztas/synthetic-transaction-monitoring-dataset-aml

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
{ ok: 1, dropped: 'bank' }
{ ok: 1, dropped: 'bank' }
0 rows
ready to start consuming query after 348 ms, results consumed after another 0 ms
Deleted 1359 nodes, Deleted 2858 relationships
+----------------------------------------------------+
| value                                              |
+----------------------------------------------------+
| "Query caches successfully cleared of 11 queries." |
+----------------------------------------------------+

1 row
ready to start consuming query after 46 ms, results consumed after another 123 ms
0 rows
ready to start consuming query after 30 ms, results consumed after another 0 ms
+---------------------------------------------------+
| value                                             |
+---------------------------------------------------+
| "Query caches successfully cleared of 3 queries." |
+---------------------------------------------------+

1 row
ready to start consuming query after 18 ms, results consumed after another 3 ms
0 rows
ready to start consuming query after 28 ms, results consumed after another 0 ms
0 rows
ready to start consuming query after 9 ms, results consumed after another 0 ms
remove transactions
remove output
```

## Set environment variables
Check `sample.env` and copy/create `.env` with own values, then run:

```
source .env
```

Add relevant information to configuration file `config.json`.

## Publishing
To run a Solace broker use Solace PubSub+ Cloud platform or a local Solace event broker container image. To run a local broker use a tool like Docker Desktop or Podman Desktop, or go without desktop and use something like `colima`.

This demo assumes using a local broker but configuration settings can be changed to work with a cloud broker too. 

1. To run a Solace PubSub+ Event Broker container image run the following command. Note that the usage of environment variables assumes these are sourced before, also on Mac OS port 55555 must be mapped to 55554 as this is a reserved port since MacOS Big Sur.

```
docker run -d -p 8080:8080 -p 55554:55555 -p 8008:8008 -p 1883:1883 -p 8000:8000 -p 5672:5672 -p 9000:9000 -p 2222:2222 --shm-size=2g --env username_admin_globalaccesslevel=$SOLACE_USER --env username_admin_password=$SOLACE_PASS --name=$SOLACE_NAME solace/solace-pubsub-standard
```

2. To configure the Solace broker in tghe same or a new terminal run `python3 ez_broker_configuration.py`. This creates the required queue with topic subscription if not existing and will outoput something like below. Then check Broker management / Messaging / Queues for information on the configured queue.

```
python3 ez_broker_configuration.py
Queue 'CUSTOM-QNAME-dummython' does not exist. Creating...
Queue 'CUSTOM-QNAME-dummython' created successfully.
Subscription 'dummython/messages/>' added to queue 'CUSTOM-QNAME-dummython'.
Done.
```

Now open the Solace PubSub+ Event Broker management console at http://localhost:8080/ to check the configuration. 

3. In a second terminal run the gateway with `python3 dummython_gateway.py`. Don't forget to `source .env` first. Will output something like:

```
python3 dummython_gateway.py
[2025-06-03 09:54:39] Connect to Solace broker...
[2025-06-03 09:54:39] 
[2025-06-03 09:54:39] Pubsliher started...
[2025-06-03 09:54:39] 
[2025-06-03 09:54:39] - SQLite database running in memory
[2025-06-03 09:54:39] - Neo4j database running at neo4j://localhost:7687, Neo4j Browser at http://localhost:7474/
[2025-06-03 09:54:39] HTTP server on port 54321 started
```

4. Open a third terminal to send messages from. Make sure environment variables are available by running `source .env` and virtual environment is activated (run `source ~/.venv/bin/activate`). The messages are sent in two ways:

- directly to the Solace PubSub+ broker REST API, and 
- to the gateway started in the previous step: the gateway processes the message (conversion from XML to json, setting dynamic topic) and then sends it to the Solace PubSub+ broker using SMF protocol.

To execute once run `python3 dummythonSoapSender.py`, or run repeatedly every five seconds with `while true; do python3 dummythonSoapSender.py; sleep 5; done`

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

In all open terminals run `source .env.solace.cloud` and start scripts `python3 dummython_gateway.py` and `while true; do python3 dummythonSoapSender.py; sleep 5; done` again.

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
Explore Message Transformation Approach using connector.

https://docs.solace.com/API/Connectors/Self-Contained-Connectors/Message-Processor/Message-Processor-Overview.htm

2.
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
`brew install neo4j`

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
