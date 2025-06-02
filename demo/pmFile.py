import ast
import numpy as np
import concore

def pm(u):
    return u + 0.01

concore.default_maxtime(150)
concore.delay = 0.02

init_simtime_u = "[0.0, 0.0]"
init_simtime_ym = "[0.0, 0.0]"

ym = np.array([concore.initval(init_simtime_ym)]).T

while concore.simtime < concore.maxtime:
    while concore.unchanged():
        u_raw = concore.read(1, "u", init_simtime_u)
        if isinstance(u_raw, str):  # Fallback when read fails and returns init_simtime_u
            try:
                u_raw = ast.literal_eval(u_raw)
            except:
                print("Failed to parse fallback string:", u_raw)
                u_raw = [0.0]  # safe default
        u = np.array([u_raw], dtype=np.float64).T

    try:
        with open(concore.inpath + "1/file.txt") as infile:
            print(infile.read())
    except:
        print("no file.txt yet")

    ym = pm(u)
    print(f"{concore.simtime}. u={u} ym={ym}")
    concore.write(1, "ym", list(ym.T[0]), delta=1)

print("retry=" + str(concore.retrycount))