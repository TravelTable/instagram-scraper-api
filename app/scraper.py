# app/scraper.py

import httpx
import json
import asyncio
from urllib.parse import quote
import jmespath
from langdetect import detect
from datetime import datetime
import re
import random

from app.config import HEADERS, INSTAGRAM_PROFILE_URL, INSTAGRAM_GRAPHQL_URL, POST_DOCUMENT_ID, USER_POSTS_DOCUMENT_ID

# --- PROXIES ---
proxies = [
    "http://xttldmfg:72k2bib2ip3r@23.229.125.125:5394",
    "http://xttldmfg:72k2bib2ip3r@38.153.138.115:9454",
    "http://xttldmfg:72k2bib2ip3r@104.233.26.4:5842",
    "http://xttldmfg:72k2bib2ip3r@23.27.203.45:6780",
    "http://xttldmfg:72k2bib2ip3r@50.114.15.144:6129",
    "http://xttldmfg:72k2bib2ip3r@104.224.90.91:6252",
    "http://xttldmfg:72k2bib2ip3r@45.41.176.74:6372",
    "http://xttldmfg:72k2bib2ip3r@64.188.120.31:7778",
    "http://xttldmfg:72k2bib2ip3r@136.0.186.24:6385",
    "http://xttldmfg:72k2bib2ip3r@154.29.65.38:6146",
    "http://xttldmfg:72k2bib2ip3r@181.41.218.12:5598",
    "http://xttldmfg:72k2bib2ip3r@185.216.106.137:6214",
    "http://xttldmfg:72k2bib2ip3r@31.58.29.202:6168",
    "http://xttldmfg:72k2bib2ip3r@45.39.1.154:5593",
    "http://xttldmfg:72k2bib2ip3r@145.223.54.28:5993",
    "http://xttldmfg:72k2bib2ip3r@185.216.107.95:5672",
    "http://xttldmfg:72k2bib2ip3r@23.27.91.39:6118",
    "http://xttldmfg:72k2bib2ip3r@206.206.119.188:6099",
    "http://xttldmfg:72k2bib2ip3r@154.6.115.147:6616",
    "http://xttldmfg:72k2bib2ip3r@192.3.48.157:6150",
    "http://xttldmfg:72k2bib2ip3r@179.61.166.210:6633",
    "http://xttldmfg:72k2bib2ip3r@38.170.190.152:9503",
    "http://xttldmfg:72k2bib2ip3r@45.56.175.147:5821",
    "http://xttldmfg:72k2bib2ip3r@45.61.123.232:5911",
    "http://xttldmfg:72k2bib2ip3r@91.124.253.207:6567",
    "http://xttldmfg:72k2bib2ip3r@136.0.220.206:5586",
    "http://xttldmfg:72k2bib2ip3r@142.111.131.107:6185",
    "http://xttldmfg:72k2bib2ip3r@185.216.106.148:6225",
    "http://xttldmfg:72k2bib2ip3r@38.170.157.215:9254",
    "http://xttldmfg:72k2bib2ip3r@166.88.48.95:5421",
    "http://xttldmfg:72k2bib2ip3r@207.244.219.94:6350",
    "http://xttldmfg:72k2bib2ip3r@23.27.184.132:5733",
    "http://xttldmfg:72k2bib2ip3r@64.64.110.184:6707",
    "http://xttldmfg:72k2bib2ip3r@104.252.28.213:6151",
    "http://xttldmfg:72k2bib2ip3r@148.135.144.194:5690",
    "http://xttldmfg:72k2bib2ip3r@38.154.191.188:8765",
    "http://xttldmfg:72k2bib2ip3r@45.39.27.21:7442",
    "http://xttldmfg:72k2bib2ip3r@45.38.84.131:7067",
    "http://xttldmfg:72k2bib2ip3r@23.236.247.164:8196",
    "http://xttldmfg:72k2bib2ip3r@45.61.127.95:6034",
    "http://xttldmfg:72k2bib2ip3r@107.174.136.29:5971",
    "http://xttldmfg:72k2bib2ip3r@191.101.25.224:6621",
    "http://xttldmfg:72k2bib2ip3r@206.206.119.208:6119",
    "http://xttldmfg:72k2bib2ip3r@107.172.116.129:5585",
    "http://xttldmfg:72k2bib2ip3r@173.211.0.21:6514",
    "http://xttldmfg:72k2bib2ip3r@191.101.188.184:6938",
    "http://xttldmfg:72k2bib2ip3r@92.113.7.171:6897",
    "http://xttldmfg:72k2bib2ip3r@173.239.219.46:5955",
    "http://xttldmfg:72k2bib2ip3r@185.216.107.164:5741",
    "http://xttldmfg:72k2bib2ip3r@104.238.10.36:5982",
    "http://xttldmfg:72k2bib2ip3r@185.101.254.44:5591",
    "http://xttldmfg:72k2bib2ip3r@23.26.95.75:5557",
    "http://xttldmfg:72k2bib2ip3r@199.180.10.91:6462",
    "http://xttldmfg:72k2bib2ip3r@136.0.220.56:5436",
    "http://xttldmfg:72k2bib2ip3r@136.0.127.44:5753",
    "http://xttldmfg:72k2bib2ip3r@104.238.10.251:6197",
    "http://xttldmfg:72k2bib2ip3r@104.232.211.93:5706",
    "http://xttldmfg:72k2bib2ip3r@198.37.99.2:5793",
    "http://xttldmfg:72k2bib2ip3r@198.46.148.171:5859",
    "http://xttldmfg:72k2bib2ip3r@191.96.130.197:5960",
    "http://xttldmfg:72k2bib2ip3r@216.74.80.53:6625",
    "http://xttldmfg:72k2bib2ip3r@192.241.125.185:8229",
    "http://xttldmfg:72k2bib2ip3r@23.95.255.196:6780",
    "http://xttldmfg:72k2bib2ip3r@38.153.133.161:9565",
    "http://xttldmfg:72k2bib2ip3r@23.26.94.5:5987",
    "http://xttldmfg:72k2bib2ip3r@38.170.169.59:5300",
    "http://xttldmfg:72k2bib2ip3r@45.81.149.168:6600",
    "http://xttldmfg:72k2bib2ip3r@184.174.43.249:6789",
    "http://xttldmfg:72k2bib2ip3r@191.96.254.62:6109",
    "http://xttldmfg:72k2bib2ip3r@67.227.36.7:6049",
    "http://xttldmfg:72k2bib2ip3r@147.124.198.215:6074",
    "http://xttldmfg:72k2bib2ip3r@45.61.100.246:6514",
    "http://xttldmfg:72k2bib2ip3r@104.233.13.27:6022",
    "http://xttldmfg:72k2bib2ip3r@154.6.129.121:5591",
    "http://xttldmfg:72k2bib2ip3r@206.206.64.132:6093",
    "http://xttldmfg:72k2bib2ip3r@38.153.139.129:9805",
    "http://xttldmfg:72k2bib2ip3r@45.61.97.37:6563",
    "http://xttldmfg:72k2bib2ip3r@216.74.118.163:6318",
    "http://xttldmfg:72k2bib2ip3r@173.244.41.11:6195",
    "http://xttldmfg:72k2bib2ip3r@38.153.137.229:5537",
    "http://xttldmfg:72k2bib2ip3r@184.174.27.168:6391",
    "http://xttldmfg:72k2bib2ip3r@206.206.124.5:6586",
    "http://xttldmfg:72k2bib2ip3r@154.6.87.89:6559",
    "http://xttldmfg:72k2bib2ip3r@92.113.246.119:5704",
    "http://xttldmfg:72k2bib2ip3r@166.88.238.121:6101",
    "http://xttldmfg:72k2bib2ip3r@89.249.193.137:5875",
    "http://xttldmfg:72k2bib2ip3r@89.249.193.85:5823",
    "http://xttldmfg:72k2bib2ip3r@142.111.161.99:6470",
    "http://xttldmfg:72k2bib2ip3r@45.38.78.62:5999",
    "http://xttldmfg:72k2bib2ip3r@104.239.107.43:5695",
    "http://xttldmfg:72k2bib2ip3r@23.26.95.154:5636",
    "http://xttldmfg:72k2bib2ip3r@107.174.136.190:6132",
    "http://xttldmfg:72k2bib2ip3r@172.245.158.28:5981",
    "http://xttldmfg:72k2bib2ip3r@154.6.59.117:6585",
    "http://xttldmfg:72k2bib2ip3r@191.96.117.22:6777",
    "http://xttldmfg:72k2bib2ip3r@198.37.99.159:5950",
    "http://xttldmfg:72k2bib2ip3r@208.70.11.124:6205",
    "http://xttldmfg:72k2bib2ip3r@107.172.163.30:6546",
    "http://xttldmfg:72k2bib2ip3r@38.153.135.119:5499",
    "http://xttldmfg:72k2bib2ip3r@46.202.248.63:5557",
    "http://xttldmfg:72k2bib2ip3r@184.174.56.215:5227",
    "http://xttldmfg:72k2bib2ip3r@154.6.121.253:6220",
    "http://xttldmfg:72k2bib2ip3r@23.26.71.226:5709",
    "http://xttldmfg:72k2bib2ip3r@104.239.35.158:5840",
    "http://xttldmfg:72k2bib2ip3r@192.186.185.53:6612",
    "http://xttldmfg:72k2bib2ip3r@38.154.224.144:6685",
    "http://xttldmfg:72k2bib2ip3r@31.59.18.54:6635",
    "http://xttldmfg:72k2bib2ip3r@104.239.38.29:6562",
    "http://xttldmfg:72k2bib2ip3r@198.37.118.167:5626",
    "http://xttldmfg:72k2bib2ip3r@89.249.197.52:6638",
    "http://xttldmfg:72k2bib2ip3r@142.111.98.126:5827",
    "http://xttldmfg:72k2bib2ip3r@31.58.151.72:6063",
    "http://xttldmfg:72k2bib2ip3r@174.140.254.21:6612",
    "http://xttldmfg:72k2bib2ip3r@38.153.138.157:9496",
    "http://xttldmfg:72k2bib2ip3r@184.174.30.232:5901",
    "http://xttldmfg:72k2bib2ip3r@191.101.181.110:6863",
    "http://xttldmfg:72k2bib2ip3r@136.0.180.88:6109",
    "http://xttldmfg:72k2bib2ip3r@31.58.16.66:6033",
    "http://xttldmfg:72k2bib2ip3r@104.239.38.149:6682",
    "http://xttldmfg:72k2bib2ip3r@92.113.231.202:7287",
    "http://xttldmfg:72k2bib2ip3r@166.88.169.88:6695",
    "http://xttldmfg:72k2bib2ip3r@107.173.137.47:6301",
    "http://xttldmfg:72k2bib2ip3r@136.0.189.92:6819",
    "http://xttldmfg:72k2bib2ip3r@38.170.163.164:8220",
    "http://xttldmfg:72k2bib2ip3r@45.61.121.217:6816",
    "http://xttldmfg:72k2bib2ip3r@64.64.118.36:6619",
    "http://xttldmfg:72k2bib2ip3r@45.39.1.128:5567",
    "http://xttldmfg:72k2bib2ip3r@46.202.71.95:6090",
    "http://xttldmfg:72k2bib2ip3r@191.96.130.100:5863",
    "http://xttldmfg:72k2bib2ip3r@191.101.26.153:5892",
    "http://xttldmfg:72k2bib2ip3r@192.186.151.51:8552",
    "http://xttldmfg:72k2bib2ip3r@192.186.185.232:6791",
    "http://xttldmfg:72k2bib2ip3r@198.46.241.207:6742",
    "http://xttldmfg:72k2bib2ip3r@154.29.232.88:6748",
    "http://xttldmfg:72k2bib2ip3r@46.202.78.247:5742",
    "http://xttldmfg:72k2bib2ip3r@166.88.224.152:6050",
    "http://xttldmfg:72k2bib2ip3r@64.79.235.25:6049",
    "http://xttldmfg:72k2bib2ip3r@31.57.85.115:5801",
    "http://xttldmfg:72k2bib2ip3r@142.147.132.177:6372",
    "http://xttldmfg:72k2bib2ip3r@104.232.209.133:6091",
    "http://xttldmfg:72k2bib2ip3r@206.206.119.55:5966",
    "http://xttldmfg:72k2bib2ip3r@179.61.166.41:6464",
    "http://xttldmfg:72k2bib2ip3r@146.103.5.87:6667",
    "http://xttldmfg:72k2bib2ip3r@64.188.100.215:7963",
    "http://xttldmfg:72k2bib2ip3r@166.88.64.149:6532",
    "http://xttldmfg:72k2bib2ip3r@192.186.151.167:8668",
    "http://xttldmfg:72k2bib2ip3r@23.27.78.48:5628",
    "http://xttldmfg:72k2bib2ip3r@38.170.173.87:7638",
    "http://xttldmfg:72k2bib2ip3r@136.0.207.249:6826",
    "http://xttldmfg:72k2bib2ip3r@107.173.36.46:5501",
    "http://xttldmfg:72k2bib2ip3r@192.186.151.19:8520",
    "http://xttldmfg:72k2bib2ip3r@206.206.119.121:6032",
    "http://xttldmfg:72k2bib2ip3r@38.153.137.22:5330",
    "http://xttldmfg:72k2bib2ip3r@67.227.14.17:6609",
    "http://xttldmfg:72k2bib2ip3r@104.233.12.232:6783",
    "http://xttldmfg:72k2bib2ip3r@104.239.105.26:6556",
    "http://xttldmfg:72k2bib2ip3r@185.202.175.8:6796",
    "http://xttldmfg:72k2bib2ip3r@166.88.169.199:6806",
    "http://xttldmfg:72k2bib2ip3r@185.216.106.11:6088",
    "http://xttldmfg:72k2bib2ip3r@145.223.54.129:6094",
    "http://xttldmfg:72k2bib2ip3r@107.174.194.154:5596",
    "http://xttldmfg:72k2bib2ip3r@46.202.71.35:6030",
    "http://xttldmfg:72k2bib2ip3r@154.30.1.73:5389",
    "http://xttldmfg:72k2bib2ip3r@31.57.87.129:5814",
    "http://xttldmfg:72k2bib2ip3r@92.113.1.80:5780",
    "http://xttldmfg:72k2bib2ip3r@142.111.93.241:6802",
    "http://xttldmfg:72k2bib2ip3r@216.173.120.93:6385",
    "http://xttldmfg:72k2bib2ip3r@92.113.246.113:5698",
    "http://xttldmfg:72k2bib2ip3r@136.0.109.55:6341",
    "http://xttldmfg:72k2bib2ip3r@38.154.233.30:5440",
    "http://xttldmfg:72k2bib2ip3r@107.172.221.6:5961",
    "http://xttldmfg:72k2bib2ip3r@173.244.41.113:6297",
    "http://xttldmfg:72k2bib2ip3r@198.37.116.246:6205",
    "http://xttldmfg:72k2bib2ip3r@104.239.38.118:6651",
    "http://xttldmfg:72k2bib2ip3r@23.27.208.128:5838",
    "http://xttldmfg:72k2bib2ip3r@45.39.5.119:6557",
    "http://xttldmfg:72k2bib2ip3r@206.206.64.77:6038",
    "http://xttldmfg:72k2bib2ip3r@146.103.55.207:6259",
    "http://xttldmfg:72k2bib2ip3r@146.103.5.90:6670",
    "http://xttldmfg:72k2bib2ip3r@173.0.10.120:6296",
    "http://xttldmfg:72k2bib2ip3r@38.153.137.28:5336",
    "http://xttldmfg:72k2bib2ip3r@45.38.84.28:6964",
    "http://xttldmfg:72k2bib2ip3r@173.0.9.96:5679",
    "http://xttldmfg:72k2bib2ip3r@149.57.17.215:5683",
    "http://xttldmfg:72k2bib2ip3r@38.154.197.109:6775",
    "http://xttldmfg:72k2bib2ip3r@45.38.45.29:5968",
    "http://xttldmfg:72k2bib2ip3r@38.153.152.177:9527",
    "http://xttldmfg:72k2bib2ip3r@104.232.211.227:5840",
    "http://xttldmfg:72k2bib2ip3r@31.58.29.9:5975",
    "http://xttldmfg:72k2bib2ip3r@161.123.101.46:6672",
    "http://xttldmfg:72k2bib2ip3r@192.177.86.139:5140",
    "http://xttldmfg:72k2bib2ip3r@104.252.28.154:6092",
    "http://xttldmfg:72k2bib2ip3r@38.170.159.128:6719",
    "http://xttldmfg:72k2bib2ip3r@192.177.103.164:6657",
    "http://xttldmfg:72k2bib2ip3r@199.180.11.19:6756",
    "http://xttldmfg:72k2bib2ip3r@38.154.193.243:5516",
    "http://xttldmfg:72k2bib2ip3r@107.172.116.145:5601",
    "http://xttldmfg:72k2bib2ip3r@31.59.13.249:6519",
    "http://xttldmfg:72k2bib2ip3r@31.57.87.210:5895",
    "http://xttldmfg:72k2bib2ip3r@45.127.250.159:5768",
    "http://xttldmfg:72k2bib2ip3r@172.245.7.119:5172",
    "http://xttldmfg:72k2bib2ip3r@192.154.250.174:5754",
    "http://xttldmfg:72k2bib2ip3r@154.6.115.137:6606",
    "http://xttldmfg:72k2bib2ip3r@142.147.245.154:5845",
    "http://xttldmfg:72k2bib2ip3r@146.103.5.188:6768",
    "http://xttldmfg:72k2bib2ip3r@173.239.237.225:5871",
    "http://xttldmfg:72k2bib2ip3r@89.249.194.31:6430",
    "http://xttldmfg:72k2bib2ip3r@173.211.69.215:6808",
    "http://xttldmfg:72k2bib2ip3r@23.26.68.153:6136",
    "http://xttldmfg:72k2bib2ip3r@50.114.15.198:6183",
    "http://xttldmfg:72k2bib2ip3r@184.174.30.126:5795",
    "http://xttldmfg:72k2bib2ip3r@23.27.91.241:6320",
    "http://xttldmfg:72k2bib2ip3r@45.127.248.186:5187",
    "http://xttldmfg:72k2bib2ip3r@92.113.1.184:5884",
    "http://xttldmfg:72k2bib2ip3r@206.206.122.150:5781",
    "http://xttldmfg:72k2bib2ip3r@161.123.93.40:5770",
    "http://xttldmfg:72k2bib2ip3r@147.185.250.171:6957",
    "http://xttldmfg:72k2bib2ip3r@67.227.112.102:6142",
    "http://xttldmfg:72k2bib2ip3r@45.41.178.104:6325",
    "http://xttldmfg:72k2bib2ip3r@198.23.214.241:6508",
    "http://xttldmfg:72k2bib2ip3r@23.229.125.76:5345",
    "http://xttldmfg:72k2bib2ip3r@146.103.44.145:6697",
    "http://xttldmfg:72k2bib2ip3r@38.153.139.170:9846",
    "http://xttldmfg:72k2bib2ip3r@107.172.163.29:6545",
    "http://xttldmfg:72k2bib2ip3r@198.37.121.15:6435",
    "http://xttldmfg:72k2bib2ip3r@142.111.161.180:6551",
    "http://xttldmfg:72k2bib2ip3r@198.37.109.252:6359",
    "http://xttldmfg:72k2bib2ip3r@104.238.10.111:6057",
    "http://xttldmfg:72k2bib2ip3r@38.170.176.93:5488",
    "http://xttldmfg:72k2bib2ip3r@45.92.77.33:6055",
    "http://xttldmfg:72k2bib2ip3r@45.249.59.104:6080",
    "http://xttldmfg:72k2bib2ip3r@142.147.131.217:6117",
    "http://xttldmfg:72k2bib2ip3r@145.223.54.253:6218",
    "http://xttldmfg:72k2bib2ip3r@184.174.126.165:6457",
    "http://xttldmfg:72k2bib2ip3r@142.111.93.86:6647",
    "http://xttldmfg:72k2bib2ip3r@173.211.30.36:6470",
    "http://xttldmfg:72k2bib2ip3r@45.41.176.242:6540",
    "http://xttldmfg:72k2bib2ip3r@67.227.113.204:5744",
    "http://xttldmfg:72k2bib2ip3r@45.56.175.149:5823",
    "http://xttldmfg:72k2bib2ip3r@161.123.130.115:5786",
    "http://xttldmfg:72k2bib2ip3r@104.252.12.130:7069",
    "http://xttldmfg:72k2bib2ip3r@154.30.250.129:5641",
    "http://xttldmfg:72k2bib2ip3r@154.30.242.118:9512",
    "http://xttldmfg:72k2bib2ip3r@198.46.241.36:6571",
    "http://xttldmfg:72k2bib2ip3r@23.26.94.4:5986",
    "http://xttldmfg:72k2bib2ip3r@89.249.192.205:6604",
    "http://xttldmfg:72k2bib2ip3r@38.154.191.90:8667",
    "http://xttldmfg:72k2bib2ip3r@23.26.94.162:6144",
    "http://xttldmfg:72k2bib2ip3r@104.239.39.226:6155",
    "http://xttldmfg:72k2bib2ip3r@136.0.105.149:6159",
    "http://xttldmfg:72k2bib2ip3r@92.113.236.13:6598",
    "http://xttldmfg:72k2bib2ip3r@45.39.1.152:5591",
    "http://xttldmfg:72k2bib2ip3r@23.95.255.17:6601",
    "http://xttldmfg:72k2bib2ip3r@166.88.238.148:6128",
    "http://xttldmfg:72k2bib2ip3r@45.41.179.141:6676",
    "http://xttldmfg:72k2bib2ip3r@38.153.134.114:9783",
    "http://xttldmfg:72k2bib2ip3r@45.127.248.178:5179",
    "http://xttldmfg:72k2bib2ip3r@142.111.124.105:6125",
    "http://xttldmfg:72k2bib2ip3r@148.135.144.157:5653",
    "http://xttldmfg:72k2bib2ip3r@216.173.120.222:6514",
    "http://xttldmfg:72k2bib2ip3r@23.27.210.203:6573",
    "http://xttldmfg:72k2bib2ip3r@145.223.58.194:6463",
    "http://xttldmfg:72k2bib2ip3r@198.46.148.170:5858",
    "http://xttldmfg:72k2bib2ip3r@46.202.224.186:5738",
    "http://xttldmfg:72k2bib2ip3r@136.0.118.193:6565",
    "http://xttldmfg:72k2bib2ip3r@198.46.148.225:5913",
    "http://xttldmfg:72k2bib2ip3r@166.88.235.225:5853",
    "http://xttldmfg:72k2bib2ip3r@192.186.151.146:8647",
    "http://xttldmfg:72k2bib2ip3r@206.232.103.203:6360",
    "http://xttldmfg:72k2bib2ip3r@142.147.131.156:6056",
    "http://xttldmfg:72k2bib2ip3r@184.174.56.75:5087",
    "http://xttldmfg:72k2bib2ip3r@104.239.35.21:5703",
    "http://xttldmfg:72k2bib2ip3r@103.251.223.32:6011",
    "http://xttldmfg:72k2bib2ip3r@154.30.252.8:5139",
    "http://xttldmfg:72k2bib2ip3r@64.79.235.222:6246",
    "http://xttldmfg:72k2bib2ip3r@166.88.58.42:5767",
    "http://xttldmfg:72k2bib2ip3r@45.61.100.168:6436",
    "http://xttldmfg:72k2bib2ip3r@191.101.181.102:6855",
    "http://xttldmfg:72k2bib2ip3r@192.186.151.160:8661",
    "http://xttldmfg:72k2bib2ip3r@38.153.148.54:5325",
    "http://xttldmfg:72k2bib2ip3r@45.39.5.181:6619",
    "http://xttldmfg:72k2bib2ip3r@104.239.39.184:6113",
    "http://xttldmfg:72k2bib2ip3r@45.39.13.86:5523",
    "http://xttldmfg:72k2bib2ip3r@50.114.15.229:6214",
    "http://xttldmfg:72k2bib2ip3r@173.239.219.244:6153",
    "http://xttldmfg:72k2bib2ip3r@104.168.118.133:6089",
    "http://xttldmfg:72k2bib2ip3r@191.96.130.9:5772",
    "http://xttldmfg:72k2bib2ip3r@206.206.71.141:5781",
    "http://xttldmfg:72k2bib2ip3r@38.170.172.63:5064",
    "http://xttldmfg:72k2bib2ip3r@104.239.124.52:6330",
    "http://xttldmfg:72k2bib2ip3r@147.185.217.219:6653",
    "http://xttldmfg:72k2bib2ip3r@173.211.69.69:6662",
    "http://xttldmfg:72k2bib2ip3r@23.27.75.102:6182",
    "http://xttldmfg:72k2bib2ip3r@104.239.107.188:5840",
    "http://xttldmfg:72k2bib2ip3r@23.236.247.189:8221",
    "http://xttldmfg:72k2bib2ip3r@38.170.173.47:7598",
    "http://xttldmfg:72k2bib2ip3r@45.38.45.91:6030",
    "http://xttldmfg:72k2bib2ip3r@46.202.67.55:6051",
    "http://xttldmfg:72k2bib2ip3r@66.78.32.155:5205",
    "http://xttldmfg:72k2bib2ip3r@166.88.238.25:6005",
    "http://xttldmfg:72k2bib2ip3r@191.96.174.174:7260",
    "http://xttldmfg:72k2bib2ip3r@206.206.64.110:6071",
    "http://xttldmfg:72k2bib2ip3r@23.26.68.32:6015",
    "http://xttldmfg:72k2bib2ip3r@142.111.124.160:6180",
    "http://xttldmfg:72k2bib2ip3r@198.37.121.108:6528",
    "http://xttldmfg:72k2bib2ip3r@161.123.151.101:6085",
    "http://xttldmfg:72k2bib2ip3r@136.0.109.145:6431",
    "http://xttldmfg:72k2bib2ip3r@142.111.239.202:5780",
    "http://xttldmfg:72k2bib2ip3r@154.6.87.60:6530",
    "http://xttldmfg:72k2bib2ip3r@154.29.233.151:5912",
    "http://xttldmfg:72k2bib2ip3r@206.232.103.133:6290",
    "http://xttldmfg:72k2bib2ip3r@45.38.92.6:7927",
    "http://xttldmfg:72k2bib2ip3r@38.153.134.215:9884",
    "http://xttldmfg:72k2bib2ip3r@38.154.197.151:6817",
    "http://xttldmfg:72k2bib2ip3r@104.233.26.42:5880",
    "http://xttldmfg:72k2bib2ip3r@161.123.115.185:5206",
    "http://xttldmfg:72k2bib2ip3r@199.180.10.243:6614",
    "http://xttldmfg:72k2bib2ip3r@38.170.163.45:8101",
    "http://xttldmfg:72k2bib2ip3r@67.227.119.180:6509",
    "http://xttldmfg:72k2bib2ip3r@142.111.131.152:6230",
    "http://xttldmfg:72k2bib2ip3r@149.57.85.5:5973",
    "http://xttldmfg:72k2bib2ip3r@191.96.254.221:6268",
    "http://xttldmfg:72k2bib2ip3r@45.61.123.21:5700",
    "http://xttldmfg:72k2bib2ip3r@192.241.125.215:8259",
    "http://xttldmfg:72k2bib2ip3r@206.206.122.165:5796",
    "http://xttldmfg:72k2bib2ip3r@38.170.173.70:7621",
    "http://xttldmfg:72k2bib2ip3r@142.147.132.47:6242",
    "http://xttldmfg:72k2bib2ip3r@45.56.175.47:5721",
    "http://xttldmfg:72k2bib2ip3r@142.111.113.29:6390",
    "http://xttldmfg:72k2bib2ip3r@198.46.148.233:5921",
    "http://xttldmfg:72k2bib2ip3r@46.202.227.202:6196",
    "http://xttldmfg:72k2bib2ip3r@161.123.130.214:5885",
    "http://xttldmfg:72k2bib2ip3r@216.74.115.141:6735",
    "http://xttldmfg:72k2bib2ip3r@64.188.100.185:7933",
    "http://xttldmfg:72k2bib2ip3r@191.96.174.112:7198",
    "http://xttldmfg:72k2bib2ip3r@146.103.5.212:6792",
    "http://xttldmfg:72k2bib2ip3r@91.124.253.120:6480",
    "http://xttldmfg:72k2bib2ip3r@92.113.3.191:6200",
    "http://xttldmfg:72k2bib2ip3r@104.239.38.232:6765",
    "http://xttldmfg:72k2bib2ip3r@136.0.117.67:6805",
    "http://xttldmfg:72k2bib2ip3r@136.0.126.190:5951",
    "http://xttldmfg:72k2bib2ip3r@142.111.161.87:6458",
    "http://xttldmfg:72k2bib2ip3r@38.154.191.130:8707",
    "http://xttldmfg:72k2bib2ip3r@216.10.27.31:6709",
    "http://xttldmfg:72k2bib2ip3r@64.64.115.98:5733",
    "http://xttldmfg:72k2bib2ip3r@199.180.8.252:5963",
    "http://xttldmfg:72k2bib2ip3r@192.241.112.108:7610",
    "http://xttldmfg:72k2bib2ip3r@145.223.58.165:6434",
    "http://xttldmfg:72k2bib2ip3r@154.6.83.34:6505",
    "http://xttldmfg:72k2bib2ip3r@154.6.23.13:6480",
    "http://xttldmfg:72k2bib2ip3r@38.154.206.220:9711",
    "http://xttldmfg:72k2bib2ip3r@142.111.161.63:6434",
    "http://xttldmfg:72k2bib2ip3r@191.101.181.18:6771",
    "http://xttldmfg:72k2bib2ip3r@45.38.78.130:6067",
    "http://xttldmfg:72k2bib2ip3r@104.238.49.199:5853",
    "http://xttldmfg:72k2bib2ip3r@142.147.240.68:6590",
    "http://xttldmfg:72k2bib2ip3r@184.174.56.2:5014",
    "http://xttldmfg:72k2bib2ip3r@50.114.98.177:5661",
    "http://xttldmfg:72k2bib2ip3r@104.168.25.224:5906",
    "http://xttldmfg:72k2bib2ip3r@38.170.188.212:5785",
    "http://xttldmfg:72k2bib2ip3r@45.56.173.195:6178",
    "http://xttldmfg:72k2bib2ip3r@154.6.121.77:6044",
    "http://xttldmfg:72k2bib2ip3r@154.6.121.47:6014",
    "http://xttldmfg:72k2bib2ip3r@179.61.166.136:6559",
    "http://xttldmfg:72k2bib2ip3r@31.58.30.224:6806",
    "http://xttldmfg:72k2bib2ip3r@173.211.8.36:6148",
    "http://xttldmfg:72k2bib2ip3r@184.174.24.131:6707",
    "http://xttldmfg:72k2bib2ip3r@38.170.176.79:5474",
    "http://xttldmfg:72k2bib2ip3r@89.249.197.112:6698",
    "http://xttldmfg:72k2bib2ip3r@31.58.19.134:6406",
    "http://xttldmfg:72k2bib2ip3r@192.177.86.66:5067",
    "http://xttldmfg:72k2bib2ip3r@154.22.56.47:5088",
    "http://xttldmfg:72k2bib2ip3r@154.30.242.130:9524",
    "http://xttldmfg:72k2bib2ip3r@216.173.76.231:6858",
    "http://xttldmfg:72k2bib2ip3r@45.43.167.23:6205",
    "http://xttldmfg:72k2bib2ip3r@174.140.200.59:6339",
    "http://xttldmfg:72k2bib2ip3r@45.43.167.187:6369",
    "http://xttldmfg:72k2bib2ip3r@45.38.94.151:6072",
    "http://xttldmfg:72k2bib2ip3r@45.39.4.145:5570",
    "http://xttldmfg:72k2bib2ip3r@45.43.167.47:6229",
    "http://xttldmfg:72k2bib2ip3r@198.37.109.102:6209",
    "http://xttldmfg:72k2bib2ip3r@69.58.12.135:8140",
    "http://xttldmfg:72k2bib2ip3r@89.249.193.193:5931",
    "http://xttldmfg:72k2bib2ip3r@142.111.161.228:6599",
    "http://xttldmfg:72k2bib2ip3r@173.214.177.237:5928",
    "http://xttldmfg:72k2bib2ip3r@98.159.38.246:6546",
    "http://xttldmfg:72k2bib2ip3r@148.135.148.159:6152",
    "http://xttldmfg:72k2bib2ip3r@104.233.12.95:6646",
    "http://xttldmfg:72k2bib2ip3r@66.78.32.134:5184",
    "http://xttldmfg:72k2bib2ip3r@23.26.68.19:6002",
    "http://xttldmfg:72k2bib2ip3r@45.41.178.35:6256",
    "http://xttldmfg:72k2bib2ip3r@64.64.118.39:6622",
    "http://xttldmfg:72k2bib2ip3r@104.239.78.35:5980",
    "http://xttldmfg:72k2bib2ip3r@154.29.233.49:5810",
    "http://xttldmfg:72k2bib2ip3r@142.111.245.37:5904",
    "http://xttldmfg:72k2bib2ip3r@173.239.219.135:6044",
    "http://xttldmfg:72k2bib2ip3r@38.170.172.130:5131",
    "http://xttldmfg:72k2bib2ip3r@104.252.41.163:7100",
    "http://xttldmfg:72k2bib2ip3r@173.211.68.61:6343",
    "http://xttldmfg:72k2bib2ip3r@199.180.9.84:6104",
    "http://xttldmfg:72k2bib2ip3r@45.127.250.21:5630",
    "http://xttldmfg:72k2bib2ip3r@192.210.132.57:6027",
    "http://xttldmfg:72k2bib2ip3r@107.172.156.84:5732",
    "http://xttldmfg:72k2bib2ip3r@173.211.0.51:6544",
    "http://xttldmfg:72k2bib2ip3r@142.111.131.7:6085",
    "http://xttldmfg:72k2bib2ip3r@50.114.28.205:5690",
    "http://xttldmfg:72k2bib2ip3r@198.12.112.67:5078",
    "http://xttldmfg:72k2bib2ip3r@198.46.161.33:5083",
    "http://xttldmfg:72k2bib2ip3r@142.111.104.133:6143",
    "http://xttldmfg:72k2bib2ip3r@31.59.18.188:6769",
    "http://xttldmfg:72k2bib2ip3r@38.154.199.89:5243",
    "http://xttldmfg:72k2bib2ip3r@23.27.196.88:6457",
    "http://xttldmfg:72k2bib2ip3r@64.64.110.197:6720",
    "http://xttldmfg:72k2bib2ip3r@154.6.8.215:5682",
    "http://xttldmfg:72k2bib2ip3r@45.61.100.228:6496",
    "http://xttldmfg:72k2bib2ip3r@192.186.176.93:8143",
    "http://xttldmfg:72k2bib2ip3r@206.206.73.203:6819",
    "http://xttldmfg:72k2bib2ip3r@173.211.69.251:6844",
    "http://xttldmfg:72k2bib2ip3r@206.206.64.188:6149",
    "http://xttldmfg:72k2bib2ip3r@107.172.116.69:5525",
    "http://xttldmfg:72k2bib2ip3r@31.57.85.54:5740",
    "http://xttldmfg:72k2bib2ip3r@207.244.219.158:6414",
    "http://xttldmfg:72k2bib2ip3r@107.173.105.78:5765",
    "http://xttldmfg:72k2bib2ip3r@192.210.132.108:6078",
    "http://xttldmfg:72k2bib2ip3r@184.174.44.49:6475",
    "http://xttldmfg:72k2bib2ip3r@145.223.56.82:7134",
    "http://xttldmfg:72k2bib2ip3r@173.244.41.59:6243",
    "http://xttldmfg:72k2bib2ip3r@104.168.8.109:5562",
    "http://xttldmfg:72k2bib2ip3r@64.64.127.76:6029",
    "http://xttldmfg:72k2bib2ip3r@107.172.163.210:6726",
    "http://xttldmfg:72k2bib2ip3r@136.0.180.161:6182",
    "http://xttldmfg:72k2bib2ip3r@166.88.224.181:6079",
    "http://xttldmfg:72k2bib2ip3r@45.38.84.232:7168",
    "http://xttldmfg:72k2bib2ip3r@142.147.242.244:6223",
    "http://xttldmfg:72k2bib2ip3r@142.147.244.164:6408",
    "http://xttldmfg:72k2bib2ip3r@145.223.58.17:6286",
    "http://xttldmfg:72k2bib2ip3r@191.101.11.26:6424",
    "http://xttldmfg:72k2bib2ip3r@136.0.182.168:6238",
    "http://xttldmfg:72k2bib2ip3r@172.245.158.7:5960",
    "http://xttldmfg:72k2bib2ip3r@199.180.11.174:6911",
    "http://xttldmfg:72k2bib2ip3r@136.0.184.249:6670",
    "http://xttldmfg:72k2bib2ip3r@104.239.104.63:6287",
    "http://xttldmfg:72k2bib2ip3r@107.173.93.204:6158",
    "http://xttldmfg:72k2bib2ip3r@198.23.128.23:5651",
    "http://xttldmfg:72k2bib2ip3r@46.202.248.195:5689",
    "http://xttldmfg:72k2bib2ip3r@198.46.202.13:5293",
    "http://xttldmfg:72k2bib2ip3r@208.70.10.207:5979",
    "http://xttldmfg:72k2bib2ip3r@209.127.191.165:5239",
    "http://xttldmfg:72k2bib2ip3r@147.124.198.218:6077",
    "http://xttldmfg:72k2bib2ip3r@23.229.110.23:8551",
    "http://xttldmfg:72k2bib2ip3r@142.147.240.89:6611",
    "http://xttldmfg:72k2bib2ip3r@104.168.118.71:6027",
    "http://xttldmfg:72k2bib2ip3r@198.23.239.9:6415",
    "http://xttldmfg:72k2bib2ip3r@38.153.148.121:5392",
    "http://xttldmfg:72k2bib2ip3r@38.154.191.0:8577",
    "http://xttldmfg:72k2bib2ip3r@23.95.250.152:6425",
    "http://xttldmfg:72k2bib2ip3r@185.216.106.18:6095",
    "http://xttldmfg:72k2bib2ip3r@64.64.115.143:5778",
    "http://xttldmfg:72k2bib2ip3r@38.153.152.146:9496",
    "http://xttldmfg:72k2bib2ip3r@161.123.33.178:6201",
    "http://xttldmfg:72k2bib2ip3r@206.206.118.135:6373",
    "http://xttldmfg:72k2bib2ip3r@198.144.190.218:6065",
    "http://xttldmfg:72k2bib2ip3r@45.38.94.155:6076",
    "http://xttldmfg:72k2bib2ip3r@173.214.176.168:6139",
    "http://xttldmfg:72k2bib2ip3r@142.147.129.80:5689",
    "http://xttldmfg:72k2bib2ip3r@46.202.224.92:5644",
    "http://xttldmfg:72k2bib2ip3r@38.153.156.165:9848",
    "http://xttldmfg:72k2bib2ip3r@23.27.210.134:6504",
    "http://xttldmfg:72k2bib2ip3r@104.239.35.170:5852",
    "http://xttldmfg:72k2bib2ip3r@166.88.58.171:5896",
    "http://xttldmfg:72k2bib2ip3r@174.140.254.248:6839",
    "http://xttldmfg:72k2bib2ip3r@193.148.92.120:6047",
    "http://xttldmfg:72k2bib2ip3r@38.170.162.150:7205",
    "http://xttldmfg:72k2bib2ip3r@45.56.174.191:6444",
    "http://xttldmfg:72k2bib2ip3r@107.174.25.222:5676",
    "http://xttldmfg:72k2bib2ip3r@136.0.126.220:5981",
    "http://xttldmfg:72k2bib2ip3r@166.88.83.72:6729",
    "http://xttldmfg:72k2bib2ip3r@92.113.231.175:7260",
    "http://xttldmfg:72k2bib2ip3r@149.57.85.76:6044",
    "http://xttldmfg:72k2bib2ip3r@31.58.29.28:5994",
    "http://xttldmfg:72k2bib2ip3r@104.233.12.85:6636",
    "http://xttldmfg:72k2bib2ip3r@184.174.30.81:5750",
    "http://xttldmfg:72k2bib2ip3r@198.37.99.223:6014",
    "http://xttldmfg:72k2bib2ip3r@104.168.25.13:5695",
    "http://xttldmfg:72k2bib2ip3r@38.153.135.198:5578",
    "http://xttldmfg:72k2bib2ip3r@154.22.56.70:5111",
    "http://xttldmfg:72k2bib2ip3r@161.123.5.17:5066",
    "http://xttldmfg:72k2bib2ip3r@161.123.115.129:5150",
    "http://xttldmfg:72k2bib2ip3r@192.177.86.108:5109",
    "http://xttldmfg:72k2bib2ip3r@198.23.214.157:6424",
    "http://xttldmfg:72k2bib2ip3r@38.153.132.64:5171",
    "http://xttldmfg:72k2bib2ip3r@31.58.26.61:6644",
    "http://xttldmfg:72k2bib2ip3r@45.61.116.48:6726",
    "http://xttldmfg:72k2bib2ip3r@198.144.190.238:6085",
    "http://xttldmfg:72k2bib2ip3r@154.29.239.42:6081",
    "http://xttldmfg:72k2bib2ip3r@103.251.223.50:6029",
    "http://xttldmfg:72k2bib2ip3r@154.6.121.54:6021",
    "http://xttldmfg:72k2bib2ip3r@154.29.235.129:6470",
    "http://xttldmfg:72k2bib2ip3r@104.232.209.134:6092",
    "http://xttldmfg:72k2bib2ip3r@104.245.244.195:6635"
]



