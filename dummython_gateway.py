import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import xml.etree.ElementTree as ET
from solace.messaging.messaging_service import MessagingService, RetryStrategy
from solace.messaging.resources.topic import Topic
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.authentication_strategy import ClientCertificateAuthentication
import time
import re
# analytics
import sqlite3
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
# ez
from ez_config_loader import ConfigLoader
from ez_opentelemetry import *

def initialize_db():
    """Initialize the in-memory database and create a transactions table."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id TEXT,
            building_id TEXT,
            machine_id TEXT,
            payload TEXT,
            cpaid TEXT,
            conversationid TEXT,
            service TEXT,
            action TEXT,
            timestamp TEXT,
            dust TEXT,
            sticky TEXT,
            odor TEXT,
            cleaning TEXT,
            dli INTEGER,
            sri INTEGER,
            odi INTEGER
        )
    ''')
    conn.commit()
    return conn

def insert_transaction(conn, transaction_json):
    """Run external fraud check then insert transaction and fraud score into SQLite."""
    cursor = conn.cursor()
    transaction = json.loads(transaction_json)

    # Insert into SQLite
    cursor.execute('''
        INSERT INTO transactions (
            plant_id,
            building_id,
            machine_id,
            payload,
            cpaid,
            conversationid,
            service,
            action,
            timestamp,
            dust,
            sticky,
            odor,
            cleaning,
            dli,
            sri,
            odi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        transaction['plant_id'], transaction['building_id'], transaction['machine_id'],
        transaction['payload'], transaction['cpaid'], transaction['conversationid'],
        transaction['service'], transaction['action'], transaction['timestamp'],
        transaction['dust'], transaction['sticky'], transaction['odor'],
        transaction['cleaning'],transaction['dli'],transaction['sri'],transaction['odi']
    ))
    conn.commit()

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

        # analysis
        insert_transaction(conn, json_message)
        analyze_fraud(conn)

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

def analyze_fraud(conn):
    """Analyze transaction patterns using Isolation Forest to detect anomalies."""
    # Get transactions table length first to determine if necessary to continue. Using COUNT(*) is faster than doing len(df) on SELECT *
    # Note that COUNT(*) can be out of sync?
    len_df = pd.read_sql_query("SELECT COUNT(*) FROM transactions", conn).iloc[0, 0]
    
    # Only train when nt new transactions are added
    nt = 20
    mod = len_df % nt
    if mod != 0:
        return

    # Only train when mt minimum transactions is available
    if len_df < 10:
        print("Not enough data to train the model yet.")
        return

    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    len_df = len(df)

    # Feature selection (excluding categorical/text fields)
    features = ['dli', 'sri', 'odi']
    X = df[features]
    
    # Normalize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest model
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_scaled)
    df['anomaly_score'] = model.decision_function(X_scaled)
    df['is_anomaly'] = model.predict(X_scaled)

    # Compute peer-group mean transaction deviations
    peer_group_means = df.groupby('machine_id')[['dli', 'sri', 'odi']].transform('mean')
    # df['peer_deviation'] = abs(df[['dli', 'sri', 'odi']].sum(axis=1) - peer_group_means) / peer_group_means
    peer_sum = peer_group_means.sum(axis=1)  # sum of means per row (Series)
    df_sum = df[['dli', 'sri', 'odi']].sum(axis=1)  # sum per row (Series)
    df['peer_deviation'] = abs(df_sum - peer_sum) / peer_sum


    # Rule-based checks: Flagging risky payment types and high-risk bank locations
    high_risk_dust = ['high']
    high_risk_sticky = ['excessive']
    high_risk_odor = ['noticeable', 'strong']

    df['high_risk_dust'] = df['dust'].isin(high_risk_dust).astype(int)
    df['high_risk_sticky'] = df['sticky'].isin(high_risk_sticky).astype(int)
    df['high_risk_odor'] = df['odor'].isin(high_risk_odor).astype(int)
        
    # Final fraud risk score
    df['final_cleaning_risk'] = (
        (df['is_anomaly'] == -1).astype(int) + (df['peer_deviation'] > 2).astype(int) + 
        df['high_risk_dust'] + df['high_risk_sticky'] + df['high_risk_odor']
    )

    # Print potential high and low risk transactions to console and report
    high_risk_transactions = df[df['final_cleaning_risk'] > 1]
    low_risk_transactions = df[df['final_cleaning_risk'] < .3]
    high_risk_title = "\nPotential High Risk Cleaning Issue With Machine:\n"
    low_risk_title = "\nPotential Low Risk Cleaning Issue With Machine:\n"
    tprint(f"{bcolors.OKCYAN}")
    tprint(high_risk_title)
    tprint(high_risk_transactions)
    tprint(f"{bcolors.OKBLUE}")
    tprint(low_risk_title)
    tprint(low_risk_transactions)
    tprint(f"{bcolors.ENDC}")
    report_file = open(REPORT_FILE, "a")
    report_file.write(high_risk_title)
    report_file.write(high_risk_transactions.to_string())
    report_file.write(low_risk_title)
    report_file.write(low_risk_transactions.to_string())
    return

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

    REPORT_FILE = config.get("app.report_file")

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

    # Initialize SQLite database (would be Neo4j, MongoDB Atlas, bank system, combination...)
    try:
        conn = initialize_db()
        tprint("- SQLite database running in memory")
    except Exception:
        tprint("- SQLite database not running")
        quit()

    # Start HTTP server
    try:
        tprint("HTTP server on port 54321 started")
        server_address = ('localhost', 54321)
        httpd = HTTPServer(server_address, SOAPRequestHandler)
        httpd.serve_forever()
    except Exception as e:
        tprint(f"- HTTP server  not started: {e}")
        quit()
