import socket, json, sqlite3, os, sys, requests
import os
from ctypes import *
unit = ["KB/s", "MB/s", "GB/s"]

def loadDatabase():
    IDCs = loadIDC()
    conn = sqlite3.connect('./DataCenter.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    conn.commit()
    cursor.execute('''create table if not exists data_centers
           (id                   INTEGER PRIMARY KEY    AUTOINCREMENT,
            idc                  TEXT                   NOT NULL,
            idc_abbr             TEXT                   NOT NULL,
            official_website     TEXT                   NOT NULL,
            enable_tcping_test   NUMERIC                NOT NULL,
            enable_download_test NUMERIC                NOT NULL,
            country              TEXT                   NOT NULL,
            city                 TEXT                   NOT NULL,
            ip                   TEXT                   NOT NULL,
            tcping_port          NUMERIC                NOT NULL,
            test_file_link       TEXT                   NOT NULL,
            ping_loss            NUMERIC                NOT NULL,
            ping_received        NUMERIC                NOT NULL,
            ping_time            REAL                   NOT NULL,
            download_speed       REAL                   NOT NULL
           );''')

    dataCenters = []

    for IDC in IDCs:
        dataCenterCount = len(IDC["data_centers"])
        for dataCenterIndex in range(0, dataCenterCount):
            dataCenterTuple = generateIDCTuple(IDC,IDC["data_centers"][dataCenterIndex])
            cursor.execute("SELECT id FROM data_centers WHERE ip = ? and idc = ?", (IDC["data_centers"][dataCenterIndex]['network_info']['ip'],IDC["idc"]))
            if cursor.fetchone() is None:
                dataCenters.append(dataCenterTuple)
    saveIDC(IDCs)
    cursor.executemany('INSERT INTO data_centers VALUES (null,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', dataCenters)
    conn.commit()

    #result = cursor.execute('SELECT * FROM data_centers')
    #for row in result:
    #    print(row)
    return conn,cursor

#    调用go的ping模块进行ping go_ping(pingType,sql,pingCount,pingTimeout)
#    pingType:
#      0:TCP
#      1:ICMP
#    sql: Full sql query string
#    pingTimeout 单位 秒 是整数


#    go_ping(1,"Where country='日本' and idc='Vultr'",4,1)
#    go_ping(1,"",20,1)
def go_ping(pingType,sqlWhere,pingCount,pingTimeout):
    current_path = os.path.dirname(os.path.realpath(__file__))
    lib = cdll.LoadLibrary(current_path + '/ping.so')
    ping = lib.ping
    ping.argtypes = [c_int,c_char_p,c_int,c_int]
    ping(pingType,("SELECT ip,tcping_port,enable_tcping_test FROM data_centers "+sqlWhere).encode("utf-8"),pingCount,pingTimeout)


def getIPInfoFromIPIP(ip):
    response = requests.get("https://btapi.ipip.net/host/info?ip=" + ip)
    if response.status_code == 200:
        info = json.loads(response.text)['area'].split('\t')
        return info[0], " ".join(info[1:3]).strip()
    return None,None

def getHostFromUrl(url):
    return url[url.index('//') + 2:url.index('/', 8)]


def getIPFromHost(host):
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        ip = None
    return ip


def getPercentage(a,b):
    if b==0:
        return 0
    return a/b*100

def loadIDC():
    with open('DataCenter.json', 'r', encoding='UTF-8') as loadedJson:
        return json.load(loadedJson)
    return []


def saveIDC(dataCenter):
    with open('DataCenter.json', 'w', encoding='UTF-8') as loadedJson:
        json.dump(dataCenter,
                  loadedJson,
                  sort_keys=True,
                  indent=4,
                  separators=(', ', ': '),
                  ensure_ascii=False)

def generateIDCAbbr(idcAbbr):
    return "|"+"|".join(idcAbbr)+"|"

def generateIDCTuple(idc,dataCenter):
    if "idc_abbr" not in idc:
        idc["idc_abbr"]=[]
    if "official_website" not in idc:
        idc["official_website"]=""
    if "network_info" not in dataCenter:
        print(idc["idc"],"的数据中心缺少网络信息。")
        sys.exit(1)
    canDownload = False
    canTcping = True
    if "test_file_link" in dataCenter["network_info"]:
        canDownload = True
    if "ip" not in dataCenter["network_info"]:
        if canDownload:
             dataCenter["network_info"]["ip"]=getIPFromHost(getHostFromUrl(dataCenter["network_info"]["test_file_link"]))
        else:
            print(idc["idc"],"的数据中心缺少网络信息。")
            sys.exit(1)
    if "tcping_port" not in dataCenter["network_info"]:
        if canDownload:
             dataCenter["network_info"]["tcping_port"] = 80 if dataCenter["network_info"]["test_file_link"][4]==':' else 443
        else:
            canTcping = False
    dataCenter["conf"]={}
    dataCenter["conf"]["enable_tcping_test"] = canTcping
    dataCenter["conf"]["enable_download_test"] = canDownload
    if "geo_info" not in dataCenter:
        dataCenter["geo_info"]={}
        country,city = getIPInfoFromIPIP(dataCenter["network_info"]["ip"])
        if country==None:
            print(idc["idc"],"的数据中心缺少地理信息。")
            sys.exit(1)
        else:
            dataCenter["geo_info"]["country"]=country
            dataCenter["geo_info"]["city"]=city
    dataCenter["ping_status"]={	"ping_loss": 0,	"ping_received": 0,	"ping_time": 0.0}
    dataCenter["speed_status"]={"download_speed": 0}
    return (idc["idc"],generateIDCAbbr(idc["idc_abbr"]),idc["official_website"],dataCenter["conf"]["enable_tcping_test"],dataCenter["conf"]["enable_download_test"],dataCenter["geo_info"]["country"],dataCenter["geo_info"]["city"],dataCenter["network_info"]["ip"],dataCenter["network_info"]["tcping_port"],dataCenter["network_info"]["test_file_link"],dataCenter["ping_status"]["ping_loss"],dataCenter["ping_status"]["ping_received"],dataCenter["ping_status"]["ping_time"],dataCenter["speed_status"]["download_speed"])

def prettifyUnit(speedFloat):
    speedFloat /= 1024
    step = 0
    while speedFloat > 1024 and step < 2:
        speedFloat /= 1024
        step += 1
    return "{0:.2f} {1}".format(speedFloat, unit[step])
