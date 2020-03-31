import socket, json

unit = ["KB/s", "MB/s", "GB/s"]


def getHostFromUrl(url):
    return url[url.index('//') + 2:url.index('/', 8)]


def getIPFromHost(host):
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        ip = None
    return ip


def loadIDC():
    with open('DataCenter.json', 'r', encoding='UTF-8') as loadedJson:
        return json.load(loadedJson)
    return {}


def saveIDC(dataCenter):
    with open('DataCenter.json', 'w', encoding='UTF-8') as loadedJson:
        json.dump(dataCenter,
                  loadedJson,
                  sort_keys=True,
                  indent=4,
                  separators=(', ', ': '),
                  ensure_ascii=False)


def loadUrlByArgs(IDC, dataCenterIndex):
    args = []
    #向参数列表中添加参数.
    for argIndex in range(0, IDC['argc']):
        args.append(IDC['prefix'][argIndex][dataCenterIndex])
    #返回填充参数完毕后的url.
    return IDC['domain'].format(*args)


def getLocalizedDataCenterArray(IDC):
    if "localized_data_center" in IDC:
        return IDC["localized_data_center"]
    else:
        return IDC['prefix'][0]


def getLocalizedIDC(IDC):
    if 'localized_idc' in IDC:
        return IDC['localized_idc']
    else:
        return IDC['idc']


def prettifyUnit(speedFloat):
    speedFloat /= 1024
    step = 0
    while speedFloat > 1024 and step < 2:
        speedFloat /= 1024
        step += 1
    return "{0:.2f} {1}".format(speedFloat, unit[step])
