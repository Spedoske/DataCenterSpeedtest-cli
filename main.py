import argparse,util,dataCenterSpeedtest,sys
import prettytable as pt

parser = argparse.ArgumentParser()
parser.add_argument("--search",
                    nargs='?',
                    help="使用Where语句筛选数据中心",
                    default="",
                    const="")

parser.add_argument("--order",
                    nargs='?',
                    help="使用Order语句对数据中心排序(仅在--list时生效)",
                    default="",
                    const="")

parser.add_argument("--list",
                    nargs='+',
                    help="输出筛选后的结果,需要提供key")

parser.add_argument("--speedtest", help="对筛选后的结果测速", action='store_true')
parser.add_argument("--icmping", help="对筛选后的结果进行icmping", action='store_true')
parser.add_argument("--tcping", help="对筛选后的结果进行tcping", action='store_true')

parser.add_argument("--pingCount",default=20,help="发送ping的数量",type=int)
parser.add_argument("--pingTimeout",default=1,help="ping超时时间(秒)",type=int)

parser.add_argument("--flushPing", help="清除ping的相关记录", action='store_true')
parser.add_argument("--flushSpeedtest", help="清除测速的相关记录", action='store_true')

args = parser.parse_args()

conn,cursor = util.loadDatabase()

def handleFlush():
    if args.flushPing:
        cursor.execute("UPDATE data_centers SET ping_loss=0,ping_received=0,ping_time=0 "+args.search)
        conn.commit()
    if args.flushSpeedtest:
        cursor.execute("UPDATE data_centers SET download_speed=0 "+args.search)
        conn.commit()

def handlePing():
    if args.icmping:
        util.go_ping(1,args.search,args.pingCount,args.pingTimeout)
    if args.tcping:
        util.go_ping(0,args.search,args.pingCount,args.pingTimeout)

def handleSpeedtest():
    if args.speedtest:
        currentCount=0
        result = cursor.execute('SELECT idc,country,city,test_file_link,enable_download_test FROM data_centers '+args.search).fetchall()
        count = len(result)
        for row in result:
            if row[4]==1:
                [time,data] = dataCenterSpeedtest.measureDownloadSpeed(row[0],row[1]+" "+row[2],row[3],currentCount,count)
                cursor.execute("UPDATE data_centers SET download_speed=? WHERE test_file_link=?",(data/time,row[3]))
                conn.commit()
            else:
                print(
                "节点:", row[0] + " " + row[1]+" "+row[2] +
                "({0}/{1}) 未提供测速链接，无法测速。".format(currentCount + 1, count))
            currentCount+=1

ListMap = {"id":0,
"idc":1,
"idc_abbr":2,
"official_website":3,
"enable_tcping_test":4,
"enable_download_test":5,
"country":6,
"city":7,
"ip":8,
"tcping_port":9,
"test_file_link":10,
"ping_loss":11,
"ping_received":12,
"ping_time":13,
"download_speed":14}

TranslateMap = ["序号",
"服务商名称",
"服务商缩写",
"官方网站",
"是否可以进行tcping",
"是否可以进行测速",
"国家",
"城市",
"IP地址",
"tcping端口",
"下载文件链接",
"ping丢包",
"ping收包",
"ping的平均时间",
"下载速度"]

def handleList():
    if args.list==None:
        return
    listArgs = []
    for listArg in args.list:
        listArgs.append(ListMap[listArg])
    listArgs.sort()
    results = cursor.execute('SELECT * FROM data_centers '+args.search+" "+args.order).fetchall()
    searchTable = pt.PrettyTable()
    fieldNames = []
    for listArg in listArgs:
        fieldNames.append(TranslateMap[listArg])
    searchTable = pt.PrettyTable(fieldNames)
    for result in results:
        resultArray = []
        for listArg in listArgs:
            if listArg==11:
                resultArray.append("{}({:.1f}%)".format(result[listArg],util.getPercentage(result[11],result[11]+result[12])))
            elif listArg==12:
                resultArray.append("{}({:.1f}%)".format(result[listArg],util.getPercentage(result[12],result[11]+result[12])))
            elif listArg==13:
                resultArray.append("{:.2f}ms".format(result[listArg]))
            elif listArg==14:
                resultArray.append(util.prettifyUnit(result[listArg]))
            else:
                resultArray.append(result[listArg])
        searchTable.add_row(resultArray)
    print(searchTable)

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)
actions = [handleFlush,handlePing,handleSpeedtest,handleList]
for behaviour in actions:
    behaviour()
