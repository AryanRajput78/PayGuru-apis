from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser

from .models import userDetails
from .serializers import UserSerializer

from requests.auth import HTTPDigestAuth

import json
import requests
import datetime
import xmltodict
import pandas as pd
import pymysql as mysql

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

# API to create a new User. (Development Done.) (Optimized below.)
# class createUser(generics.ListCreateAPIView):
#     queryset = userDetails.objects.all()
#     serializer_class = UserSerializer
# user_create = createUser.as_view()

# API to check if the device is online or not. (Development Done.)
@api_view(['GET'])
def checkOnline(request):
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
                    # print(f'Fetched System info for {url}.')
                else:
                    print(f'Unable to fetch System info for {url}.')
            else:
                print(f'Authentication for {url} unsuccessful.')
        except Exception as e:
            status = 'Offline'
        deviceSerial.append((firmware, url, status))
        query = f"""UPDATE device_devicedetails SET status = %s WHERE (ip = %s)"""
        val = (status, ip)
        cursor.execute(query, val)
        dbs.commit()
    # print(deviceSerial)
    return Response(deviceSerial)

# API to get count of User, Cards and Face registered. (Development Done.)
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
 
#API to get the registered User Details. (Development Done.)
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
                                        # print(key, uinfo[key])
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
    print(end - start)
    return Response(info)

#API to get the list of cards from the database.
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

class createUser(APIView):
    
    def get(self, request):
        users = userDetails.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        file = request.data['image']
        print(file)
        if serializer.is_valid():
            if file:
                serializer.image = file 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
create_user = createUser.as_view()

class updateUser(APIView):
    
    def get_object(self, pk):
        try:
            print(userDetails.objects.get(pk=pk))
            return userDetails.objects.get(pk=pk)
        except userDetails.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        users = self.get_object(pk)
        serializer = UserSerializer(users)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        parser_classes = (MultiPartParser, FormParser)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
update_user = updateUser.as_view()
# class createUser(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = userDetails.objects.all()
#     serializer_class = UserSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def perform_update(self, request, *args, **kwargs):
#         return self.perform_update(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
