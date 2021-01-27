import time,json,requests,random,datetime
import campus

def main():
    #定义变量
    success,failure=[],[]
    #sectets字段录入
    phone, password, deviceId, sckey = [], [], [], []
    #多人循环录入
    while True:  
        try:
            users = input()
            info = users.split(',')
            phone.append(info[0])
            password.append(info[1])
            deviceId.append(info[2])
            sckey.append(info[3])
        except:
            break

    #提交打卡
    for index,value in enumerate(phone):
        print("开始尝试为用户%s打卡"%(value[-4:]))
        count = 0
        while (count <= 3):
            try:
                token = campus.campus_start(phone[index],password[index],deviceId[index])
                userInfo=getUserInfo(token)
                if mark == 0:
                    response = checkIn(userInfo,token)
                if mark == 1:
                    ownphone=phone[index]
                    response = check(ownphone,userInfo,token)
                strTime = getNowTime()
                if response.json()["msg"] == '成功':
                    success.append(value[-4:])
                    print(response.text)
                    msg = strTime + value[-4:]+"打卡成功"
                    if index == 0:
                        result=response
                    break
                else:
                    failure.append(value[-4:])
                    print(response.text)
                    msg =  strTime + value[-4:] + "打卡异常"
                    count = count + 1
                    if index == 0:
                        result=response
                    if count<=3:
                        print('%s打卡失败，开始第%d次重试...'%(value[-4:],count))
                    time.sleep(5)
            except Exception as e:
                print(e.__class__)
                failure.append(value[-4:])
                strTime = getNowTime()
                msg = strTime + value[-4:] +"出现错误"
                count = count + 1
                result = "出现错误" 
                if count<=3:
                    print('%s打卡出错，开始第%d次重试...'%(value[-4:],count))
                time.sleep(3)
        print(msg)
        print("-----------------------")
    fail = sorted(set(failure),key=failure.index)
    title = "成功: %s 人,失败: %s 人"%(len(success),len(fail))
    try:
        print('主用户开始微信推送...')
        wechatPush(title,sckey[0],success,fail,result)
    except:
        print("微信推送出错！")

#时间函数
def getNowTime():
    cstTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8))
    strTime = cstTime.strftime("%H:%M:%S ")
    return strTime

#信息获取函数
def getUserInfo(token):
    for _ in range(3):
        try:
            data = {"appClassify": "DK", "token": token}
            sign_url = "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo"
            response = requests.post(sign_url, data=data)
            return response.json()['userInfo']
        except:
            print('getUserInfo ERR，Retry......')
            time.sleep(3)

#校内打卡提交函数
def checkIn(userInfo,token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
     #随机温度(36.2~36.8)
    a=random.uniform(36.2,36.8)
    temperature = round(a, 1)
    jsons={
  "businessType": "epmpics",
  "method": "submitUpInfo",
  "jsonData": {
    "deptStr": {
      "deptid": 46394,
      "text": "学生-航海学院-航海171D"
    },
    "areaStr": "{\"streetNumber\":\"\",\"street\":\"护驾山路\",\"district\":\"邹城市\",\"city\":\"济宁市\",\"province\":\"山东省\",\"town\":\"\",\"pois\":\"邹城市第一中学(北校区)\",\"lng\":117.0043030000003,\"lat\":35.41580091076081,\"address\":\"邹城市护驾山路邹城市第一中学(北校区)\",\"text\":\"山东省-济宁市\",\"code\":\"\"}",
    "reportdate": 1611740388473,
    "customerid": "790",
    "deptid": 46394,
    "source": "app",
    "templateid": "pneumonia",
    "stuNo": "201721011408",
    "username": "朱培宁",
    "phonenum": "18253738399",
    "userid": "13422677",
    "updatainfo": [
      {
        "propertyname": "temperature",
        "value": "36.5"
      },
      {
        "propertyname": "symptom",
        "value": "无症状"
      },
      {
        "propertyname": "SFJCQZHYS",
        "value": "否，从未隔离观察"
      },
      {
        "propertyname": "jjxhuodong",
        "value": "没有"
      },
      {
        "propertyname": "jtcy",
        "value": "没有"
      },
      {
        "propertyname": "isAlreadyInSchool",
        "value": "没有"
      },
      {
        "propertyname": "isTouch",
        "value": "否"
      },
      {
        "propertyname": "outdoor",
        "value": "否"
      },
      {
        "propertyname": "xinqing",
        "value": "健康"
      },
      {
        "propertyname": "ownbodyzk",
        "value": "否"
      },
      {
        "propertyname": "yiqu",
        "value": "无症状"
      },
      {
        "propertyname": "dormitory",
        "value": "技校家属院"
      },
      {
        "propertyname": "ownPhone",
        "value": "18253738399"
      },
      {
        "propertyname": "emergencyContact",
        "value": "朱本湖"
      },
      {
        "propertyname": "mergencyPeoplePhone",
        "value": "13465476420"
      },
      {
        "propertyname": "assistRemark",
        "value": ""
      },
      {
        "propertyname": "symptoms",
        "value": "本人承诺以上信息均经本人审核确认，准确无误，如有瞒报、漏报和弄虚作假行为，自愿接受国家疫情防控相关管理规定处理。"
      }
    ],
    "gpsType": 0,
    "token": "1a55cef9-b6db-4971-aa1d-d3457e0ed237"
  }
}
    res = requests.post(sign_url, json=check_json) 
    return res

#微信通知
def wechatPush(title,sckey,success,fail,result):    
    strTime = getNowTime()
    page = json.dumps(result.json(), sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False)
    content = f"""
`{strTime}` 
#### 打卡成功用户：
`{success}` 
#### 打卡失败用户:
`{fail}`
#### 主用户打卡信息:
```
{page}
```
### 😀[收藏此项目](https://github.com/YooKing/HAUT_autoCheck)

        """
    data = {
            "text":title,
            "desp":content
    }
    scurl='https://sc.ftqq.com/'+sckey+'.send'
    for _ in range(3):
        try:
            req = requests.post(scurl,data = data)
            if req.json()["errmsg"] == 'success':
                print("Server酱推送服务成功")
                break
            else:
                print("Server酱推送服务失败")
                time.sleep(3)
        except:
            print("微信推送参数错误")

if __name__ == '__main__':
    mark = 1
    main()
