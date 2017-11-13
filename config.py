# -*- coding:utf-8 -*- 
# author: szy
# time: 2017/11/8 14:37
# email: shizhenyu96@gmail.com

SETTINGS = {
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': 'password',
    'MYSQL_DBNAME': 'rawler',
    'MYSQL_SERVER': 'localhost'
}

TIME_OUT = 10
SLEEP_TIME = 10
TABLE_NAME = "ALL_URL"
DB_PARAM = {
    'url': None,
    'html': None,
    'language': 'Unknown',
    'encode': None,
    'http_code': None,
    'useful': 0,
    'wrong_reason': '',
    'AddTime': None,
    'UpdateTime': None,
}

VALID_SUFFIX = ["aspx", "php", "htm", "html", "asp", "ashx", "mooc", "cgi", "action", "jsp", "do", "psp", "jspy"]
COMMON_FILE_SUFFIX = ["jpg", "png", "css", "pdf", "doc", "docx", "ico", "mp4", "avi",
                      "rar", "xlsx", "xls", "gif", "xml", "portal", "thmx", "flv",
                      "mp3", "zip", "ppt", "pptx", "mso", "gz", "txt", "owl", "exe"]
OUTER_DOMAIN = ["com", "net", "in", "org", "fr", "de", "cn"]

INVALID_HREF_PATTERN = ["javascript:", "mailto:", "@nju.edu.cn"]

url1 = 'https://www.nju.edu.cn'
url2 = 'https://grawww.nju.edu.cn'
url3 = 'http://jw.nju.edu.cn'
url4 = 'https://nubs.nju.edu.cn'
url5 = 'http://lib.nju.edu.cn/html/index.html'
url6 = 'http://ces.nju.edu.cn'
url7 = 'http://news.nju.edu.cn'
url8 = 'http://cssrac.nju.edu.cn/index.html'
url9 = 'http://public.nju.edu.cn'
url10 = 'http://acoustics.nju.edu.cn'
url11 = 'https://physics.nju.edu.cn'
url12 = 'http://pyb.nju.edu.cn'
url13 = 'http://fcc.nju.edu.cn'
url14 = 'https://cs.nju.edu.cn'
url15 = 'https://es.nju.edu.cn'
url16 = 'https://bkzs.nju.edu.cn'
url17 = 'https://xiaoban.nju.edu.cn'
url18 = 'https://xgc.nju.edu.cn'
url19 = 'http://hjxy.nju.edu.cn'
url20 = 'http://med.nju.edu.cn'
url21 = 'https://sgos.nju.edu.cn'
url22 = 'http://job.nju.edu.cn:9081'
url23 = 'http://chin.nju.edu.cn'
url24 = 'http://chem.nju.edu.cn'
url25 = 'http://admission.nju.edu.cn'
url26 = 'http://lamda.nju.edu.cn/CH.MainPage.ashx'
url27 = 'https://arch.nju.edu.cn/1108/list.htm'
url28 = 'http://essi.nju.edu.cn'
url29 = 'http://nlp.nju.edu.cn/homepage'
url30 = 'https://eng.nju.edu.cn'
url31 = 'http://software.nju.edu.cn'
url32 = 'http://astronomy.nju.edu.cn'
url33 = 'http://as.nju.edu.cn'
url34 = 'http://ese.nju.edu.cn'
url35 = 'http://rdc.nju.edu.cn'
url36 = 'https://malab.nju.edu.cn'
url37 = 'https://philo.nju.edu.cn'
url38 = 'http://history.nju.edu.cn'
url39 = 'https://www.sfs.nju.edu.cn'
url40 = 'http://math.nju.edu.cn'
url41 = 'http://life.nju.edu.cn'
url42 = 'https://hr.nju.edu.cn'
url43 = 'http://stuex.nju.edu.cn'
url44 = 'http://njubs.nju.edu.cn'
url45 = 'http://sdibc.nju.edu.cn'
url46 = 'https://ocer.nju.edu.cn'
url47 = 'https://nic.nju.edu.cn'
url48 = 'http://sklac.nju.edu.cn'
url49 = 'http://law.nju.edu.cn'
url50 = 'http://marxism.nju.edu.cn'
url51 = 'https://scit.nju.edu.cn'
url52 = 'http://biophy.nju.edu.cn'
url53 = 'https://jc.nju.edu.cn'
url54 = 'http://hospital.nju.edu.cn'
url55 = 'http://ltx.nju.edu.cn'
url56 = 'https://mpacc.nju.edu.cn'
url57 = 'http://study.nju.edu.cn/home/index.mooc'
url58 = 'http://edu.nju.edu.cn'
url59 = 'http://pld.nju.edu.cn/cgi-bin/mydate.cgi'
url61 = 'http://im.nju.edu.cn'
url62 = 'http://qinggongxiao.nju.edu.cn/cys/index.html#/home'
url63 = 'https://zzb.nju.edu.cn'
url64 = 'https://grayx.nju.edu.cn'
url65 = 'https://hwxy.nju.edu.cn'
url67 = 'https://nanhai.nju.edu.cn'
url68 = 'http://emba.nju.edu.cn'
url69 = 'https://sme.nju.edu.cn'
url70 = 'https://zhwh.nju.edu.cn'
url71 = 'https://bwc.nju.edu.cn'
url72 = 'http://chemlabs.nju.edu.cn'
url73 = 'https://confucius.nju.edu.cn'
url74 = 'https://keysoftlab.nju.edu.cn'
url75 = 'http://pasa-bigdata.nju.edu.cn'
url76 = 'https://rwb.nju.edu.cn'
url77 = 'http://skch.nju.edu.cn'
url78 = 'http://aerc.nju.edu.cn'
url79 = 'http://sociology.nju.edu.cn/index.html'
url80 = 'https://dii.nju.edu.cn'
url81 = 'http://rczp.nju.edu.cn'
url82 = 'http://jianglab.nju.edu.cn'
url83 = 'https://bwc.nju.edu.cn'
url84 = 'https://zzb.nju.edu.cn'
url85 = 'http://xlzx.nju.edu.cn'
url86 = 'http://biophy.nju.edu.cn'
url87 = 'https://charity.nju.edu.cn'
url88 = 'http://jshr.nju.edu.cn'
url89 = 'https://rwb.nju.edu.cn'
url90 = 'https://physics.nju.edu.cn'
url91 = 'https://edp.nju.edu.cn'
#hint url45 ,url59  url91 have some problem, so crawler it first
SEED_URL_SET = {url45, url59, url91, url1, url2, url3, url4, url5, url6, url7, url8, url9, url10, url11, url12, url13, url14, url15,
                url16, url17, url18, url19, url20, url21, url22, url23, url24, url25, url26, url27, url28, url29,
                url30, url31, url32, url33, url34, url35, url36, url37, url38, url39, url40, url41, url42, url43,
                url44, url46, url47, url48, url49, url50, url51, url52, url53, url54, url55, url56, url57,
                url58, url59, url61, url62, url63, url64, url65, url67, url68, url69, url70, url71, url72, url73,
                url74, url75, url76, url77, url78, url79, url80, url81, url82, url83, url84, url85, url86, url87,
                url88, url89, url90}

ALLOWED_DOMAIN = {"nju.edu.cn"}
