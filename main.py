import eventlet

eventlet.monkey_patch()

import argparse, util, dataCenterSpeedtest, functools
import prettytable as pt

IDCs = util.loadIDC()

# 保存搜索结果
# ["服务商", "节点编号"]

searchSet = set()
searchList = []

parser = argparse.ArgumentParser(
)  #description="calculate X to the power of Y")
#group = parser.add_mutually_exclusive_group()
parser.add_argument("--search",
                    nargs='?',
                    help="列出数据中心的信息",
                    default=[],
                    const='all',
                    action='append')
parser.add_argument("--dataCenterIndex",
                    help="限制数据中心的编号",
                    default=[],
                    type=int,
                    action='append')
parser.add_argument("--list",
                    help="输出筛选后的结果(包括服务商,数据中心名称和数据中心编号)",
                    action='store_true')
parser.add_argument("--withIDCAbbr", help="输出服务商的缩写", action='store_true')
parser.add_argument("--withDataCenterHost",
                    help="输出数据中心的域名",
                    action='store_true')
parser.add_argument("--withDataCenterUrl",
                    help="输出数据中心的下载文件地址",
                    action='store_true')
parser.add_argument("--speedtest", help="对筛选后的结果测速", action='store_true')
args = parser.parse_args()

#(isValidIDC,isValidDataCenter,isValidLocalizedDataCenterName)


def doSearch(isValid):
    for IDC in IDCs:
        IDCName = IDC
        IDCLocalizedName = IDCs[IDC]['localized_idc']
        IDCNameValidation = isValid(IDC)
        IDCLocalizedNameValidation = isValid(IDCLocalizedName)
        IDCValidation = IDCNameValidation or IDCLocalizedNameValidation
        dataCenterCount = len(IDCs[IDC]['prefix'][0])
        for dataCenterIndex in range(0, dataCenterCount):
            if (IDCValidation or isValid(
                    IDCs[IDC]["localized_data_center"][dataCenterIndex])) and (
                        len(args.dataCenterIndex) == 0
                        or dataCenterIndex in args.dataCenterIndex):
                searchSet.add((IDCName, dataCenterIndex))


def handleSearch():
    if 'all' in args.search or len(args.search) == 0:
        doSearch(lambda name: True)
    else:
        for arg in args.search:
            doSearch(lambda name: name.upper().find(arg.upper()) >= 0)
    global searchList
    searchList = list(searchSet)
    searchList.sort()


def doPackList(IDCName, Abbr, DCName, DCIdx, DCHost, DCUrl):
    array = [IDCName]
    if args.withIDCAbbr:
        array.append(Abbr)
    array.append(DCName)
    array.append(DCIdx)
    if args.withDataCenterHost:
        array.append(DCHost)
    if args.withDataCenterUrl:
        array.append(DCUrl)
    return array


def handleList():
    if not args.list:
        return
    searchTable = pt.PrettyTable()
    searchTable.field_names = doPackList("服务商", "缩写", "节点位置", "节点编号", "节点域名",
                                         "节点链接")
    searchTable.align = 'l'
    searchTable.align["节点编号"] = 'r'
    for dataCenter in searchList:
        IDC = IDCs[dataCenter[0]]
        dataCenterIndex = dataCenter[1]
        DCUrl = util.loadUrlByArgs(IDC, dataCenterIndex)
        searchTable.add_row(
            doPackList(IDC['localized_idc'], IDC['idc'],
                       IDC['localized_data_center'][dataCenterIndex],
                       dataCenterIndex, util.getHostFromUrl(DCUrl), DCUrl))
    print(searchTable)


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


def handleSpeedtest():
    if not args.speedtest:
        return
    resultArray = []
    searchListCount = len(searchList)
    for dataCenterIndex in range(0, searchListCount):
        dataCenterSpeedtest.measureDownloadSpeed(
            IDCs[searchList[dataCenterIndex][0]],
            searchList[dataCenterIndex][1], resultArray, dataCenterIndex,
            searchListCount)
    resultArray.sort(key=functools.cmp_to_key(compareResultObject),
                     reverse=True)
    resultTable = pt.PrettyTable()
    resultTable.field_names = ["服务商", "节点", "速度", "节点链接"]
    resultTable.align = 'l'
    resultTable.align['速度'] = 'r'
    for row in resultArray:
        row[2] = dataCenterSpeedtest.util.prettifyUnit(row[2])
        resultTable.add_row(row)
    print(resultTable)


actions = [handleSearch, handleList, handleSpeedtest]
for behaviour in actions:
    behaviour()
