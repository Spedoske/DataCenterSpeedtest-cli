import json, time, sys, urllib3, functools
import prettytable as pt
import eventlet
import util

eventlet.monkey_patch()

# linode 亚特兰大测试点好像挂了,删除测试连接.

downloadTimeout = 30  #单位:秒
downloadChunkSize = 32768  #如果CPU占用率高,请调高此参数.
downloadSpeedRefreshRate = 10  #速度刷新频率.如果CPU占用率高,请调低此参数.
downloadMaxRetryCount = 20
resultArray = []
resultTable = pt.PrettyTable()
resultTable.field_names = ["服务商", "节点", "速度", "节点链接"]
unit = ["KB/s", "MB/s", "GB/s"]
http = urllib3.PoolManager()


def compareResultObject(x, y):
    if x[2] > y[2]:
        return 1
    elif x[2] < y[2]:
        return -1
    elif x[0] < y[0]:
        return 1
    elif x[0] > y[0]:
        return -1
    elif x[1] < y[1]:
        return 1
    return -1


def prettifyUnit(speedFloat):
    speedFloat /= 1024
    step = 0
    while speedFloat > 1024 and step < 2:
        speedFloat /= 1024
        step += 1
    return str(round(speedFloat, 2)) + unit[step]


def getNewSpeed(timePrev, dataPrev, dataNow, timeNow):
    timeGap = (timeNow - timePrev) / downloadSpeedRefreshRate
    downloadedData = dataNow - dataPrev
    currentSpeed = prettifyUnit(downloadedData / timeGap)
    return [timeNow, dataNow, currentSpeed]


def getValidResponse(dataCenterUrl):
    response = http.request('GET',
                            dataCenterUrl,
                            preload_content=False,
                            timeout=5.0,
                            redirect=False)
    retryCount = 0
    while response.status != 200 and retryCount < downloadMaxRetryCount:
        retryCount += 1
        print("遭遇HTTP劫持 重试中({0}/{1})".format(retryCount,
                                             downloadMaxRetryCount))
        response = http.request('GET',
                                dataCenterUrl,
                                preload_content=False,
                                timeout=5.0,
                                redirect=False)
    if response.status != 200:
        print("无法从真实测速服务器上下载测试文件,跳过...")
        raise Exception(response)
    return response


def getDataCenterSpeed(dataCenterUrl):
    dataPrev = 0
    speedLast = "0KB/s"
    dataNow = 0
    try:
        response = getValidResponse(dataCenterUrl)
        contentSize = int(response.headers['content-length'])
        with eventlet.Timeout(downloadTimeout + 2):
            timeBegin = time.time() * downloadSpeedRefreshRate
            timePrev = timeBegin
            timeNow = timeBegin
            data = True
            while data and timeNow - timeBegin <= downloadTimeout * downloadSpeedRefreshRate:
                data = response.read(downloadChunkSize)
                timeNow = time.time() * downloadSpeedRefreshRate
                dataNow += len(data)
                downloadProgress = (dataNow / contentSize) * 100
                if timeNow - timePrev > 1:
                    [timePrev, dataPrev,
                     speedLast] = getNewSpeed(timePrev, dataPrev, dataNow,
                                              timeNow)
                    print("\r下载进度：%d%% - %s       " %
                          (downloadProgress, speedLast),
                          end=" ")
            if not data:
                print("\r下载进度：100%% - %s       " % (speedLast), end=" ")
            print('\n')
            return [timeNow - timeBegin, dataNow]
    except:
        pass
    print('\n')
    return [downloadTimeout * downloadSpeedRefreshRate, dataNow]


IDCs = util.loadIDC()

for IDC in IDCs:
    if IDC['idc'] in sys.argv or IDC['localized_idc'] in sys.argv:
        if 'localized_idc' in IDC:
            localized_idc = IDC['localized_idc']
        else:
            localized_idc = IDC['idc']
        print("正在测试:", localized_idc)
        dataCenterCount = len(IDC['prefix'][0])
        for dataCenterIndex in range(0, dataCenterCount):
            if 'localized_data_center' in IDC:
                localized_data_center = IDC['localized_data_center'][
                    dataCenterIndex]
            else:
                localized_data_center = IDC['prefix'][0][dataCenterIndex]
            print("节点:", localized_data_center)
            url = util.loadUrlByArgs(IDC, dataCenterIndex)
            print("测试文件地址:", url)
            [timeSpent, dataDownload] = getDataCenterSpeed(url)
            resultArray.append([
                localized_idc, localized_data_center,
                dataDownload / timeSpent * downloadSpeedRefreshRate,
                util.getHostFromUrl(url)
            ])
resultArray.sort(key=functools.cmp_to_key(compareResultObject), reverse=True)
for row in resultArray:
    row[2] = prettifyUnit(row[2])
    resultTable.add_row(row)
print("\n\n\n\n\n")
print(resultTable)