# Pick a random proxy
def get_random_proxy():
    return random.choice(proxies)


async def create_client():
    proxy_url = get_random_proxy()
    client = httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0),
        proxy=proxy_url  # ✅ ONLY proxy
    )
    return client


# --- FETCH WITH RETRIES ---
async def fetch_with_retries(method: str, url: str, **kwargs):
    retries = 3
    for attempt in range(retries):
        try:
            client = await create_client()
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2)
                continue
            raise e

# --- SCRAPE USER ---
async def scrape_user(username: str):
    url = INSTAGRAM_PROFILE_URL.format(username)
    response = await fetch_with_retries("GET", url)
    return response.json()["data"]["user"]

# --- SCRAPE POST (REEL) ---
async def scrape_post(url_or_shortcode: str):
    if "http" in url_or_shortcode:
        if "/reel/" in url_or_shortcode:
            shortcode = url_or_shortcode.split("/reel/")[-1].split("/")[0]
        elif "/p/" in url_or_shortcode:
            shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
        else:
            raise ValueError("Invalid Instagram URL format.")
    else:
        shortcode = url_or_shortcode

    variables = quote(json.dumps({
        'shortcode': shortcode,
        'fetch_tagged_user_count': None,
        'hoisted_comment_id': None,
        'hoisted_reply_id': None
    }, separators=(',', ':')))
    
    body = f"variables={variables}&doc_id={POST_DOCUMENT_ID}"
    response = await fetch_with_retries(
        "POST",
        INSTAGRAM_GRAPHQL_URL,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=body
    )
    return response.json()["data"]["xdt_shortcode_media"]

