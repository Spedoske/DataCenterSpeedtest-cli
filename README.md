
# 数据中心测速
## 特点
+ 测试与多个数据中心的下载速度(Linode,DigitalOcean等)
+ 灵活的配置文件,可自行添加数据中心测速链接
+ 支持将数据中心地址导入[SmartPing](https://github.com/smartping/smartping)

## 输出示例

| 服务商 |            节点            |    速度    |         节点链接         |
|--------|----------------------------|------------|--------------------------|
| Vultr  |   法国 法兰西岛大区 巴黎   | 222.7KB/s  |  PAR-FR-ping.vultr.com   |
| Vultr  |    美国 华盛顿州 西雅图    | 145.99KB/s |   WA-US-ping.vultr.com   |
| Vultr  |   美国 乔治亚州 亚特兰大   | 131.47KB/s |   GA-US-ping.vultr.com   |
| Vultr  |   美国 佛罗里达州 迈阿密   | 126.54KB/s |   FL-US-ping.vultr.com   |
| Vultr  |   美国 德克萨斯州 达拉斯   | 98.74KB/s  |   TX-US-ping.vultr.com   |
| Vultr  |       新加坡 新加坡        | 95.19KB/s  |    SGP-ping.vultr.com    |
| Vultr  |  美国 加利福尼亚州 圣何塞  | 94.18KB/s  | SJO-CA-US-ping.vultr.com |
| Vultr  |  荷兰 北荷兰省 阿姆斯特丹  | 86.36KB/s  |  AMS-NL-ping.vultr.com   |
| Vultr  |      日本 东京都 东京      | 75.64KB/s  |  HND-JP-ping.vultr.com   |
| Vultr  |   美国 伊利诺伊州 芝加哥   | 68.43KB/s  |   IL-US-ping.vultr.com   |
| Vultr  |   加拿大 安大略省 多伦多   | 65.63KB/s  |  TOR-CA-ping.vultr.com   |
| Vultr  |    德国 黑森州 法兰克福    |  62.5KB/s  |  FRA-DE-ping.vultr.com   |
| Vultr  |  美国 新泽西州 皮斯卡特维  | 60.35KB/s  |   NJ-US-ping.vultr.com   |
| Vultr  |         英国 伦敦          | 49.11KB/s  |  LON-GB-ping.vultr.com   |
| Vultr  | 澳大利亚 新南威尔士州 悉尼 | 29.52KB/s  |  SYD-AU-ping.vultr.com   |

## 安装
### 依赖
+ Python3
+ requests
+ prettytable
+ eventlet
+ urllib3
## 使用
### dataCenterSpeedtest.py
dataCenterSpeedtest.py 允许你测试本机与数据中心之间的速度。您可运行:
```
python3 DataCenterSpeedtest.py vultr Linode
```
来测试本机到vultr和linode节点的速度.
您可输入在`DataCenter.json`中任意IDC的名称或本地化名称作为参数,例如，您想测试本地到DigitalOcean的速度,则可输入:
```
python3 DataCenterSpeedtest.py DigitalOcean
```
或
```
python3 DataCenterSpeedtest.py do
```
注意:类似于`Amazon Web Services`的含有空格的IDC本地化名称无法作为参数输入,因为它会被分解为`Amazon`,`Web`和`Services`.
### updateSmartPing.py
updateSmartPing.py 允许您把数据中心节点添加到[SmartPing](https://github.com/smartping/smartping)中。您可运行:
```
python3 DataCenterSpeedtest.py DigitalOcean
```
将DigitalOcean的所有测试节点添加到[SmartPing](https://github.com/smartping/smartping)中。添加多个测试节点的方法与dataCenterSpeedtest.py的使用方法相同.
### generateLocalizedDataCenterName.py
执行generateLocalizedDataCenterName.py将调用免费IPIP的API生成节点中文名称.
### DataCenter.json
此文件包含了所有节点信息.

## 添加节点信息
节点信息储存在DataCenter.json中，字段意义如下.
| 字段  | 含义  |
|--------|----------------------------|
| idc | 服务商的名称(缩写,便于命令输入)  |
|  localized_idc | 服务商的全称(作为输出,中文英文均可)   |
| domain  |  下载文件的地址(可插入{0},{1},{2}...的参数)  |
| agrc  |  参数数量 |
|  prefix |  参数数组 |
