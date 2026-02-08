#CW
import concore
import requests
import time
from ast import literal_eval
import os
import logging

#time.sleep(7)
timeout_max = 20
concore.delay = 0.02

try:
    apikey=open(concore.inpath+'1/concore.apikey',newline=None).readline().rstrip()
except:
    try: 
        #perhaps this should be removed for security
        apikey=open('./concore.apikey',newline=None).readline().rstrip()
    except:
        apikey = ''

try:
    yuyu=open(concore.inpath+'1/concore.yuyu',newline=None).readline().rstrip()
except:
    try: 
        yuyu=open('./concore.yuyu',newline=None).readline().rstrip()
    except:
        yuyu = 'yuyu'

try:
    name1=open(concore.inpath+'1/concore.name1',newline=None).readline().rstrip()
except:
    try:
        name1=open('./concore.name1',newline=None).readline().rstrip()
    except:
        name1 = 'u'

try:
    name2=open(concore.inpath+'1/concore.name2',newline=None).readline().rstrip()
except:
    try:
        name2=open('./concore.name2',newline=None).readline().rstrip()
    except:
        name2 = 'ym'

try:
    init_simtime_u = open(concore.inpath+'1/concore.init1',newline=None).readline().rstrip()
except:
    try:
        init_simtime_u = open('./concore.init1',newline=None).readline().rstrip()
    except:
        init_simtime_u = "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"

try:
    init_simtime_ym = open(concore.inpath+'1/concore.init2',newline=None).readline().rstrip()
except:
    try:
        init_simtime_ym = open('./concore.init2',newline=None).readline().rstrip()
    except:
        init_simtime_ym = "[0.0, 0.0, 0.0]"

logging.debug(f"API Key: {apikey}")
logging.info(f"Yuyu: {yuyu}")
logging.info(f"{name1}={init_simtime_u}")
logging.info(f"{name2}={init_simtime_ym}")

while not os.path.exists(concore.inpath+'1/'+name1):
    time.sleep(concore.delay)


#Nsim = 150
concore.default_maxtime(150)
#init_simtime_u = "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"
#init_simtime_ym = "[0.0, 0.0, 0.0]"

ym = concore.initval(init_simtime_ym)
oldym = init_simtime_ym
oldt = 0


while(concore.simtime<concore.maxtime):
    logging.debug("CW outer loop")
    while concore.unchanged():
        u = concore.read(1,name1,init_simtime_u)
    f = {'file1': open(concore.inpath+'1/'+name1, 'rb')}
    logging.debug(f"CW: before post u={u}")
    logging.debug(f'http://www.controlcore.org/pm/{yuyu}{apikey}&fetch={name2}')
    r = requests.post('http://www.controlcore.org/pm/'+yuyu+apikey+'&fetch='+name2, files=f,timeout=timeout_max)
    if r.status_code!=200:
        logging.error(f"bad POST request {r.status_code}")
        quit()
    if len(r.text)!=0:
        try:
            t=literal_eval(r.text)[0]
        except:
            logging.error(f"bad eval {r.text}")
    timeout_count = 0
    t1 = time.perf_counter()
    logging.debug(f"CW: after post status={r.status_code} r.content={r.content} t={t}")
    #while r.text==oldym or len(r.content)==0:
    while oldt==t or len(r.content)==0:
        time.sleep(concore.delay)
        logging.debug(f"CW waiting status={r.status_code} content={r.content.decode('utf-8')} t={t}")
        f = {'file1': open(concore.inpath+'1/'+name1, 'rb')}
        try:
            r = requests.post('http://www.controlcore.org/pm/'+yuyu+apikey+'&fetch='+name2, files=f,timeout=timeout_max)
        except:
            logging.error("CW: bad request")
        timeout_count += 1
        if r.status_code!=200 or time.perf_counter()-t1 > 1.1*timeout_max: #timeout_count>100:
            logging.error(f"timeout or bad POST request {r.status_code}")
            quit()
        if len(r.text)!=0:
            try:
                t=literal_eval(r.text)[0]
            except:
                logging.error(f"bad eval {r.text}")
    oldt = t
    oldym = r.text
    logging.debug(f"CW: oldym={oldym} t={concore.simtime}")
    concore.write(1,name2,oldym)
#concore.write(1,"ym",init_simtime_ym)
logging.info(f"retry={concore.retrycount}")