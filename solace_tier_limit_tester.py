import threading
import time
import os
import logging
import sys
# solace
from solace.messaging.messaging_service import MessagingService, RetryStrategy
from solace.messaging.config.transport_security_strategy import TLS

# Configuration
# NOTE: environment variables must be sourced in advance
# Solace broker connection settings
SOLACE_MESSAGE_VPN = os.environ["SOLACE_MESSAGE_VPN"]
SOLACE_CLIENT_USER = os.environ["SOLACE_CLIENT_USER"]
SOLACE_CLIENT_PASS = os.environ["SOLACE_CLIENT_PASS"]
SOLACE_HOST = os.environ["SOLACE_HOST"]
SOLACE_SMF_PORT = os.environ["SOLACE_SMF_PORT"]
SOLACE_TRUSTSTORE_PEM = os.environ["SOLACE_TRUSTSTORE_PEM"]

SOLACE_TCP_PROTOCOL = os.environ["SOLACE_TCP_PROTOCOL"]

args = sys.argv[1:]  # skip the script name
# print(f"Received arguments: {args}")
# for arg in args:
#     print(f"Processing argument: {arg}")
# Set the number of concurrent connections to create (1, 11, 101, 251, 999, 1000, 1001, ...) defaults to 10
NUM_CONNECTIONS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 10
active_connections = []
lock = threading.Lock()

def maintain_connection(index):
    global active_connections

    broker_props = {
        "solace.messaging.transport.host": f"{SOLACE_TCP_PROTOCOL}{SOLACE_HOST}:{SOLACE_SMF_PORT}",
        "solace.messaging.service.vpn-name": SOLACE_MESSAGE_VPN,
        "solace.messaging.authentication.scheme.basic.username": SOLACE_CLIENT_USER,
        "solace.messaging.authentication.scheme.basic.password": SOLACE_CLIENT_PASS,
    }

    try:
        if SOLACE_TCP_PROTOCOL == 'tcp://':
            # Initialize Solace Messaging Service
            messaging_service = (
                MessagingService.builder()
                .from_properties(broker_props)
                .build()
            )
        else:
            # In case of secure connection, still without certificate validation...
            transport_security_strategy = TLS.create().without_certificate_validation() # TLS.create().with_certificate_validation(True, validate_server_name=False, trust_store_file_path=f"{SOLACE_TRUSTSTORE_PEM}")
            messaging_service = (
                MessagingService.builder()
                .from_properties(broker_props)
                .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20,3))
                .with_transport_security_strategy(transport_security_strategy)
                .build()   
            )
        messaging_service.connect()
        with lock:
            active_connections.append(messaging_service)
            print(f"[✓] Connection {index} established. Total active: {len(active_connections)}")

        # Keep the thread alive to maintain the connection
        while messaging_service.is_connected:
            time.sleep(1)

    except Exception as e:
        print(f"[✗] Connection {index} failed: {e}")
        #pass

# Set Solace logging level to ERROR to avoid lots of WARNING messages with connect
logging.getLogger("solace.messaging.core").setLevel(logging.ERROR)

# Launch connections
threads = []

for i in range(NUM_CONNECTIONS):
    t = threading.Thread(target=maintain_connection, args=(i,), daemon=True)
    threads.append(t)
    sleepytime = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else .1
    time.sleep(sleepytime)
    t.start()

# Monitor thread
try:
    while True:
        time.sleep(10)
        with lock:
            print(f"[INFO] {len(active_connections)} active connections being maintained.")
except KeyboardInterrupt:
    print("\n[INFO] Shutting down...")

"""
https://solacedotcom.slack.com/archives/C627M1NKA/p1729584577368259

Assign more resources to colima service

colima stop -f
colima start --cpu 6 --memory 18 --network-address

docker run -d -p 8080:8080 -p 55554:55555 -p 8008:8008 -p 1883:1883 -p 8000:8000 -p 5672:5672 -p 9000:9000 -p 2222:2222 --shm-size=8g --env username_admin_globalaccesslevel=$SOLACE_USER --env username_admin_password=$SOLACE_PASS --env system_scaling_maxconnectioncount=1000 --env system_scaling_maxqueuemessagecount=240 --env system_scaling_maxkafkabridgecount=0 --env system_scaling_maxkafkabrokerconnectioncount=0 --env system_scaling_maxsubscriptioncount=500000  --env messagespool_maxspoolusage=10000 --name=$SOLACE_NAME solace/solace-pubsub-standard

Note the --shm-size value

solace-pubsub-enterprise:latest


2025-06-13 16:46:10,038 [WARNING] solace.messaging.core: [_solace_transport.py:89]  [[SERVICE: 0x10816fd90] - [APP ID: ezSolace.local/41741/01520001/0Hc_FB-Lrz]] {'caller_description': 'From service event callback', 'return_code': 'Ok', 'sub_code': 'SOLCLIENT_SUBCODE_COMMUNICATION_ERROR', 'error_info_sub_code': 14, 'error_info_contents': 'TCP connection failure for fd 1022, error = Connection refused (61)'}
[✓] Connection 339 established. Total active: 339

Suppress warnings by setting logger level

2025-06-13 16:46:10,131 [WARNING] solace.messaging.core: [_solace_session.py:321]  [SolaceApiContext Id: 0x10844cde0] Failed to create solace context
Caller Description: SolaceApiContext->init. Error Info Sub code: [13]. Error: [Could not create write socket for internal CMD pipe, type 2, protocol 17, error = Unexpected error 0. Caller may not be thread safe]. Sub code: [SOLCLIENT_SUBCODE_OS_ERROR]. Return code: [Fail]

'Solve' FDs issue by running multiple instances of Python script

2025-06-14 13:14:42,833 [WARNING] solace.messaging.connections: [messaging_service.py:1262]  [[SERVICE: 0x110944d50] - [APP ID: ezSolace.local/10265/01320001/NdCngUOWiw]] Connection failed. Status code: -1
[✗] Connection 306 failed: {'caller_description': 'do_connect', 'return_code': 'Fail', 'sub_code': 'SOLCLIENT_SUBCODE_OUT_OF_RESOURCES', 'error_info_sub_code': 5, 'error_info_contents': 'Too many FDs opened for events for context 306, fd# = 1025'}

Going to/over 1000 connections by running multiple instances of script, e.g. three with 332-333 connections crashes broker and container and colima
Runs stable up to 998 (includes one internal connection), nummer 999 connects but then everythign goes down.

When running in iTerm2 check ulimit, apparently set to 256 default. Set with ulimit -n 65535
"""