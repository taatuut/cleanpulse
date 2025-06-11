# general
import json
import os
import uuid
import time
# solace
from solace.messaging.messaging_service import MessagingService, RetryStrategy
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.resources.queue import Queue
from solace.messaging.receiver.inbound_message import InboundMessage
from solace.messaging.config.transport_security_strategy import TLS
# neo4j
from neo4j import GraphDatabase
# ez
from ez_config_loader import ConfigLoader

def insert_transaction(transaction_json, neo4j_driver):
    """Insert transaction into Neo4j."""
    transaction = json.loads(transaction_json)

    # Insert into Neo4j
    with neo4j_driver.session() as session:
        #tprint(transaction)
        session.execute_write(create_graph, transaction)
        tprint("Inserted transaction into Neo4j.")
        pass

def create_graph(tx, transaction):
    """Create nodes and relationships in Neo4j."""
    query = """
    MERGE (pi:PlantID {dt: $plant_id})
    MERGE (bi:BuildingID {dt: $building_id})
    MERGE (mi:MachineID {dt: $machine_id})
    MERGE (cp:CpaID {dt: $cpaid})
    MERGE (cid:ConversationID {dt: $conversationid})
    MERGE (s:Service {dt: $service})
    MERGE (a:Action {dt: $action})
    MERGE (dl:DustLevel {dt: $dust})
    MERGE (sr:StickyResidu {dt: $sticky})
    MERGE (od:Odor {dt: $odor})
    MERGE (p:payload {dt: $payload, timestamp: datetime($timestamp)})
    MERGE (pi)-[:HAS_CID]->(cid)
    MERGE (pi)-[:LOCATES]->(bi)
    MERGE (pi)-[:HAS_CPA]->(cp)
    MERGE (bi)-[:HAS_CID]->(cid)
    MERGE (bi)-[:HAS]->(mi)
    MERGE (bi)-[:HAS_SERVICE]->(s)
    MERGE (mi)-[:HAS_CID]->(cid)
    MERGE (mi)-[:HAS_PAYLOAD]->(p)
    MERGE (mi)-[:HAS_ACTION]->(a)
    MERGE (mi)-[:HAS_DUSTLEVEL]->(dl)
    MERGE (mi)-[:HAS_STICKYRESIDU]->(sr)
    MERGE (mi)-[:HAS_ODOR]->(od)
    MERGE (mi)-[:NEEDS_CLEANING]->(od)
    """
    transaction['txid'] = str(uuid.uuid4())
    tx.run(query, **transaction)

def initialize_neo4j():
    """Initialize Neo4j database connection."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def tprint(string=""):
    """Takes a string and prints it with a timestamp prefixt."""
    print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"), string))

def process_and_store(message: InboundMessage):
    data = message.get_payload_as_string()
    insert_transaction(data, neo4j_driver)

if __name__ == "__main__":
    # Load values from the configuration
    config = ConfigLoader("config.json")
    APP_TOPIC = config.get("app.topic")
    # Only print, write etc in debug modus, using config variable
    APP_DEBUG = config.get("app.debug")

    # NOTE: environment variables must be sourced in advance
    # Solace broker connection settings
    SOLACE_MESSAGE_VPN = os.environ["SOLACE_MESSAGE_VPN"]
    SOLACE_CLIENT_USER = os.environ["SOLACE_CLIENT_USER"]
    SOLACE_CLIENT_PASS = os.environ["SOLACE_CLIENT_PASS"]
    SOLACE_HOST = os.environ["SOLACE_HOST"]
    SOLACE_SMF_PORT = os.environ["SOLACE_SMF_PORT"]
    SOLACE_TRUSTSTORE_PEM = os.environ["SOLACE_TRUSTSTORE_PEM"]

    SOLACE_TCP_PROTOCOL = os.environ["SOLACE_TCP_PROTOCOL"]

    NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
    NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
    NEO4J_URI = os.environ["NEO4J_URI"]
    NEO4J_CONSOLE = os.environ["NEO4J_CONSOLE"]

    # Initialize Neo4j database
    try:
        neo4j_driver = initialize_neo4j()
        neo4j_driver.verify_connectivity()
        tprint(f"- Neo4j database running at {NEO4J_URI}, Neo4j Browser at {NEO4J_CONSOLE}")
    except Exception as e:
        tprint(f"- Neo4j database not connected: {e}")
        quit()

    broker_props = {
        "solace.messaging.transport.host": f"{SOLACE_TCP_PROTOCOL}{SOLACE_HOST}:{SOLACE_SMF_PORT}",
        "solace.messaging.service.vpn-name": SOLACE_MESSAGE_VPN,
        "solace.messaging.authentication.scheme.basic.username": SOLACE_CLIENT_USER,
        "solace.messaging.authentication.scheme.basic.password": SOLACE_CLIENT_PASS,
        #"solace.messaging.tls.trust-store-path": SOLACE_TRUSTSTORE_PEM
    }

    if SOLACE_TCP_PROTOCOL == 'tcp://': # TODO: sloppy... replace with proper check/setup (as in other repo)
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
            #.with_authentication_strategy(ClientCertificateAuthentication.of(certificate_file=f"{SOLACE_TRUSTSTORE_PEM}",key_file="key_file",key_password="key_store_password"))
            .build()   
        )
    
    # Connect to Solace broker
    messaging_service.connect()
    tprint("Connect to Solace broker...")
    tprint()
    # Create messsage handler
    class MyMessageHandler(MessageHandler):
        def __init__(self, processor_func):
            self.processor_func = processor_func

        def on_message(self, message):
            self.processor_func(message)

    try:
        # Create queue receiver
        QUEUE_NAME = 'CUSTOM-QNAME-dummython-json' # TODO: get from config
        queue = Queue.durable_exclusive_queue(QUEUE_NAME) 
        receiver = messaging_service.create_persistent_message_receiver_builder().build(queue)
        receiver.start()
        handler = MyMessageHandler(process_and_store)
        receiver.receive_async(handler)
        print("Receiver is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)  # Keeps the main thread alive
    except KeyboardInterrupt:
        print("Shutting down...")
        receiver.terminate()
        messaging_service.disconnect()
