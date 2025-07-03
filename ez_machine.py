# general
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import uuid
import random
import datetime
import time
import threading
from urllib.parse import urlparse, parse_qs
# ez
from ez_config_loader import ConfigLoader

def tprint(string=""):
    """Takes a string and prints it with a timestamp prefixt."""
    print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"), string))

def generate_uuid():
    return str(uuid.uuid4())

def getCPA():
    return random.choice(['cpa123456', 'cpa23456', 'cpa86420', 'cpa98765'])
def getService():
    return random.choice(['urn:services:SupplierOrderProcessing', 'urn:services:QuoteToCollect'])
def getAction():
    return random.choice(['NewPurchaseOrder', 'NewOrder', 'PurchaseOrderResponse'])

def create_soap_message(plant_id, building_id, machine_id, payload, dli, sri, odi):
    # Define the SOAP envelope with headers and payload
    soap_env = f'''
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:dt="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd">
        <soapenv:Header>
            <dt:MessageHeader soapenv:mustUnderstand="1" dt:version="2.0">
                <dt:From>
                    <dt:PartyId>urn:example:sender</dt:PartyId>
                </dt:From>
                <dt:To>
                    <dt:PartyId>urn:example:receiver</dt:PartyId>
                </dt:To>
                <dt:CPAId>{getCPA()}</dt:CPAId>
                <dt:ConversationId>{plant_id}/{building_id}/{machine_id}</dt:ConversationId>
                <dt:Service>{getService()}</dt:Service>
                <dt:Action>{getAction()}</dt:Action>
                <dt:MessageData>
                    <dt:MessageId>{generate_uuid()}</dt:MessageId>
                    <dt:Timestamp>{datetime.datetime.now().isoformat()}</dt:Timestamp>
                </dt:MessageData>
            </dt:MessageHeader>
        </soapenv:Header>
        <soapenv:Body>
            <dt:Manifest>
                <dt:Reference xlink:href="cid:{machine_id}" xmlns:xlink="http://www.w3.org/1999/xlink"/>
            </dt:Manifest>
            <Payload>
                <Document>
                    <plant-id>{plant_id}</plant-id>
                    <building-id>{building_id}</building-id>
                    <machine-id>{machine_id}</machine-id>
                    <dli>{dli}</dli>
                    <sri>{sri}</sri>
                    <odi>{odi}</odi>
                    <Content>{payload}</Content>
                </Document>
            </Payload>
        </soapenv:Body>
    </soapenv:Envelope>
    '''
    return soap_env

def send_message(url, message, machine_id):
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'ebMS',
        'machine-id': machine_id
    }
    try:
        response = requests.post(url, data=message, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None

class SOAPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        tprint(post_data)
        return

    def do_GET(self):
        # Parse URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        # Prepare response
        self.send_response(200)
        self.end_headers()
        response = f"{query_params}".encode()
        self.wfile.write(response)
        tprint(query_params)

def main():
    # TODO: get ranges from config.json
    plant_id = 'plant' + str(random.randint(1, 3)) # 1-5
    building_id = 'building' + str(random.randint(1, 2)) # 1-20
    machine_id = 'machine' + str(random.randint(1, 4)) # 1-10
    d={'low':20,'moderate':80,'high':120}
    s={'minimal':30,'present':70,'excessive':110}
    o={'normal':10,'noticeable':60,'strong':100}
    dl = random.choices(list(d),weights=[60,30,10])[0]
    dli = d[dl]
    sr = random.choices(list(s),weights=[50,35,15])[0]
    sri = s[sr]
    od = random.choices(list(o),weights=[70,20,10])[0]
    odi = o[od]
    # TODO: maintenance calculation should be done in gateway, not in sender...
    w=d[dl]+s[sr]+o[od]
    m='not required' if w<70 else 'recommended' if w<=150 else 'urgently needed'
    payload = f"[{datetime.datetime.now().isoformat()}] Dust level: {dl}, Sticky residue: {sr}, Odor: {od}. Cleaning: {m}."
    soap_message = create_soap_message(plant_id, building_id, machine_id, payload, dli, sri, odi)
    response = send_message(APP_URL, soap_message, machine_id)
    if response:
        tprint(f"SOAP request sent to Gateway {APP_URL}")
        # tprint("Gateway Response:")
        # tprint(f"Status Code: {response.status_code}")
        # tprint(f"Response headers: {response.headers}")
        # tprint(f"Response text: {response.text}")
    else:
        tprint("Failed to send SOAP message to gateway.")
    url = f"{SOLACE_REST_URL}/{APP_TOPIC}/xml/v1/{plant_id}/{building_id}/{machine_id}"
    response = send_message(url, soap_message, machine_id)
    if response:
        tprint(f"REST request sent to Solace broker {url}")
        # tprint("Broker Response:")
        # tprint(f"Status Code: {response.status_code}")
        # tprint(f"Response headers: {response.headers}")
        # tprint(f"Response text: {response.text}")
    else:
        tprint("Failed to send SOAP message to Solace broker.")

def run_loop():
    while True:
        main()
        time.sleep(5)  # Interval between messages

def run_http_server():
    try:
        tprint("Sender HTTP server on port 54322 started")
        server_address = ('localhost', 54322)
        httpd = HTTPServer(server_address, SOAPRequestHandler)
        httpd.serve_forever()
    except Exception as e:
        tprint(f"Sender HTTP server not started: {e}")
        quit()

if __name__ == "__main__":
    # Load values from the configuration
    config = ConfigLoader("config.json")
    APP_URL = config.get("app.url")
    APP_TOPIC = config.get("app.topic")

    # NOTE: environment variables must be sourced in advance
    # Solace broker connection settings
    SOLACE_MESSAGE_VPN = os.environ["SOLACE_MESSAGE_VPN"]
    SOLACE_CLIENT_USER = os.environ["SOLACE_CLIENT_USER"]
    SOLACE_CLIENT_PASS = os.environ["SOLACE_CLIENT_PASS"]
    SOLACE_HOST = os.environ["SOLACE_HOST"]
    SOLACE_REST_PORT = os.environ["SOLACE_REST_PORT"]

    http_protocol = 'https://' if SOLACE_REST_PORT[-2:] == '43' else 'http://'

    userpass = '' if http_protocol == 'http://' else f"{SOLACE_CLIENT_USER}:{SOLACE_CLIENT_PASS}@" # TODO: sloppy... replace with proper check/setup (as in other repo)

    # Solace REST API URL
    SOLACE_REST_URL = f"{http_protocol}{userpass}{SOLACE_HOST}:{SOLACE_REST_PORT}"

    # Start the loop sending messages in a separate thread
    loop_thread = threading.Thread(target=run_loop, daemon=True)
    loop_thread.start()

    # Start the HTTP server in the main thread
    run_http_server()