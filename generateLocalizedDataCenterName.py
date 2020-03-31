import requests, json, util


def getIPInfoFromIPIP(ip):
    response = requests.get("http://freeapi.ipip.net/" + ip)
    if response.status_code == 200:
        info = json.loads(response.text)
        return " ".join(info[:-1]).strip()
    return None


IDCs = util.loadIDC()

for IDC in IDCs:
    IDCObject = IDCs[IDC]
    #检查IDC名称是否有翻译.
    if "localized_data_center" not in IDCObject:
        IDCObject["localized_data_center"] = []
        dataCenterCount = len(IDCObject['prefix'][0])
        #开始遍历数据中心.
        for dataCenterIndex in range(0, dataCenterCount):
            url = util.loadUrlByArgs(IDCObject, dataCenterIndex)
            ip = util.getIPFromHost(util.getHostFromUrl(url))
            unlocalizedName = IDCObject['prefix'][0][dataCenterIndex].strip()
            if ip:
                #IP解析成功,调用IPIP免费API.
                localizedName = getIPInfoFromIPIP(ip)
                if localizedName == None:
                    localizedName = unlocalizedName
                IDCObject["localized_data_center"].append(localizedName)
            else:
                #IP解析失败,使用英文名称.
                IDCObject["localized_data_center"].append(unlocalizedName)

util.saveIDC(IDCs)
