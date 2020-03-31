import socket, json


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
    with open('DataCenter.json', 'w') as loadedJson:
        json.dump(dataCenter, loadedJson)


def loadUrlByArgs(IDC, dataCenterIndex):
    args = []
    #向参数列表中添加参数.
    for argIndex in range(0, IDC['argc']):
        args.append(IDC['prefix'][argIndex][dataCenterIndex])
    #返回填充参数完毕后的url.
    return IDC['domain'].format(*args)