# --- SCRAPE USER POSTS ---
async def scrape_user_posts(username: str, max_pages: int = 1):
    all_posts = []
    variables = {
        "after": None,
        "before": None,
        "data": {
            "count": 12,
            "include_reel_media_seen_timestamp": True,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "first": 12,
        "last": None,
        "username": username,
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
        "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
    }

    prev_cursor = None
    page_count = 0

    while page_count < max_pages:
        body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={USER_POSTS_DOCUMENT_ID}"
        response = await fetch_with_retries(
            "POST",
            INSTAGRAM_GRAPHQL_URL,
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=body
        )
        data = response.json()
        posts = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]["edges"]

        for post in posts:
            all_posts.append(post["node"])

        page_info = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]["page_info"]
        if not page_info["has_next_page"] or page_info["end_cursor"] == prev_cursor:
            break

        prev_cursor = page_info["end_cursor"]
        variables["after"] = page_info["end_cursor"]
        page_count += 1

    return all_posts

# --- GET VIDEO FILE SIZE ---
async def get_video_file_size(url: str) -> float:
    proxy_url = get_random_proxy()
    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0),
        proxy=proxy_url  # ✅ ONLY proxy
    ) as client:
        response = await client.head(url)
        size_bytes = int(response.headers.get("content-length", 0))
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)


