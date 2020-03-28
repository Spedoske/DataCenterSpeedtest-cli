import socket, requests, json, util, sys

smartpingUrl = "http://127.0.0.1:8899"

smartpingPassword = "smartping"


def getServerSettings():
    jsonUrl = requests.get(smartpingUrl + "/api/config.json")
    return json.loads(jsonUrl.text)


def getDefaultEndPoint(name, ip):
    return {
        "Addr": ip,
        "Name": name,
        "Ping": [],
        "Smartping": False,
        "Topology": []
    }


smartpingSetting = getServerSettings()
IDCs = util.loadIDC()

for IDC in IDCs:
    if IDC['idc'] in sys.argv or IDC['localized_idc'] in sys.argv:
        if "localized_data_center" in IDC:
            localized_data_center_array = IDC["localized_data_center"]
        else:
            localized_data_center_array = IDC['prefix'][0]
        dataCenterCount = len(IDC['prefix'][0])
        for dataCenterIndex in range(0, dataCenterCount):
            url = util.loadUrlByArgs(IDC, dataCenterIndex)
            localized_idc = IDC[
                'localized_idc'] + ' ' + localized_data_center_array[
                    dataCenterIndex]
            ip = util.getIPFromHost(util.getHostFromUrl(url))
            if ip not in smartpingSetting['Network'] and ip != None:
                smartpingSetting['Network'][ip] = getDefaultEndPoint(
                    localized_idc, ip)
requests.post(smartpingUrl + "/api/saveconfig.json",
              data={
                  "password": smartpingPassword,
                  "config": json.dumps(smartpingSetting)
              })
