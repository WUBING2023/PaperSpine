# -*- coding: utf-8 -*-
import datetime, json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- city coordinates ----------------
# name -> (lng, lat, country, zh_display)
CITIES = {
    "Beijing":    (116.40, 39.90, "China", "北京"),
    "Shanghai":   (121.47, 31.23, "China", "上海"),
    "Hangzhou":   (120.15, 30.27, "China", "杭州"),
    "Shenzhen":   (114.06, 22.54, "China", "深圳"),
    "Guangzhou":  (113.26, 23.13, "China", "广州"),
    "Zhuhai":     (113.58, 22.27, "China", "珠海"),
    "Nanjing":    (118.80, 32.06, "China", "南京"),
    "Suzhou":     (120.62, 31.30, "China", "苏州"),
    "Wuxi":       (120.30, 31.57, "China", "无锡"),
    "Xuzhou":     (117.18, 34.26, "China", "徐州"),
    "Yangzhou":   (119.42, 32.39, "China", "扬州"),
    "Huai'an":    (119.02, 33.62, "China", "淮安"),
    "Wuhan":      (114.31, 30.59, "China", "武汉"),
    "Chengdu":    (104.07, 30.67, "China", "成都"),
    "Chongqing":  (106.55, 29.56, "China", "重庆"),
    "Xi'an":      (108.94, 34.34, "China", "西安"),
    "Hefei":      (117.28, 31.86, "China", "合肥"),
    "Wuhu":       (118.43, 31.35, "China", "芜湖"),
    "Huainan":    (117.00, 32.63, "China", "淮南"),
    "Tianjin":    (117.20, 39.08, "China", "天津"),
    "Changsha":   (112.94, 28.23, "China", "长沙"),
    "Xiangtan":   (112.94, 27.83, "China", "湘潭"),
    "Harbin":     (126.63, 45.80, "China", "哈尔滨"),
    "Changchun":  (125.32, 43.88, "China", "长春"),
    "Shenyang":   (123.43, 41.80, "China", "沈阳"),
    "Dalian":     (121.61, 38.91, "China", "大连"),
    "Qingdao":    (120.38, 36.07, "China", "青岛"),
    "Jinan":      (117.12, 36.65, "China", "济南"),
    "Zhengzhou":  (113.63, 34.75, "China", "郑州"),
    "Luoyang":    (112.45, 34.62, "China", "洛阳"),
    "Xiamen":     (118.09, 24.48, "China", "厦门"),
    "Fuzhou":     (119.30, 26.08, "China", "福州"),
    "Putian":     (119.01, 25.45, "China", "莆田"),
    "Kunming":    (102.83, 24.88, "China", "昆明"),
    "Nanchang":   (115.86, 28.68, "China", "南昌"),
    "Ningbo":     (121.55, 29.88, "China", "宁波"),
    "Wenzhou":    (120.70, 28.00, "China", "温州"),
    "Jinhua":     (119.65, 29.08, "China", "金华"),
    "Urumqi":     (87.62, 43.83, "China", "乌鲁木齐"),
    "Lanzhou":    (103.83, 36.06, "China", "兰州"),
    "Hohhot":     (111.75, 40.84, "China", "呼和浩特"),
    "Guiyang":    (106.63, 26.65, "China", "贵阳"),
    "Nanning":    (108.37, 22.82, "China", "南宁"),
    "Haikou":     (110.35, 20.02, "China", "海口"),
    "Sanya":      (109.51, 18.25, "China", "三亚"),
    "Shijiazhuang": (114.51, 38.04, "China", "石家庄"),
    "Baoding":    (115.46, 38.87, "China", "保定"),
    "Taiyuan":    (112.55, 37.87, "China", "太原"),
    "Xining":     (101.78, 36.62, "China", "西宁"),
    "Yinchuan":   (106.27, 38.47, "China", "银川"),
    "Lhasa":      (91.11, 29.65, "China", "拉萨"),
    "Hong Kong":  (114.17, 22.32, "China", "香港"),
    "Macau":      (113.55, 22.20, "China", "澳门"),
    "Taipei":     (121.56, 25.03, "China", "台北"),
    "Hsinchu":    (120.97, 24.81, "China", "新竹"),
    "China (city unspecified)": (103.5, 36.5, "China", "中国·未注明城市"),
    "Singapore":  (103.85, 1.29, "Singapore", "新加坡"),
    "Tokyo":      (139.69, 35.69, "Japan", "东京"),
    "Kochi":      (133.53, 33.56, "Japan", "高知"),
    "Seoul":      (126.98, 37.57, "South Korea", "首尔"),
    "Siheung":    (126.80, 37.38, "South Korea", "始兴"),
    "Penang":     (100.33, 5.41, "Malaysia", "槟城"),
    "Kuala Lumpur": (101.69, 3.14, "Malaysia", "吉隆坡"),
    "Moscow":     (37.62, 55.75, "Russia", "莫斯科"),
    "St. Petersburg": (30.32, 59.94, "Russia", "圣彼得堡"),
    "London":     (-0.13, 51.51, "United Kingdom", "伦敦"),
    "Durham (UK)": (-1.58, 54.78, "United Kingdom", "杜伦"),
    "Paris":      (2.35, 48.86, "France", "巴黎"),
    "Munich":     (11.58, 48.14, "Germany", "慕尼黑"),
    "Berlin":     (13.40, 52.52, "Germany", "柏林"),
    "Zurich":     (8.54, 47.38, "Switzerland", "苏黎世"),
    "Athens":     (23.73, 37.98, "Greece", "雅典"),
    "Sydney":     (151.21, -33.87, "Australia", "悉尼"),
    "Brisbane":   (153.03, -27.47, "Australia", "布里斯班"),
    "Melbourne":  (144.96, -37.81, "Australia", "墨尔本"),
    "Los Angeles": (-118.24, 34.05, "United States", "洛杉矶"),
    "San Francisco": (-122.42, 37.77, "United States", "旧金山"),
    "Chicago":    (-87.63, 41.88, "United States", "芝加哥"),
    "Chapel Hill": (-79.06, 35.91, "United States", "教堂山"),
    "Baltimore":  (-76.61, 39.29, "United States", "巴尔的摩"),
    "Louisville": (-85.76, 38.25, "United States", "路易斯维尔"),
    "New York":   (-74.01, 40.71, "United States", "纽约"),
    "Boston":     (-71.06, 42.36, "United States", "波士顿"),
    "Seattle":    (-122.33, 47.61, "United States", "西雅图"),
    "USA (city unspecified)": (-98.5, 39.8, "United States", "美国·未注明城市"),
    "Brasilia":   (-47.88, -15.79, "Brazil", "巴西利亚"),
    "Beni Mellal": (-6.35, 32.34, "Morocco", "贝尼迈拉勒"),
    "Kaifeng":    (114.31, 34.80, "China", "开封"),
    "Bengbu":     (117.39, 32.92, "China", "蚌埠"),
    "Datong":     (113.30, 40.08, "China", "大同"),
    "Huzhou":     (120.09, 30.89, "China", "湖州"),
    "Vienna":     (16.37, 48.21, "Austria", "维也纳"),
    "Madrid":     (-3.70, 40.42, "Spain", "马德里"),
    "Barcelona":  (2.17, 41.39, "Spain", "巴塞罗那"),
    "Poznan":     (16.93, 52.41, "Poland", "波兹南"),
    "Portsmouth": (-1.09, 50.80, "United Kingdom", "朴次茅斯"),
    "Huddersfield": (-1.78, 53.65, "United Kingdom", "哈德斯菲尔德"),
    "Ankara":     (32.85, 39.93, "Turkey", "安卡拉"),
    "Malatya":    (38.32, 38.35, "Turkey", "马拉蒂亚"),
    "Riyadh":     (46.72, 24.69, "Saudi Arabia", "利雅得"),
    "Bangkok":    (100.50, 13.76, "Thailand", "曼谷"),
    "Suwon":      (127.03, 37.26, "South Korea", "水原"),
    "New Delhi":  (77.21, 28.61, "India", "新德里"),
    "Jakarta":    (106.85, -6.21, "Indonesia", "雅加达"),
    "Perth":      (115.86, -31.95, "Australia", "珀斯"),
    "Sao Paulo":  (-46.63, -23.55, "Brazil", "圣保罗"),
    "Dakar":      (-17.44, 14.69, "Senegal", "达喀尔"),
    "San Jose":   (-121.89, 37.34, "United States", "圣何塞"),
    "Irvine":     (-117.83, 33.68, "United States", "尔湾"),
    "Albuquerque": (-106.65, 35.08, "United States", "阿尔伯克基"),
    "Telluride":  (-107.81, 37.94, "United States", "特柳赖德"),
    "Ames":       (-93.62, 42.03, "United States", "埃姆斯"),
    "Ridgecrest": (-117.67, 35.62, "United States", "里奇克莱斯特"),
    "Belfast":    (-5.93, 54.60, "United Kingdom", "贝尔法斯特"),
    "Leicester":  (-1.13, 52.64, "United Kingdom", "莱斯特"),
    "Manchester": (-2.24, 53.48, "United Kingdom", "曼彻斯特"),
    "Prague":     (14.42, 50.09, "Czechia", "布拉格"),
    "Budapest":   (19.04, 47.50, "Hungary", "布达佩斯"),
    "Toronto":    (-79.38, 43.65, "Canada", "多伦多"),
    "Osaka":      (135.50, 34.69, "Japan", "大阪"),
    "Windhoek":   (17.08, -22.56, "Namibia", "温得和克"),
    "Ponta Grossa": (-50.16, -25.09, "Brazil", "蓬塔格罗萨"),
}

