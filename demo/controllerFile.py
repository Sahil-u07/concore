import numpy as np
import concore
import ast

ysp = 3.0

def controller(ym): 
    if ym[0] < ysp:
        return 1.01 * ym
    else:
        return 0.9 * ym

concore.default_maxtime(150)
concore.delay = 0.02

init_simtime_u = "[0.0, 0.0]"
init_simtime_ym = "[0.0, 0.0]"

u = np.array([concore.initval(init_simtime_u)], dtype=np.float64).T

while concore.simtime < concore.maxtime:
    while concore.unchanged():
        ym_raw = concore.read(1, "ym", init_simtime_ym)
        if isinstance(ym_raw, str):
            try:
                ym_raw = ast.literal_eval(ym_raw)
            except:
                print("Failed to parse fallback ym string:", ym_raw)
                ym_raw = [0.0]
        ym = np.array([ym_raw], dtype=np.float64).T

    u = controller(ym)
    
    try:
        with open(concore.outpath + "1/file.txt", "w") as outfile:
            outfile.write("the controller says u=" + str(u) + " ym=" + str(ym))
    except Exception as e:
        print(f"Error writing file.txt: {e}")
    
    print(f"{concore.simtime}. u={u} ym={ym}")
    concore.write(1, "u", list(u.T[0]), delta=0)

print("retry=" + str(concore.retrycount))