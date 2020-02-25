import sys, getopt
import requests as req
from lxml import etree


def prepare_login():
    url_login_get = "https://sso.stu.edu.cn/login?service=https%3A%2F%2Fmy.stu.edu.cn%2Fhealth-report%2Finit-stu-user"
    session = req.Session()
    res = session.get(url_login_get)
    jsessionid = session.cookies.get_dict()["JSESSIONID"]

    res_html = res.text
    content = etree.HTML(res_html)
    token = content.xpath("//input[@name='lt']/@value")[0]

    # print(token)
    # print(jsessionid)
    return session,token,jsessionid
    


def login(username,passwd):
    session,token,jsessionid = prepare_login()

    url_login_post = "https://sso.stu.edu.cn/login;jsessionid="
    url_login_post += jsessionid
    url_login_post += "?service=https%3A%2F%2Fmy.stu.edu.cn%2Fhealth-report%2Finit-stu-user"

    headers_login_post = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "115",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "JSESSIONID="+jsessionid,
        "Origin": "https://sso.stu.edu.cn",
        "Pragma": "no-cache",
        "Referer": "https://sso.stu.edu.cn/login?service=https%3A%2F%2Fmy.stu.edu.cn%2Fhealth-report%2Finit-stu-user",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    }
    form_data = {
        "username" : username,
        "password" : passwd,
        "lt": token,
        "execution": "e1s1", #不知道这是什么
        "_eventId": "submit",
    }
  
    login_res = session.post(url_login_post,data=form_data,headers=headers_login_post)

    # login_res = req.post(url_login_post,data=form_data,headers=headers_login_post)

    # print(login_res.status_code) #在浏览器看到的是302,这里却是200,奇怪
    if login_res.status_code == 200:
        print("登录成功！")
        return session
    else:
        return None
 


def report(username,passwd):
    session = login(username,passwd)
    if session!=None:
        url_report = "https://my.stu.edu.cn/health-report/report/saveReport.do"

        form_data = {
            "health": "良好",
            "familyHealth": "良好",
            "importantPersonType": 4,
            "dailyReport.afternoorBodyHeat": 37.0,
            "dailyReport.forenoonBodyHeat": 37.0,
            "dailyReport.hasCough": False,
            "dailyReport.hasShortBreath": False,
            "dailyReport.hasWeak": False,
            "dailyReport.hasFever": False,
            "dailyReport.exception": None,
            "dailyReport.treatment":  None,
            "dailyReport.conclusion":  None,
            "watchingInfoOutofStu.address":  None,
            "watchingInfoOutofStu.startDate":  None,
            "watchingInfoOutofStu.comment":  None,
        }
        report_res = session.post(url_report,form_data)
        # print(report_res.status_code)
        if report_res.status_code == 200:
            print("今天的健康信息已经上传！")
    


def usage():
    print("usage: python auto_health_report.py -u <username> -p <password> --healthy")
    print("  username: 校园网帐号 \n  password：密码 \n  --healthy: 确保你是健康的")


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hu:p:",["healthy"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    

    username = ""
    passwd = ""
    is_healthy = False
    for opt, val in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt == "-u":
            username = val
        elif opt == "-p":
            passwd = val
        elif opt == "--healthy":
            is_healthy = True
    
    if is_healthy and username != "" and passwd != "" :
        report(username,passwd)
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])