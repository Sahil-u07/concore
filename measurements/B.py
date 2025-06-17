# B.py (Broker with Measurements)
import concore
import time

# --- ZMQ Initialization ---
# This REP socket binds and waits for requests from Node A
concore.init_zmq_port(
    port_name=PORT_NAME_F1_F2,
    port_type="bind",
    address="tcp://*:" + PORT_F1_F2,
    socket_type_str="REP"
)
# This REQ socket connects to Node C
concore.init_zmq_port(
    port_name=PORT_NAME_F2_F3,
    port_type="connect",
    address="tcp://localhost:" + PORT_F2_F3,
    socket_type_str="REQ"
)

print("Node B broker started. Waiting for requests...")

# --- Measurement Initialization ---
start_time = time.monotonic()
messages_routed = 0

while True:
    # 1. Wait for a request from Node A
    value_from_a = concore.read(PORT_NAME_F1_F2, "value", [0.0])
    received_value = value_from_a[0]
    print(f"Node B: Received {received_value:.2f} from Node A. Forwarding to C...")

    # 2. Send the received value as a new request to Node C
    concore.write(PORT_NAME_F2_F3, "value", [received_value])

    # 3. Wait for the reply from Node C
    value_from_c = concore.read(PORT_NAME_F2_F3, "value", [0.0])
    processed_value = value_from_c[0]
    print(f"Node B: Received {processed_value:.2f} from Node C. Replying to A...")

    # 4. Send the processed value back as a reply to Node A
    concore.write(PORT_NAME_F1_F2, "value", [processed_value])
    messages_routed += 1

    # 5. Check termination condition
    if processed_value >= 100:
        break

# --- Finalize and Report Measurements ---
end_time = time.monotonic()
duration = end_time - start_time

print("\n" + "="*30)
print("--- NODE B: RESULTS ---")
print(f"Total messages routed: {messages_routed}")
print(f"Total execution time:  {duration:.4f} seconds")
print("="*30)

print("\nNode B: Terminating.")
concore.terminate_zmq()