# --- LANGUAGE DETECTION ---
def safe_detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return "unknown"

# --- PARSE REEL DATA ---
async def parse_reel(data: dict) -> dict:
    raw = jmespath.search("""
    {
        id: id,
        shortcode: shortcode,
        username: owner.username,
        caption: edge_media_to_caption.edges[0].node.text,
        video_url: video_url,
        display_url: display_url,
        like_count: edge_media_preview_like.count,
        comment_count: edge_media_to_parent_comment.count,
        is_video: is_video,
        taken_at_timestamp: taken_at_timestamp,
        view_count: video_view_count,
        video_play_count: video_play_count,
        duration: video_duration,
        audio: clips_music_attribution_info.song_name
    }
    """, data)

    upload_date = datetime.utcfromtimestamp(raw['taken_at_timestamp']).strftime('%B %d, %Y')
    caption = raw.get('caption') or ""
    language = safe_detect_language(caption)
    hashtags = re.findall(r"#(\w+)", caption)
    file_size_mb = await get_video_file_size(raw['video_url'])

    return {
        "id": raw["id"],
        "shortcode": raw["shortcode"],
        "username": raw["username"],
        "caption": caption,
        "hashtags": hashtags,
        "language": language,
        "upload_date": upload_date,
        "video_url": raw["video_url"],
        "display_url": raw["display_url"],
        "file_size_mb": file_size_mb,
        "audio_title": raw.get("audio", "Original Audio"),
        "like_count": raw["like_count"],
        "comment_count": raw["comment_count"],
        "view_count": raw["view_count"],
        "duration_seconds": raw["duration"],
    }