# location-substring -> city key (checked longest-first, lowercase)
LOC_PATTERNS = {
    "jinan university": "Guangzhou",  # 暨南大学在广州
    "zhuhai": "Zhuhai",
    "terra cotta warriors": "Xi'an",
    "xidian": "Xi'an", "xi'an": "Xi'an", "xian": "Xi'an", "西安": "Xi'an",
    "beijing": "Beijing", "北京": "Beijing", "haidian": "Beijing", "tsinghua": "Beijing", "tshinghua": "Beijing", "renmin university": "Beijing", "beihang": "Beijing",
    "shanghai": "Shanghai", "上海": "Shanghai", "fudan": "Shanghai",
    "hangzhou": "Hangzhou", "杭州": "Hangzhou", "yuhangtang": "Hangzhou", "xihu district": "Hangzhou",
    "shenzhen": "Shenzhen", "深圳": "Shenzhen",
    "guangzhou": "Guangzhou", "广州": "Guangzhou", "south china university": "Guangzhou",
    "nanjing": "Nanjing", "南京": "Nanjing", "xianlin avenue": "Nanjing", "southeast university": "Nanjing",
    "suzhou": "Suzhou", "苏州": "Suzhou",
    "wuxi": "Wuxi", "无锡": "Wuxi",
    "xuzhou": "Xuzhou", "china university of mining": "Xuzhou",
    "yangzhou": "Yangzhou", "扬州": "Yangzhou",
    "wuhan": "Wuhan", "武汉": "Wuhan", "luoyu road": "Wuhan", "hongshan district": "Wuhan",
    "chengdu": "Chengdu", "成都": "Chengdu", "sichuan": "Chengdu",
    "chongqing": "Chongqing", "重庆": "Chongqing",
    "hefei": "Hefei", "hefe": "Hefei", "合肥": "Hefei", "anhui": "Hefei", "shushan district": "Hefei",
    "huainan": "Huainan", "淮南": "Huainan",
    "tianjin": "Tianjin", "天津": "Tianjin", "dongli district": "Tianjin",
    "changsha": "Changsha", "长沙": "Changsha", "hunan": "Changsha",
    "harbin": "Harbin", "哈尔滨": "Harbin", "heilongjiang": "Harbin",
    "changchun": "Changchun", "长春": "Changchun", "jilin": "Changchun", "吉林": "Changchun",
    "shenyang": "Shenyang", "shen yang": "Shenyang", "沈阳": "Shenyang", "liaoning": "Shenyang", "辽宁": "Shenyang",
    "dalian": "Dalian", "大连": "Dalian", "ganjingzi": "Dalian",
    "qingdao": "Qingdao", "青岛": "Qingdao",
    "jinan": "Jinan", "济南": "Jinan", "zhangqiu": "Jinan", "shandong": "Jinan", "山东": "Jinan",
    "zhengzhou": "Zhengzhou", "郑州": "Zhengzhou", "henan": "Zhengzhou", "河南": "Zhengzhou",
    "luoyang": "Luoyang", "洛阳": "Luoyang",
    "xiamen": "Xiamen", "厦门": "Xiamen",
    "fuzhou": "Fuzhou", "福州": "Fuzhou", "fujian": "Fuzhou",
    "putian": "Putian",
    "kunming": "Kunming", "昆明": "Kunming", "yunnan": "Kunming", "云南": "Kunming",
    "nanchang": "Nanchang", "jiangxi": "Nanchang", "江西": "Nanchang",
    "ningbo": "Ningbo", "宁波": "Ningbo",
    "wenzhou": "Wenzhou", "温州": "Wenzhou",
    "urumqi": "Urumqi", "xinjiang": "Urumqi", "新疆": "Urumqi",
    "lanzhou": "Lanzhou", "兰州": "Lanzhou", "gansu": "Lanzhou", "甘肃": "Lanzhou",
    "hohhot": "Hohhot", "inner mongolia": "Hohhot", "内蒙古": "Hohhot",
    "guiyang": "Guiyang", "guizhou": "Guiyang", "贵州": "Guiyang",
    "nanning": "Nanning", "guangxi": "Nanning", "广西": "Nanning",
    "haikou": "Haikou", "hainan": "Haikou", "海南": "Haikou",
    "sanya": "Sanya", "三亚": "Sanya",
    "shijiazhuang": "Shijiazhuang", "石家庄": "Shijiazhuang",
    "baoding": "Baoding", "保定": "Baoding", "hebei": "Shijiazhuang", "河北": "Shijiazhuang",
    "taiyuan": "Taiyuan", "shanxi": "Taiyuan", "山西": "Taiyuan",
    "xining": "Xining", "qinghai": "Xining", "青海": "Xining",
    "yinchuan": "Yinchuan", "ningxia": "Yinchuan", "宁夏": "Yinchuan",
    "lhasa": "Lhasa", "tibet": "Lhasa", "西藏": "Lhasa",
    "hong kong": "Hong Kong", "hongkong": "Hong Kong", "香港": "Hong Kong",
    "macau": "Macau", "macao": "Macau", "澳门": "Macau",
    "taipei": "Taipei", "台北": "Taipei", "taiwan": "Taipei", "台湾": "Taipei",
    "hsinchu": "Hsinchu", "新竹": "Hsinchu",
    "jiangsu": "Nanjing", "江苏": "Nanjing",
    "zhejiang": "Hangzhou", "浙江": "Hangzhou",
    "guangdong": "Guangzhou", "广东": "Guangzhou",
    "hubei": "Wuhan", "湖北": "Wuhan",
    "shaanxi": "Xi'an", "陕西": "Xi'an",
    "singapore": "Singapore", "新加坡": "Singapore",
    "tokyo": "Tokyo", "东京": "Tokyo",
    "kochi": "Kochi",
    "seoul": "Seoul",
    "penang": "Penang",
    "kuala lumpur": "Kuala Lumpur", "malaysia": "Kuala Lumpur",
    "moscow": "Moscow",
    "petersburg": "St. Petersburg",
    "london": "London",
    "durham": "Durham (UK)",
    "paris": "Paris",
    "munich": "Munich", "münchen": "Munich",
    "berlin": "Berlin",
    "zurich": "Zurich",
    "athens": "Athens", "greece": "Athens",
    "sydney": "Sydney",
    "brisbane": "Brisbane",
    "melbourne": "Melbourne", "parkville": "Melbourne",
    "los angeles": "Los Angeles",
    "san francisco": "San Francisco", "bay area": "San Francisco",
    "chicago": "Chicago",
    "chapel hill": "Chapel Hill",
    "baltimore": "Baltimore",
    "louisville": "Louisville",
    "new york": "New York",
    "boston": "Boston",
    "seattle": "Seattle",
    "brazil": "Brasilia",
    "beni mellal": "Beni Mellal", "morocco": "Beni Mellal",
    "kaifeng": "Kaifeng", "开封": "Kaifeng",
    "bengbu": "Bengbu", "蚌埠": "Bengbu",
    "datong": "Datong", "大同": "Datong",
    "huzhou": "Huzhou", "湖州": "Huzhou",
    "academy of sciences": "Beijing", "ucas": "Beijing",
    "northeastern university": "Shenyang",
    "central south university": "Changsha",
    "austria": "Vienna", "vienna": "Vienna",
    "madrid": "Madrid", "spain": "Madrid",
    "barcelona": "Barcelona",
    "pozna": "Poznan",
    "portsmouth": "Portsmouth",
    "huddersfield": "Huddersfield",
    "ankara": "Ankara",
    "malatya": "Malatya",
    "riyadh": "Riyadh", "saudi arabia": "Riyadh",
    "bangkok": "Bangkok", "thailand": "Bangkok",
    "suwon": "Suwon",
    "india": "New Delhi",
    "indonesia": "Jakarta",
    "western australia": "Perth", "perth": "Perth",
    "são paulo": "Sao Paulo", "sao paulo": "Sao Paulo",
    "dakar": "Dakar",
    "san jose": "San Jose", "redwood city": "San Jose",
    "irvine": "Irvine",
    "albuquerque": "Albuquerque",
    "telluride": "Telluride",
    "ames": "Ames",
    "ridgecrest": "Ridgecrest",
    "cambridge, ma": "Boston", "cambridge,ma": "Boston",
    "belfast": "Belfast",
    "leicester": "Leicester",
    "manchester": "Manchester",
    "france": "Paris",
    "donghua university": "Shanghai",
    "canada": "Toronto", "toronto": "Toronto",
    "windhoek": "Windhoek",
    "osaka": "Osaka",
    "czech": "Prague", "prague": "Prague",
    "budapest": "Budapest", "hungary": "Budapest",
    "ponta grossa": "Ponta Grossa",
    "hk": "Hong Kong",
    "switzerland": "Zurich",
    "united states": "USA (city unspecified)", "usa": "USA (city unspecified)",
    "china": "China (city unspecified)", "中国": "China (city unspecified)", "p.r.c": "China (city unspecified)", "prc": "China (city unspecified)", "cn": "China (city unspecified)",
    "us": "USA (city unspecified)",
}

