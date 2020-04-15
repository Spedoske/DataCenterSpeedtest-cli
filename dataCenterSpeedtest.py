import time, urllib3
import eventlet
import util

# linode 亚特兰大测试点好像挂了,删除测试连接.

downloadTimeout = 30  #单位:秒
downloadChunkSize = 32768  #如果CPU占用率高,请调高此参数.
downloadSpeedRefreshRate = 10  #速度刷新频率.如果CPU占用率高,请调低此参数.
downloadMaxRetryCount = 20  #运营商劫持重试次数

urllib3.disable_warnings()
http = urllib3.PoolManager()


def getNewSpeed(timePrev, dataPrev, dataNow, timeNow):
    timeGap = (timeNow - timePrev) / downloadSpeedRefreshRate
    downloadedData = dataNow - dataPrev
    currentSpeed = util.prettifyUnit(downloadedData / timeGap)
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
        raise Exception("无法从真实测速服务器上下载测试文件,跳过...")
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
    except eventlet.Timeout:
        print('\n')
        print("超时,测试下一个数据中心.")
    except Exception as e:
        print('\n')
        print("发生错误:",str(e))
    print('\n')
    return [downloadTimeout * downloadSpeedRefreshRate, dataNow]


def measureDownloadSpeed(IDC, dataCenterIndex, resultArray, speedtestIndex,
                         searchListCount):
    localized_idc = util.getLocalizedIDC(IDC)
    localized_data_center = util.getLocalizedDataCenterArray(
        IDC)[dataCenterIndex]
    print(
        "节点:", localized_idc + " " + localized_data_center +
        "({0}/{1})".format(speedtestIndex + 1, searchListCount))
    url = util.loadUrlByArgs(IDC, dataCenterIndex)
    print("测试文件地址:", url)
    [timeSpent, dataDownload] = getDataCenterSpeed(url)
    resultArray.append([
        localized_idc, localized_data_center,
        dataDownload / timeSpent * downloadSpeedRefreshRate,
        util.getHostFromUrl(url)
    ])
