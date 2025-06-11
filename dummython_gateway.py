# general
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import xml.etree.ElementTree as ET
import time
import re
# solace
from solace.messaging.messaging_service import MessagingService, RetryStrategy
from solace.messaging.resources.topic import Topic
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.authentication_strategy import ClientCertificateAuthentication
# ez
from ez_config_loader import ConfigLoader
from ez_opentelemetry import *

def tprint(string=""):
    """Takes a string and prints it with a timestamp prefixt."""
    print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"), string))

def extract_soap_data(soap_xml):
    """Extracts machine-id and body content from SOAP XML."""
    unk = "Unknown"
    try:
        root = ET.fromstring(soap_xml)
        plant_id = root.find(".//plant-id")
        building_id = root.find(".//building-id")
        machine_id = root.find(".//machine-id")
        dli = root.find(".//dli")
        sri = root.find(".//sri")
        odi = root.find(".//odi")
        payload = root.find(".//Content")
        match = re.search(r"\[(.*?)\] Dust level: (\w+), Sticky residue: (\w+), Odor: (\w+)\. Cleaning: ([\w\s]+)\.", ET.tostring(payload, encoding='unicode'))
        if match:
            timestamp, dust, sticky, odor, cleaning = match.groups()
        else:
            timestamp, dust, sticky, odor, cleaning = unk
        # Create dynamic topic using APP_TOPIC as root based on incoming SOAP message properties
        # Not so ok to have namespsaces and elements hardcoded even though this is a dedicated gateway script...
        namespaces = {'dt': 'http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd'} # add more as needed
        cpaid = root.find('.//dt:CPAId', namespaces)
        conversationid = root.find('.//dt:ConversationId', namespaces)
        service = root.find('.//dt:Service', namespaces)
        action = root.find('.//dt:Action', namespaces)
        return (
            plant_id.text if plant_id is not None else unk,
            building_id.text if building_id is not None else unk,
            machine_id.text if machine_id is not None else unk,
            payload.text if payload is not None else unk,
            cpaid.text if cpaid is not None else unk,
            conversationid.text if conversationid is not None else unk,
            service.text if service is not None else unk,
            action.text if action is not None else unk,
            timestamp,
            dust,
            sticky,
            odor,
            cleaning,
            dli.text if dli is not None else unk,
            sri.text if sri is not None else unk,
            odi.text if odi is not None else unk
        )
    except ET.ParseError:
        return unk, ""

class SOAPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        plant_id, building_id, machine_id, payload, cpaid, conversationid, service, action, timestamp, dust, sticky, odor, cleaning, dli, sri, odi = extract_soap_data(post_data)
        json_message = json.dumps({
            "plant_id": plant_id,
            "building_id": building_id + plant_id,
            "machine_id": machine_id + building_id + plant_id,
            "payload": payload,
            "cpaid": cpaid,
            "conversationid": conversationid,
            "service": service,
            "action": action,
            "timestamp": timestamp,
            "dust": dust,
            "sticky": sticky,
            "odor": odor,
            "cleaning": cleaning,
            "dli": dli,
            "sri": sri,
            "odi": odi
        })

        # NOTE: conversationid now contains combined value of {plant_id}/{building_id}/{machine_id}
        topic = (
            f"{APP_TOPIC}/json/v1/"
            f"{conversationid}/{cpaid}/{service}/{action}/"
            f"{dust}/{sticky}/{odor}/{cleaning}"
        )        
        topic_dest = Topic.of(topic)
        if publish_to_solace(topic_dest, json_message):
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.end_headers()
            response_xml = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                <soapenv:Body>
                    <Response>
                        <Message>Message acknowledged</Message>
                        <machine-id>{machine_id}</machine-id>
                        <cleaning>{cleaning}</cleaning>
                    </Response>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            self.wfile.write(response_xml.encode('utf-8'))
        else:
            self.send_response(500)
            self.end_headers()

def publish_to_solace(topic, message):
    """Publishes message to Solace broker using SMF protocol."""
    try:
        # Publish message
        publisher.publish(message, topic)
        return True
    except Exception as e:
        tprint(f"Error publishing to Solace: {e}")
        return False

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
    # Create publisher
    publisher = messaging_service.create_persistent_message_publisher_builder().build()
    publisher.start()
    tprint("Pubsliher started...")
    tprint()

    # Start HTTP server
    try:
        tprint("HTTP server on port 54321 started")
        server_address = ('localhost', 54321)
        httpd = HTTPServer(server_address, SOAPRequestHandler)
        httpd.serve_forever()
    except Exception as e:
        tprint(f"- HTTP server  not started: {e}")
        quit()