# ---------------- org aliases ----------------
# lowercase alias -> (canonical_en, zh, type, city)   type: school | company
S, C = "school", "company"
ORG_ALIASES = {
    "tsinghua university": ("Tsinghua University", "清华大学", S, "Beijing"),
    "tsinghua": ("Tsinghua University", "清华大学", S, "Beijing"),
    "tshinghua university": ("Tsinghua University", "清华大学", S, "Beijing"),
    "thu": ("Tsinghua University", "清华大学", S, "Beijing"),
    "peking university": ("Peking University", "北京大学", S, "Beijing"),
    "pku": ("Peking University", "北京大学", S, "Beijing"),
    "zhejiang university": ("Zhejiang University", "浙江大学", S, "Hangzhou"),
    "zhejiang univesity": ("Zhejiang University", "浙江大学", S, "Hangzhou"),
    "zju": ("Zhejiang University", "浙江大学", S, "Hangzhou"),
    "xidian university": ("Xidian University", "西安电子科技大学", S, "Xi'an"),
    "xidian": ("Xidian University", "西安电子科技大学", S, "Xi'an"),
    "university of chinese academy of sciences": ("University of Chinese Academy of Sciences", "中国科学院大学", S, "Beijing"),
    "ucas": ("University of Chinese Academy of Sciences", "中国科学院大学", S, "Beijing"),
    "beihang university": ("Beihang University", "北京航空航天大学", S, "Beijing"),
    "buaa": ("Beihang University", "北京航空航天大学", S, "Beijing"),
    "harbin institute of technology": ("Harbin Institute of Technology", "哈尔滨工业大学", S, "Harbin"),
    "hit": ("Harbin Institute of Technology", "哈尔滨工业大学", S, "Harbin"),
    "tongji university": ("Tongji University", "同济大学", S, "Shanghai"),
    "xi'an jiaotong university": ("Xi'an Jiaotong University", "西安交通大学", S, "Xi'an"),
    "xjtu": ("Xi'an Jiaotong University", "西安交通大学", S, "Xi'an"),
    "dalian university of technology": ("Dalian University of Technology", "大连理工大学", S, "Dalian"),
    "dlut": ("Dalian University of Technology", "大连理工大学", S, "Dalian"),
    "southeast university": ("Southeast University", "东南大学", S, "Nanjing"),
    "seu": ("Southeast University", "东南大学", S, "Nanjing"),
    "fudan university": ("Fudan University", "复旦大学", S, "Shanghai"),
    "fudan": ("Fudan University", "复旦大学", S, "Shanghai"),
    "nanjing university of aeronautics and astronautics": ("Nanjing University of Aeronautics and Astronautics", "南京航空航天大学", S, "Nanjing"),
    "nuaa": ("Nanjing University of Aeronautics and Astronautics", "南京航空航天大学", S, "Nanjing"),
    "national university of defense technology": ("National University of Defense Technology", "国防科技大学", S, "Changsha"),
    "nudt": ("National University of Defense Technology", "国防科技大学", S, "Changsha"),
    "yunnan university": ("Yunnan University", "云南大学", S, "Kunming"),
    "beijing institute of technology": ("Beijing Institute of Technology", "北京理工大学", S, "Beijing"),
    "bit": ("Beijing Institute of Technology", "北京理工大学", S, "Beijing"),
    "south china university of technology": ("South China University of Technology", "华南理工大学", S, "Guangzhou"),
    "scut": ("South China University of Technology", "华南理工大学", S, "Guangzhou"),
    "hangzhou dianzi university": ("Hangzhou Dianzi University", "杭州电子科技大学", S, "Hangzhou"),
    "hdu": ("Hangzhou Dianzi University", "杭州电子科技大学", S, "Hangzhou"),
    "nanjing university": ("Nanjing University", "南京大学", S, "Nanjing"),
    "nju": ("Nanjing University", "南京大学", S, "Nanjing"),
    "university of science and technology of china": ("University of Science and Technology of China", "中国科学技术大学", S, "Hefei"),
    "ustc": ("University of Science and Technology of China", "中国科学技术大学", S, "Hefei"),
    "huazhong university of science and technology": ("Huazhong University of Science and Technology", "华中科技大学", S, "Wuhan"),
    "huazhong university of science of technology": ("Huazhong University of Science and Technology", "华中科技大学", S, "Wuhan"),
    "hust": ("Huazhong University of Science and Technology", "华中科技大学", S, "Wuhan"),
    "zhejiang university of technology": ("Zhejiang University of Technology", "浙江工业大学", S, "Hangzhou"),
    "wuhan university": ("Wuhan University", "武汉大学", S, "Wuhan"),
    "whu": ("Wuhan University", "武汉大学", S, "Wuhan"),
    "beijing university of posts and telecommunications": ("Beijing University of Posts and Telecommunications", "北京邮电大学", S, "Beijing"),
    "bupt": ("Beijing University of Posts and Telecommunications", "北京邮电大学", S, "Beijing"),
    "shanghai jiao tong university": ("Shanghai Jiao Tong University", "上海交通大学", S, "Shanghai"),
    "sjtu": ("Shanghai Jiao Tong University", "上海交通大学", S, "Shanghai"),
    "university of electronic science and technology of china": ("University of Electronic Science and Technology of China", "电子科技大学", S, "Chengdu"),
    "uestc": ("University of Electronic Science and Technology of China", "电子科技大学", S, "Chengdu"),
    "northeastern university": ("Northeastern University (China)", "东北大学", S, "Shenyang"),
    "tiangong university": ("Tiangong University", "天津工业大学", S, "Tianjin"),
    "yangzhou university": ("Yangzhou University", "扬州大学", S, "Yangzhou"),
    "xiamen university": ("Xiamen University", "厦门大学", S, "Xiamen"),
    "hohai university": ("Hohai University", "河海大学", S, "Nanjing"),
    "inner mongolia university": ("Inner Mongolia University", "内蒙古大学", S, "Hohhot"),
    "xinjiang university": ("Xinjiang University", "新疆大学", S, "Urumqi"),
    "university of science and technology beijing": ("University of Science and Technology Beijing", "北京科技大学", S, "Beijing"),
    "北京科技大学": ("University of Science and Technology Beijing", "北京科技大学", S, "Beijing"),
    "china agricultural university": ("China Agricultural University", "中国农业大学", S, "Beijing"),
    "henan university of science and technology": ("Henan University of Science and Technology", "河南科技大学", S, "Luoyang"),
    "xjtlu": ("Xi'an Jiaotong-Liverpool University", "西交利物浦大学", S, "Suzhou"),
    "chongqing university": ("Chongqing University", "重庆大学", S, "Chongqing"),
    "shenyang university of technology": ("Shenyang University of Technology", "沈阳工业大学", S, "Shenyang"),
    "beijing jiaotong university": ("Beijing Jiaotong University", "北京交通大学", S, "Beijing"),
    "beijing normal university": ("Beijing Normal University", "北京师范大学", S, "Beijing"),
    "chengdu university of traditional chinese medicine": ("Chengdu University of TCM", "成都中医药大学", S, "Chengdu"),
    "nanjing normal university": ("Nanjing Normal University", "南京师范大学", S, "Nanjing"),
    "ntu": ("Nanyang Technological University", "南洋理工大学", S, "Singapore"),
    "cnu": ("Capital Normal University", "首都师范大学", S, "Beijing"),
    "chengdu technological university": ("Chengdu Technological University", "成都工业学院", S, "Chengdu"),
    "hefei university of technology": ("Hefei University of Technology", "合肥工业大学", S, "Hefei"),
    "soochow university": ("Soochow University", "苏州大学", S, "Suzhou"),
    "lanzhou university of technology": ("Lanzhou University of Technology", "兰州理工大学", S, "Lanzhou"),
    "johns hopkins university": ("Johns Hopkins University", "约翰斯·霍普金斯大学", S, "Baltimore"),
    "changsha university of science & technology": ("Changsha University of Science & Technology", "长沙理工大学", S, "Changsha"),
    "china jiliang university": ("China Jiliang University", "中国计量大学", S, "Hangzhou"),
    "jilin university": ("Jilin University", "吉林大学", S, "Changchun"),
    "吉林大学": ("Jilin University", "吉林大学", S, "Changchun"),
    "jlu-solar": ("Jilin University", "吉林大学", S, "Changchun"),
    "tianjin university": ("Tianjin University", "天津大学", S, "Tianjin"),
    "shanghai innovation institute": ("Shanghai Innovation Institute", "上海创智学院", S, "Shanghai"),
    "shaanxi normal university": ("Shaanxi Normal University", "陕西师范大学", S, "Xi'an"),
    "southwest university": ("Southwest University", "西南大学", S, "Chongqing"),
    "civil aviation university of china": ("Civil Aviation University of China", "中国民航大学", S, "Tianjin"),
    "shanghai ocean university": ("Shanghai Ocean University", "上海海洋大学", S, "Shanghai"),
    "fudan university": ("Fudan University", "复旦大学", S, "Shanghai"),
    "wuhan university of technology": ("Wuhan University of Technology", "武汉理工大学", S, "Wuhan"),
    "kochi university of technology": ("Kochi University of Technology", "高知工科大学", S, "Kochi"),
    "technical university of munich": ("Technical University of Munich", "慕尼黑工业大学", S, "Munich"),
    "university of louisville": ("University of Louisville", "路易斯维尔大学", S, "Louisville"),
    "nanjing university of chinese medicine": ("Nanjing University of Chinese Medicine", "南京中医药大学", S, "Nanjing"),
    "isa-cas": ("Chinese Academy of Sciences", "中国科学院", S, "Beijing"),
    "lomonosov moscow state university": ("Lomonosov Moscow State University", "莫斯科国立大学", S, "Moscow"),
    "xiamen university of technology": ("Xiamen University of Technology", "厦门理工学院", S, "Xiamen"),
    "st. petersburg state university": ("St. Petersburg State University", "圣彼得堡国立大学", S, "St. Petersburg"),
    "the hong kong university of science and technology （guangzhou）": ("HKUST (Guangzhou)", "香港科技大学（广州）", S, "Guangzhou"),
    "the hong kong university of science and technology": ("HKUST", "香港科技大学", S, "Hong Kong"),
    "harbin engineering university": ("Harbin Engineering University", "哈尔滨工程大学", S, "Harbin"),
    "north china electric power university": ("North China Electric Power University", "华北电力大学", S, "Beijing"),
    "tianjin university of technology": ("Tianjin University of Technology", "天津理工大学", S, "Tianjin"),
    "fuzhou university": ("Fuzhou University", "福州大学", S, "Fuzhou"),
    "zhengzhou university": ("Zhengzhou University", "郑州大学", S, "Zhengzhou"),
    "山东建筑大学": ("Shandong Jianzhu University", "山东建筑大学", S, "Jinan"),
    "anhui university": ("Anhui University", "安徽大学", S, "Hefei"),
    "nanjing university of posts and telecommunications": ("Nanjing University of Posts and Telecommunications", "南京邮电大学", S, "Nanjing"),
    "南京邮电大学": ("Nanjing University of Posts and Telecommunications", "南京邮电大学", S, "Nanjing"),
    "njupt": ("Nanjing University of Posts and Telecommunications", "南京邮电大学", S, "Nanjing"),
    "university of melbourne": ("University of Melbourne", "墨尔本大学", S, "Melbourne"),
    "hebei university": ("Hebei University", "河北大学", S, "Baoding"),
    "waseda university": ("Waseda University", "早稻田大学", S, "Tokyo"),
    "unc, chapel hill": ("UNC Chapel Hill", "北卡罗来纳大学教堂山分校", S, "Chapel Hill"),
    "anhui university of science and technology": ("Anhui University of Science and Technology", "安徽理工大学", S, "Huainan"),
    "dalian maritime university": ("Dalian Maritime University", "大连海事大学", S, "Dalian"),
    "universiti sains malaysia": ("Universiti Sains Malaysia", "马来西亚理科大学", S, "Penang"),
    "imperial college": ("Imperial College London", "帝国理工学院", S, "London"),
    "renmin university of china": ("Renmin University of China", "中国人民大学", S, "Beijing"),
    "china university of mining and technology": ("China University of Mining and Technology", "中国矿业大学", S, "Xuzhou"),
    "tech university of korea": ("Tech University of Korea", "韩国工业大学", S, "Siheung"),
    "jiangxi university of finance and economics": ("Jiangxi University of Finance and Economics", "江西财经大学", S, "Nanchang"),
    "广州航海学院": ("Guangzhou Maritime University", "广州航海学院", S, "Guangzhou"),
    "温州大学": ("Wenzhou University", "温州大学", S, "Wenzhou"),
    "sun yat-sen university": ("Sun Yat-sen University", "中山大学", S, "Guangzhou"),
    "sysu": ("Sun Yat-sen University", "中山大学", S, "Guangzhou"),
    "shenzhen university": ("Shenzhen University", "深圳大学", S, "Shenzhen"),
    "moulay slimane university": ("Moulay Slimane University", "穆莱·斯利曼大学", S, "Beni Mellal"),
    "hainan normal university": ("Hainan Normal University", "海南师范大学", S, "Haikou"),
    "jinan university": ("Jinan University", "暨南大学", S, "Guangzhou"),
    "southwest petroleum university": ("Southwest Petroleum University", "西南石油大学", S, "Chengdu"),
    "jiangnan university": ("Jiangnan University", "江南大学", S, "Wuxi"),
    "xtu": ("Xiangtan University", "湘潭大学", S, "Xiangtan"),
    "center south university": ("Central South University", "中南大学", S, "Changsha"),
    "central south university": ("Central South University", "中南大学", S, "Changsha"),
    "csu": ("Central South University", "中南大学", S, "Changsha"),
    "ocean university of china": ("Ocean University of China", "中国海洋大学", S, "Qingdao"),
    "zhejiang normal university": ("Zhejiang Normal University", "浙江师范大学", S, "Jinhua"),
    "hefei normal university": ("Hefei Normal University", "合肥师范学院", S, "Hefei"),
    "zhejiang gongshang university": ("Zhejiang Gongshang University", "浙江工商大学", S, "Hangzhou"),
    "minjiang univercity": ("Minjiang University", "闽江学院", S, "Fuzhou"),
    "淮阴工学院": ("Huaiyin Institute of Technology", "淮阴工学院", S, "Huai'an"),
    "jxnu": ("Jiangxi Normal University", "江西师范大学", S, "Nanchang"),
    "wuhan university of science and technology": ("Wuhan University of Science and Technology", "武汉科技大学", S, "Wuhan"),
    "anhui normal university": ("Anhui Normal University", "安徽师范大学", S, "Wuhu"),
    "qingdao university of technology": ("Qingdao University of Technology", "青岛理工大学", S, "Qingdao"),
    "universiti malaya": ("Universiti Malaya", "马来亚大学", S, "Kuala Lumpur"),
    "guangdong university of technology": ("Guangdong University of Technology", "广东工业大学", S, "Guangzhou"),
    "ecnu": ("East China Normal University", "华东师范大学", S, "Shanghai"),
    "upc": ("China University of Petroleum", "中国石油大学", S, "Qingdao"),
    "putian university": ("Putian University", "莆田学院", S, "Putian"),
    "sari": ("Shanghai Advanced Research Institute, CAS", "中科院上海高等研究院", S, "Shanghai"),
    "kunming institute of zoology, cas": ("Kunming Institute of Zoology, CAS", "中科院昆明动物研究所", S, "Kunming"),
    "meituan": ("Meituan", "美团", C, "Beijing"),
    "wex inc.": ("WEX Inc.", "WEX Inc.", C, None),
    "act digital": ("Act Digital", "Act Digital", C, None),
    "carcinize corp": ("Carcinize Corp", "Carcinize Corp", C, None),
    "giftakis.gr": ("Giftakis.gr", "Giftakis.gr", C, "Athens"),
}

