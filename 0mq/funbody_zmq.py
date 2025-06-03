# funbody2_zmq.py
import zmq
import time
import concore
import concore2

print("funbody using 0mq")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:2356")

concore.delay = 0.07
concore2.delay = 0.07
concore2.inpath = concore.inpath
concore2.outpath = concore.outpath
concore2.simtime = 0
concore.default_maxtime(100)
init_simtime_u = "[0.0, 0.0, 0.0]"
init_simtime_ym = "[0.0, 0.0, 0.0]"

u = concore.initval(init_simtime_u)
ym = concore2.initval(init_simtime_ym)

while concore2.simtime < concore.maxtime:
    msg = socket.recv_json()
    if msg["action"] == "fun":
        u = msg["params"]["u"]
        concore.simtime = u[0]
        u = u[1:]
        concore.write(concore.oport['U2'], "u", u)
        print(u)
        old2 = concore2.simtime
        while concore2.unchanged() or concore2.simtime <= old2:
            ym = concore2.read(concore.iport['Y2'], "ym", init_simtime_ym)
        ym_full = [concore2.simtime] + ym
        print(f"Replying with {ym_full}")
        socket.send_json({"ym": ym_full})
        print(f"funbody u={u} ym={ym} time={concore2.simtime}")
    else:
        print("undefined action: " + str(msg.get("action", "None")))
        socket.send_json({"error": "undefined action"})
        break

print("retry=" + str(concore.retrycount))