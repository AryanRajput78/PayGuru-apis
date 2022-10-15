from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .forms import image
from .models import userDetails
from .serializers import UserSerializer

from requests.auth import HTTPDigestAuth

import json
import logging
import requests
import datetime
import xmltodict
import pandas as pd
import pymysql as mysql

# Log file initialization for keeping track of the files.
logging.basicConfig(
    filename="./logs.log", format="%(asctime)s %(message)s", filemode="w"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Login credentials for the devices. Hide this after development. (Development Done.)
cred = {
    "user": "admin",
    "password": "a1234@4321",
}

# Login credentials for the database. Hide this after development. (Development Done.)
dbconfig = {
    "host": 'localhost',
    "port": 3306,
    "user": "root",
    "password": "Aryan123",
    "database": "hikvision"
}

# To initialize the database using credentials and returning a database instance. (Development Done.)
def database():
    try:
        mydb = mysql.connect(
            **dbconfig,
        )
    except mysql.connect.Error as e:
        print(e)
    return mydb

# API to check if the device is online or not. (Development Done.)
@api_view(['GET'])
def checkOnline(request):
    # df = pd.read_excel('./constant/devices.xls')
    dbs = database()
    cursor = dbs.cursor()
    cursor.execute("""select * from device_devicedetails""")
    data = pd.DataFrame([dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()])
    deviceSerial = []
    for ip in data['ip']:
        url = "http://" + ip
        firmware = ""
        try:
            response = ""
            response = requests.get(f"{url}/ISAPI/Security/userCheck", auth=HTTPDigestAuth(
                cred['user'], cred["password"]), headers={}, data={}, timeout=0.1)
            response.raise_for_status()
            if response.status_code == 200:
                # print(f'Authentication for {url} successful.')
                status = 'Online'
                resp = requests.get(f"{url}/ISAPI/System/deviceinfo",
                                    auth=HTTPDigestAuth(cred['user'], cred["password"]))
                if resp.status_code == 200:
                    data = xmltodict.parse(resp.text)
                    data = data['DeviceInfo']
                    model = data['model']
                    serialNo = data['serialNumber']
                    firmware = model.replace(
                        " ", "") + serialNo.replace(" ", "")
                    resp.close()
                    logging.info(f"Device {ip} - Online.")
                    # print(f'Fetched System info for {url}.')
                else:
                    logging.info(f"Device {ip} - Unable to fetch information.")
            else:
                logging.info(f"Device {ip} - Authentication failed.")    
        except Exception as e:
            status = 'Offline'
            logging.info(f"Device - {ip} - Offline.")
        deviceSerial.append((firmware, url, status))
        query = f"""UPDATE device_devicedetails SET status = %s WHERE (ip = %s)"""
        val = (status, ip)
        cursor.execute(query, val)
        dbs.commit()
    # print(deviceSerial)
    return Response(deviceSerial)

# API to get count of User, Cards and Face registered on the device. (Development Done.)
@api_view(['GET'])
def getCount(request):
    dbs = database()
    cursor = dbs.cursor()
    cursor.execute("""select * from device_devicedetails""")
    data = pd.DataFrame([dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()])
    headers = {}
    payload = {}
    info = []
    response =""
    url_col_name = {
        ("/ISAPI/AccessControl/UserInfo/Count?format=json", "User", "userNumber"),
        ("/ISAPI/AccessControl/CardInfo/Count?format=json", "Card", "cardNumber"),
        ("/ISAPI/Intelligent/FDLib/Count?format=json&FDID=1&faceLibType=blackFD",
         "Face", "recordDataNumber")
    }
    for ip, stat in zip(data['ip'], data['status']):
        count = {}
        count['IP'] = ip
        count['Status'] = stat
        if stat != "Offline":
            for i in url_col_name:
                url = "http://"+ ip + i[0]
                count[f"{i[1]}Count"] = ""
                # To obtain the Number of Users, Face, Cards registered on the device.
                try:
                    response = requests.get(url, auth=HTTPDigestAuth(
                        cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if (i[1] != 'Face'):
                            data = data[f"{i[1]}InfoCount"]
                            count[f"{i[1]}Count"] = data[f"{i[2]}"]
                        else:
                            count["FaceCount"] = data['recordDataNumber']
                        response.close()
                except Exception as e:
                    if response != "":
                        response.close()
                finally:
                    if response != "":
                        response.close()
        info.append(count)
    return Response(info)
 
# API to get the registered User Details on the device. (Development Done.)
@api_view(['GET'])
def getUsers(request):
    dbs = database()
    cursor = dbs.cursor()
    cursor.execute("""select * from device_devicedetails""")
    data = pd.DataFrame([dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()])
    info = []
    
    for ip, stat in zip(data['ip'], data['status']):
        start = datetime.datetime.now()
        searchPosition = 0
        users ={}
        users['IP'] = ip
        users['status'] = stat
        if (stat != "Offline"):
            url = "http://" + ip + "/ISAPI/AccessControl/UserInfo/Search?format=json"
            headers = {
                'Content-Type': 'application/json'
            }
            while True:
                payload = json.dumps({
                            "UserInfoSearchCond": {
                                "searchID": "1",
                                "maxResults": 30,
                                "searchResultPosition": searchPosition
                            }
                        })
                response = requests.post(url, auth=HTTPDigestAuth(
                            cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()['UserInfoSearch']
                    if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":
                        for uinfo in data['UserInfo']:
                            if uinfo['employeeNo']:
                                userTemplate = json.loads("""{
                                                    "UserInfo": {
                                                        "employeeNo": "",
                                                        "name": "",
                                                        "userType": "",
                                                        "gender": "",
                                                        "localUIRight": "",
                                                        "maxOpenDoorTime": 0,
                                                        "Valid": "",
                                                        "doorRight": "",
                                                        "RightPlan": "",
                                                        "userVerifyMode": "",
                                                        "CardInfo": "",
                                                        "Photo": ""
                                                    }
                                                }""")
                                for key in userTemplate["UserInfo"].keys():
                                    if key in uinfo.keys():
                                        userTemplate["UserInfo"][key] = uinfo[key]
                                    users[uinfo['employeeNo']] = userTemplate
                        if data['responseStatusStrg'] == "OK":
                            break
                        searchPosition += int(data['numOfMatches'])
                    if data['responseStatusStrg'] == "NO MATCH" or searchPosition > int(data['totalMatches']):
                        break
                    response.close()
                else:
                    if response != "":
                        response.close()
        info.append(users)
    end = datetime.datetime.now()
    logging.info(f"Time taken to fetch users - {end - start}")
    return Response(info)

# API to get the list of cards from the database.
@api_view(['GET'])
def getCardList(self):
    punchcard_l = pd.read_excel('')
    url = "http://192.168.0.79/ISAPI/AccessControl/CardInfo/Search?format=json"
    headers = {
        'Content-Type': 'application/json'
    }
    response = ""
    searchPosition = 0
    empList = []
    punch = list(punchcard_l.keys())
    start = 0
    end = 30 if len(punchcard_l) > 30 else len(punch)
    i = 0
    while True:
        empList.clear()
        for key in punch[start: end]:
            empList.append({"employeeNo": key})
        while True:
            try:
                payload = json.dumps({
                    "CardInfoSearchCond": {
                        "searchID": "1",
                        "maxResults": 30,
                        "searchResultPosition": searchPosition,
                        "EmployeeNoList": empList
                    }
                })
                response = requests.post(url, auth=HTTPDigestAuth(
                    cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()['CardInfoSearch']
                    print(data)
                    # if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":

                    #     # print(data['UserInfo'])
                    #     for cinfo in data['CardInfo']:

                    #         # print(uinfo['employeeNo'])
                    #         if(cinfo['employeeNo'] != ''):
                    #             punchcards[cinfo['employeeNo']
                    #                         ]['UserInfo']['CardInfo'] = cinfo
                    #     # i += data['numOfMatches']

                    #     # print(punchcards)
                    #     if data['responseStatusStrg'] == "OK":
                    #         break
                    #     searchPosition += data['numOfMatches']
                    # if data['responseStatusStrg'] == "NO MATCH" or searchPosition > data['totalMatches']:
                    #     break
                    # response.close()
                else:
                    print(response.json())
                    break
            except Exception as e:
                # print(str(e))
                if response != "":
                    response.close()
                break
            finally:
                if response != "":
                    response.close()
    return Response(data)

# API to create a user and store it in the database. (Development Done.) (Checked using localhost/admin)
class createUser(APIView):
    
    def get(self, request):
        users = userDetails.objects.all()
        serializer = UserSerializer(users, many=True)
        logging.info(f'(createUser) Response - {serializer}')
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        form = image(request.POST, request.FILES)
        if serializer.is_valid():
            if form.is_valid():
                form.save()
                img_object = form.instance
            serializer.save()
            print(request.data)
            logging.info(f'(createUser) Data posted successfully! Data = {request.data}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logging.error(f'(createUser) Some error occurred while posting data. Error = {serializer.error}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
create_user = createUser.as_view()

# API to update user details stored in the database. (Development Done.)
class updateUser(APIView):
    
    def get_object(self, pk):
        try:
            print(userDetails.objects.get(pk=pk))
            return userDetails.objects.get(pk=pk)
        except userDetails.DoesNotExist:
            logging.error(f'(updateUser) userDetails Does not exist.')
            raise Http404

    def get(self, request, pk):
        users = self.get_object(pk)
        serializer = UserSerializer(users)
        logging.error(f'(updateUser) Response - {serializer.error}')
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logging.info(f'(updateUser) User details modified.')
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        logging.error(f'(updateUser) User details not modified.') 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        logging.info(f'(updateUser) User deleted.')
        return Response(status=status.HTTP_204_NO_CONTENT)
update_user = updateUser.as_view()

# Function to check if the user exists or not.
def checkUser(ip, id):
    url = "http://" + ip + "/ISAPI/AccessControl/UserInfo/Search?format=json"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "UserInfoSearchCond": {
            "searchID": "1",
            "maxResults": 1,
            "searchResultPosition": 0,
            "fuzzySearch": str(id)
        }
    })
    response = ""
    try:
        response = requests.post(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=payload, timeout=1)
        if response.status_code == 200:
            data = response.json()['UserInfoSearch']
            if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":
                response.close()
                return 'Exists'
            if data['responseStatusStrg'] == "NO MATCH":
                response.close()
                return "Doesnt Exist"
    except Exception as e:
        if response != "":
            response.close()
        return 'Error'
    finally:
        if response != "":
            response.close()

# API to add user template to the devices. (Partial Development Done. create, modify, delete) (Work on Image uploads.)
@api_view(['GET', 'DELETE'])
def addUserTemplate(request):
    data = request.data
    headers = {
        'Content-Type': 'application/json'
    }
    if request.method == "GET":
        for d in data:
            keys = d.keys() 
            for key in keys:
                response = ""
                if key.isdigit():
                    ip = d['IP']
                    temp = d[key].get('UserInfo')
                    enable = temp['Valid']['enable']
                    emp = temp['employeeNo']
                    found = checkUser(ip, emp)
                    types = 'Modify' if found == 'Exists' else 'Record'
                    print(f"Get method - {request.method}")
                    template = json.dumps({
                        "UserInfo": {
                            "employeeNo": str(temp['employeeNo']),
                            "name": str(temp['name']),
                            "userType": str(temp['userType']).lower(),
                            "gender": str(temp['gender']).lower(),
                            "localUIRight": False,
                            "maxOpenDoorTime": 0,
                            "Valid": {
                                "enable": enable,
                                "beginTime": "2022-10-10T00:00:00",
                                "endTime": "2037-12-31T23:59:59",
                                "timeType": "local"
                            },
                            "doorRight": "1",
                            "RightPlan": [
                                {
                                    "doorNo": 1,
                                    "planTemplateNo": "1"
                                }
                            ],
                            "userVerifyMode": "",
                            "CardInfo": "",
                            "Photo": ""
                        }
                    })
                    if types == "Record":
                        url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{types}?format=json"
                        response = requests.post(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
                    else:
                        url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{types}?format=json"
                        response = requests.put(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
    if request.method == "DELETE":
        for d in data:
            keys = d.keys() 
            for key in keys:
                response = ""
                ip = d['IP']
                emp = d['UserInfoDelCond'].get('EmployeeNoList')[0]['employeeNo']
                found = checkUser(ip, emp)
                if found == "Exists":
                    template = json.dumps({
                        "UserInfoDelCond": {
                            "EmployeeNoList": [{
                                "employeeNo":  str(emp)
                            }]
                        }
                    }) 
                    url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/Delete?format=json"
                    response = requests.put(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
                    print(response.text)
                else:
                    print('Employee Does not exist.')
                break
        logging.info(f"(addCardInfo) Response -> {response}")
    return Response("Success")

# def getUserList(ip):
#     info = []
#     searchPosition = 0
#     users ={}
#     url = "http://" + ip + "/ISAPI/AccessControl/UserInfo/Search?format=json"
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     while True:
#         payload = json.dumps({
#                     "UserInfoSearchCond": {
#                         "searchID": "1",
#                         "maxResults": 30,
#                         "searchResultPosition": searchPosition
#                     }
#                 })
#         response = requests.post(url, auth=HTTPDigestAuth(
#                     cred["user"], cred["password"]), headers=headers, data=payload, timeout=5)
#         if response.status_code == 200:
#             data = response.json()['UserInfoSearch']
#             if data['responseStatusStrg'] == "OK" or data['responseStatusStrg'] == "MORE":
#                 for uinfo in data['UserInfo']:
#                     if uinfo['employeeNo']:
#                         userTemplate = json.loads("""{
#                                             "UserInfo": {
#                                                 "employeeNo": "",
#                                                 "name": "",
#                                                 "userType": "",
#                                                 "gender": "",
#                                                 "localUIRight": "",
#                                                 "maxOpenDoorTime": 0,
#                                                 "Valid": "",
#                                                 "doorRight": "",
#                                                 "RightPlan": "",
#                                                 "userVerifyMode": "",
#                                                 "CardInfo": "",
#                                                 "Photo": ""
#                                             }
#                                         }""")
#                         for key in userTemplate["UserInfo"].keys():
#                             if key in uinfo.keys():
#                                 userTemplate["UserInfo"][key] = uinfo[key]
#                             users[uinfo['employeeNo']] = userTemplate
#                 if data['responseStatusStrg'] == "OK":
#                     break
#                 searchPosition += int(data['numOfMatches'])
#             if data['responseStatusStrg'] == "NO MATCH" or searchPosition > int(data['totalMatches']):
#                 break
#             response.close()
#         else:
#             if response != "":
#                 response.close()
#     info.append(users)
#     return info

# def addUserToDevice(user_list, slave_ips):
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     for ip in slave_ips:
#         for d in user_list:
#             keys = d.keys() 
#             for key in keys:
#                 response = ""
#                 if key.isdigit():
#                     temp = d[key].get('UserInfo')
#                     enable = temp['Valid']['enable']
#                     emp = temp['employeeNo']
#                     template = json.dumps({
#                         "UserInfo": {
#                             "employeeNo": f"{str(temp['employeeNo'])}",
#                             "name": f"{str(temp['name'])}",
#                             "userType": str(temp['userType']).lower(),
#                             "gender": f"{str(temp['gender']).lower()}",
#                             "localUIRight": False,
#                             "maxOpenDoorTime": 0,
#                             "Valid": {
#                                 "enable": enable,
#                                 "beginTime": "2022-10-10T00:00:00",
#                                 "endTime": "2037-12-31T23:59:59",
#                                 "timeType": "local"
#                             },
#                             "doorRight": "1",
#                             "RightPlan": [
#                                 {
#                                     "doorNo": 1,
#                                     "planTemplateNo": "1"
#                                 }
#                             ],
#                             "userVerifyMode": "",
#                             "CardInfo": "",
#                             "Photo": ""
#                         }
#                     })
#                     print(ip, emp)
#                     found = checkUser(ip, emp)
#                     type = 'Record' if found == True else 'Modify'
#                     print(type)
#                     if type == "Record":
#                         url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{type}?format=json"
#                         response = requests.post(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
#                     else:
#                         url = "http://" + str(ip) + f"/ISAPI/AccessControl/UserInfo/{type}?format=json"
#                         response = requests.put(url, auth=HTTPDigestAuth(cred["user"], cred["password"]), headers=headers, data=template, timeout=1)
#                     print(response.text)

# API to sync data to the devices.
@api_view(['GET'])
def deviceSync(request):
    slave = []
    dbs = database()
    cursor = dbs.cursor()
    cursor.execute("""select * from device_devicedetails""")
    device_details = pd.DataFrame([dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()])
    for i in device_details.index:
        if device_details['status'][i] == "Online":
            if device_details['master_status'][i] == 'YES':
                master = str(device_details['ip'][i])
            else:
                slave.append(device_details['ip'][i])
        
    # master_data = getUserList(master)
    # addUserToDevice(master_data, slave)
    return Response(device_details)              