SKIP_ORGS = {"china", "none", "no", "n/a", "-", "student", "research graduate",
             "graduate students work in artificial intelligence", "individual", "freelance", "home"}

SCHOOL_KW = ["university", "univ", "universiti", "università", "universität", "universidade",
             "college", "institute", "academy", "school", "cas", "大学", "学院", "中学", "研究所", "研究院", "科学院"]
COMPANY_KW = ["inc", "ltd", "llc", "corp", "co.", "tech", "technology co", "software", "group",
              "lab", "labs", "studio", "公司", "科技", "集团"]

def norm_org(raw):
    s = raw.strip().strip(".,;")
    s = re.sub(r"\s+", " ", s)
    key = s.lstrip("@").lower().strip()
    if key in SKIP_ORGS or not key:
        return None
    if key not in ORG_ALIASES:
        head = re.split(r"[,;（(]", key)[0].strip()
        if head in ORG_ALIASES:
            key = head
        elif "chinese academy of sciences" in key or key.startswith("ucas"):
            key = "ucas"
    if key in ORG_ALIASES:
        en, zh, t, city = ORG_ALIASES[key]
        return {"en": en, "zh": zh, "type": t, "city": city}
    low = key
    is_school = any(k in low for k in SCHOOL_KW)
    t = S if is_school else C
    display = s.lstrip("@")
    if display.isupper() and len(display) > 6:
        display = display.title()
    elif display.islower():
        display = display.title()
    return {"en": display, "zh": display, "type": t, "city": None}

