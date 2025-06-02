# funcall2_zmq.py
import zmq
import time
import concore
import concore2

print("funcall using 0mq")

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:2346")

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
    while concore.unchanged():
        u = concore.read(concore.iport['U'], "u", init_simtime_u)
    message = {
        "action": "fun",
        "params": {"u": [concore.simtime] + u}
    }
    socket.send_json(message)
    response = socket.recv_json()
    ym = response["ym"]
    concore2.simtime = ym[0]
    ym = ym[1:]
    concore2.write(concore.oport['Y'], "ym", ym)
    print(f"funcall 0mq u={u} ym={ym} time={concore2.simtime}")
print("retry=" + str(concore.retrycount))