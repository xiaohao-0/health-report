import sys, getopt, itchat, getpass, pickle, os
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
    # 不能通过status_code判断是否登录成功
    # if login_res.status_code == 200:
    #     print("登录成功！")
    #     return session
    # else:
    #     return None

    res_html = login_res.text
    content = etree.HTML(res_html)
    try:
        login_fail = content.xpath("//input[@name='lt']/@value")[0]
    except:
        print("登录成功！")
        return session
    else:
        print('登录失败。')
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
        flag = False
        if report_res.status_code == 200:
            print("今天的健康信息已经上传！")
            flag  = True
        else:
            print("健康信上传失败！")

        return flag
    

def send_wechat_msg(target_name,msg):
    itchat.auto_login(True)
    groups = itchat.get_chatrooms(update=True)

    target = None
    for group in groups:
        if group['NickName'] == target_name:
            target = group['UserName']

    if target != None:
        res_info = itchat.send(msg,target)
    else:
        print('微信群不存在！')

    res_flag = res_info['BaseResponse']['Ret'] == 0
    
    
    if res_flag:
        print('成功，发送消息\'{}\'到群组\'{}\''.format(msg,target_name))
    else:
        print('成功微信消息失败')
    
    return res_flag


# def get_basic_info_cmd(argv):

    # def usage():
    #     print("usage: python auto_health_report.py -u <username> -m <wechat message> -t <target group name> --healthy\n \
    #     or using cache: python auto_health_report.py  -c ")
    #     print("  username: 校园网帐号 \n  --healthy: 确保你是健康的")
    
    # try:
    #     opts, args = getopt.getopt(argv,"hu:m:t:",["healthy"])
    # except getopt.GetoptError:
    #     print('命令行参数不正确')
    #     usage()
    #     sys.exit(2)
    
    # info = {
    #     "username" : "",
    #     "is_healthy": False,
    #     "msg": "",
    #     "target_name": ""
    # }
   
    # for opt, val in opts:
    #     if opt == "-h":
    #         usage()
    #         sys.exit()
    #     elif opt == "-u":
    #         info["username"] = val
    #     elif opt == '-m':
    #         info["msg"] = val
    #     elif opt == '-t':
    #         info["target_name"] = val
    #     elif opt == "--healthy":
    #         info["is_healthy"] = True
    
    # return info


def get_basic_info():

    info = {
        "username" : "",
        "is_healthy": False,
        "msg": "",
        "target_name": ""
    }

    cache_file = 'info.pkl'

    if os.path.isfile(cache_file):
        pkl_file = open(cache_file, 'rb')
        info = pickle.load(pkl_file)
    else:
        info["username"] = input("用户名：\n")
        info["is_healthy"] = input("是否健康：(Y|其它)\n")
        info["target_name"] = input("微信群名：\n")
        info["msg"] = input("要发送的消息：\n")


        if info["is_healthy"] == "Y" or info["is_healthy"] == "y":
            info["is_healthy"] = True

        with open(cache_file,'wb') as f:
            pickle.dump(info,f)

    return info


def main(argv):
    
    info = get_basic_info()

    # info = get_basic_info_cmd(argv)

    if info["is_healthy"]:
        if info["username"] != "" and info["msg"] != "" and info["target_name"] != "":
            # print('用户：',info["username"])

            passwd = getpass.getpass('密码：')

            if report(info["username"],passwd):
                send_wechat_msg(msg=info["msg"],target_name=info["target_name"])
    
    else:
        print("请确保你是健康的。")



if __name__ == "__main__":
    main(sys.argv[1:])