def locate(loc):
    low = loc.lower()
    for pat in sorted(LOC_PATTERNS, key=len, reverse=True):
        if pat in ("us", "cn", "usa", "prc", "hk", "ames", "ucas", "india"):
            if re.search(r"(?<![a-z])" + re.escape(pat) + r"(?![a-z])", low):
                return LOC_PATTERNS[pat]
            continue
        if pat in low:
            return LOC_PATTERNS[pat]
    return None

def main():
    users = json.load(open(os.path.join(HERE, "stargazers_raw.json"), encoding="utf-8"))
    if not users:
        raise RuntimeError("stargazers_raw.json is empty; refusing to generate an empty atlas")
    city_agg = {}
    org_agg = {}
    located = 0
    unmatched_loc = collections.Counter()

    for u in users:
        org = norm_org(u["company"]) if u.get("company") else None
        city = org["city"] if org and org["city"] else None
        if city is None and u.get("location"):
            city = locate(u["location"])
            if city is None:
                unmatched_loc[u["location"].strip()] += 1

        if org:
            k = org["en"]
            o = org_agg.setdefault(k, {"en": org["en"], "zh": org["zh"], "type": org["type"],
                                       "count": 0, "cities": collections.Counter()})
            o["count"] += 1
            if city:
                o["cities"][city] += 1

        if city:
            located += 1
            lng, lat, country, zh = CITIES[city]
            if lng < -30:
                lng += 360
            c = city_agg.setdefault(city, {"name": city, "zh": zh, "lng": lng, "lat": lat,
                                           "country": country, "count": 0,
                                           "schools": collections.Counter(), "companies": collections.Counter()})
            c["count"] += 1
            if org:
                disp = org["zh"] if re.search(r"[一-鿿]", org["zh"]) else org["en"]
                (c["schools"] if org["type"] == S else c["companies"])[disp] += 1

    for c in city_agg.values():
        c["schools"] = sorted(c["schools"].items(), key=lambda kv: -kv[1])
        c["companies"] = sorted(c["companies"].items(), key=lambda kv: -kv[1])

    schools, companies = [], []
    for o in org_agg.values():
        city = o["cities"].most_common(1)[0][0] if o["cities"] else None
        item = {"en": o["en"], "zh": o["zh"], "count": o["count"],
                "city": (CITIES[city][3] if city else "")}
        (schools if o["type"] == S else companies).append(item)
    schools.sort(key=lambda x: (-x["count"], x["en"]))
    companies.sort(key=lambda x: (-x["count"], x["en"]))

    countries = collections.Counter()
    for c in city_agg.values():
        countries[c["country"]] += c["count"]

    data = {
        "repo": "WUBING2023/PaperSpine",
        "generated": datetime.date.today().isoformat(),
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "totalStars": len(users),
        "located": located,
        "withOrg": sum(1 for u in users if u.get("company") and norm_org(u["company"])),
        "schoolCount": len(schools),
        "companyCount": len(companies),
        "countryCount": len(countries),
        "cities": sorted(city_agg.values(), key=lambda c: -c["count"]),
        "schools": schools,
        "companies": companies,
        "countries": dict(countries.most_common()),
    }
    def write_data(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("window.ATLAS=")
            json.dump(data, f, ensure_ascii=False)
            f.write(";")

    write_data(os.path.join(HERE, "data.js"))
    # The V5 release page embeds website/community/, a separate view of this same
    # dataset. Publish into it here so the two copies can never drift apart.
    community_data = os.path.normpath(
        os.path.join(HERE, os.pardir, "website", "community", "data.js")
    )
    if os.path.isdir(os.path.dirname(community_data)):
        write_data(community_data)

    geo = json.load(open(os.path.join(HERE, "world.geo.json"), encoding="utf-8"))
    with open(os.path.join(HERE, "worldgeo.js"), "w", encoding="utf-8") as f:
        f.write("window.WORLD_GEO=")
        json.dump(geo, f, ensure_ascii=False)
        f.write(";")

    print(f"users={len(users)} located={located} cities={len(city_agg)} "
          f"schools={len(schools)} companies={len(companies)} countries={len(countries)}")
    print("top cities:", [(c['zh'], c['count']) for c in data['cities'][:12]])
    print("unmatched locations:")
    print(f"  {sum(unmatched_loc.values())} records")

if __name__ == "__main__":
    main()
