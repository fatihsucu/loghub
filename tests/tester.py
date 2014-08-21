import os
import unittest
import pymongo
from werkzeug.test import Headers
import sys
sys.path.append('../')
import run


class LoghubTestCase(unittest.TestCase):

    """docstring for LoghubTestCase"""
    
    def setUp(self):
        self.db = pymongo.MongoClient()['loghub_dev']
        run.app.config['TESTING'] = True
        self.app = run.app.test_client()

    
    def tearDown(self):
        db = pymongo.MongoClient()
        db.drop_database('loghub_test')


    def test_01_create_user(self):        
        rv  = self.app.post("/API/v1/users",data=dict(email="mysexyemail@mail.com",
                                                password="mysexypassword"
                                                ))        
        assert "Success" in rv.data
        rv  = self.app.post("/API/v1/users",data=dict(email="mysexyemailmail.com",
                                                    password="mysexypassword"
                                                    ))
        assert "Email is invalid" in rv.data
        rv  = self.app.post("/API/v1/users",data=dict(email="mysexyemail@mail.com",
                                                    password="my"
                                                    ))
        assert "Password is invalid" in rv.data


    def test_02_get_user(self):        
        rv = self.app.get("/API/v1/user/email=mysexyemail@mail.com&password=mysexypassword")        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/user/email=mysexyemailmail.com&password=mysexypassword")
        assert "Email is invalid" in rv.data
        rv = self.app.get("/API/v1/user/email=mysexyemail@mail.com&password=mord")
        assert "Incorrect email or password." in rv.data

    def test_03_reset_credential(self):        
        rv = self.app.post("/API/v1/user/credential", data=dict(
                                                    email="mysexyemail@mail.com",
                                                    password="mysexypassword"
                                                    ))        
        assert "Success" in rv.data
        rv = self.app.post("/API/v1/user/credential", data=dict(
                                                    email="mysexyemailmail.com",
                                                    password="mysexypassword"
                                                    ))
        assert "Email is invalid" in rv.data
        rv = self.app.post("/API/v1/user/credential", data=dict(
                                                    email="mysexyemail@mail.com",
                                                    password="myse"
                                                    ))
        assert "Password is invalid" in rv.data

    def test_04_change_user_mail(self):        
        h = Headers()        
        credential = self.db.users.find_one({"email":"mysexyemail@mail.com"})["credential_id"]  
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.put('/API/v1/user/email',data=dict(new_email="mynewemail@mail.com",
                                                        password="mysexypassword"),
                                                    headers=h
                                                    )        
        assert "Success" in rv.data
        rv = self.app.put('/API/v1/user/email',data=dict(new_email="mynewemail@mail.com",
                                                        password="myseassword"),
                                                    headers=h
                                                    )
        assert "Incorrect email or password." in rv.data
        rv = self.app.put('/API/v1/user/email',data=dict(new_email="mynewemailmail.com",
                                                        password="myseassword"),
                                                    headers=h
                                                    )
        assert "Email is invalid." in rv.data


    def test_05_remember_account(self):        
        rv = self.app.post("/API/v1/auth/remember", data=dict(
                                                    email="mynewemail@mail.com"                                                    
                                                    ))        
        assert "Success" in rv.data
        rv = self.app.post("/API/v1/auth/remember", data=dict(
                                                    email="mynewemail.com"                                                    
                                                    ))
        assert "Email is invalid." in rv.data

    def test_06_reset_user_password(self):     
        code = self.db.codes.find_one({"email":"mynewemail@mail.com"})["code"]
        rv = self.app.post("/API/v1/auth/reset_password", data=dict(
                                                    email="mynewemail@mail.com",
                                                    new_password="123456",
                                                    code="{}".format(code)                                                 
                                                    ))        
        assert "Success" in rv.data
        rv = self.app.post("/API/v1/auth/reset_password", data=dict(
                                                    email="mynewemail@mail.com",
                                                    new_password="123456",
                                                    code="sssss"                                                 
                                                    ))
        assert "Verification code is invalid." in rv.data
        rv = self.app.post("/API/v1/auth/reset_password", data=dict(
                                                    email="mysexyemailmail.com",
                                                    new_password="123456",
                                                    code="{}".format(code)                                                 
                                                    ))
        assert "Email is invalid." in rv.data


    def test_07_register_app(self):        
        h = Headers()
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.post("/API/v1/applications", data=dict(
                                                    name="mysexyapp",
                                                    ),
                                                    headers=h)        
        assert "Success" in rv.data        
        rv = self.app.post("/API/v1/applications", data=dict(
                                                    name="mysexyapp",
                                                    ))
        assert "Credential id required" in rv.data
        

    def test_08_get_apps(self):        
        h = Headers()
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.get("/API/v1/applications", headers=h)        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/applications")
        assert "Credential id required" in rv.data

    def test_09_get_app(self):        
        h = Headers()
        APP_TOKEN = self.db.apps.find_one({"name":"mysexyapp"})["APP_TOKEN"]        
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.get("/API/v1/applications/{}/".format(APP_TOKEN), headers=h)        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/applications/{}/".format(APP_TOKEN))
        assert "Credential id required" in rv.data
        rv = self.app.get("/API/v1/applications/{}1/".format(APP_TOKEN), headers=h)
        assert "Invalid APP_TOKEN" in rv.data

    def test_16_reset_app_token(self):        
        h = Headers()
        APP_TOKEN = self.db.apps.find_one({"name":"mysexyapp"})["APP_TOKEN"]
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.put("/API/v1/applications/{}/token".format(APP_TOKEN), headers=h)        
        assert "Success" in rv.data
        rv = self.app.put("/API/v1/applications/{}/token".format(APP_TOKEN), headers=h)
        assert "Couldn't find any registered apps" in rv.data

    def test_17_delete_apps(self):        
        h = Headers()
        APP_TOKEN = self.db.apps.find_one({"name":"mysexyapp"})["APP_TOKEN"]
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.delete("/API/v1/applications/{}/".format(APP_TOKEN), headers=h)        
        assert "Success" in rv.data
        rv = self.app.delete("/API/v1/applications/{}/".format(APP_TOKEN))
        assert "Credential id required" in rv.data

    def test_10_logging(self):        
        h = Headers()
        APP_TOKEN = self.db.apps.find_one({"name":"mysexyapp"})["APP_TOKEN"]
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.post("/API/v1/applications/{}/".format(APP_TOKEN),data=dict(
                                                                            message="something bad happened"                                                                              
                                                                              ),
                                                                            headers=h
                                                                            )        
        assert "Success" in rv.data
        rv = self.app.post("/API/v1/applications/{}/".format(APP_TOKEN),data=dict(
                                                                            message="something bad happened"                                                                              
                                                                              )                                                                            
                                                                            )
        assert "Credential id required" in rv.data


    def test_11_query_log(self):        
        h = Headers()
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.get("/API/v1/logs",headers=h)        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/logs")
        assert "Credential id required" in rv.data

    def test_12_register_alarm(self):        
        h = Headers()
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.post("/API/v1/alarms", data=dict(alarm="some_alarm"))
        assert "CREDENTIAL_ID required." in rv.data
        rv = self.app.post("/API/v1/alarms", data=dict(alarm="some_alarm",receivers="asdad@gmail.com",name="myAlarm"),headers=h)        
        assert "Success" in rv.data
        rv = self.app.post("/API/v1/alarms", data=dict(alarm="some_alarm",receivers="asdad@gmail.com"),headers=h)
        assert "Name and Receivers must be specified." in rv.data
        rv = self.app.post("/API/v1/alarms", data=dict(alarm="some_alarm",name="asdad"),headers=h)
        assert "Name and Receivers must be specified." in rv.data

    def test_13_get_alarms(self):        
        h = Headers()
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.get("/API/v1/alarms", headers=h)        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/alarms")
        assert "CREDENTIAL_ID required." in rv.data

    def test_14_get_alarm_by_id(self):        
        h = Headers()
        alarm_id = str(self.db.alarms.find_one({"name":"myAlarm"})["_id"])
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.get("/API/v1/alarms/{}".format(alarm_id), headers=h)        
        assert "Success" in rv.data
        rv = self.app.get("/API/v1/alarms/{}".format(alarm_id))
        assert "CREDENTIAL_ID required." in rv.data
        rv = self.app.get("/API/v1/alarms/{}b".format(alarm_id[:-1]), headers=h)
        assert "You do not have an alarm with that ID." in rv.data

    def test_15_delete_alarm(self):        
        h = Headers()
        alarm_id = str(self.db.alarms.find_one({"name":"myAlarm"})["_id"])
        credential = self.db.users.find_one({"email":"mynewemail@mail.com"})["credential_id"]        
        h.add("X-Authorization","credential_id {}".format(credential))
        rv = self.app.delete("/API/v1/alarms/{}".format(alarm_id), headers=h)        
        assert "Success" in rv.data
        rv = self.app.delete("/API/v1/alarms/{}".format(alarm_id))
        assert "CREDENTIAL_ID required." in rv.data
        rv = self.app.delete("/API/v1/alarms/{}".format(alarm_id), headers=h)        
        assert "You do not have an alarm with that ID." in rv.data


if __name__ == '__main__':
    unittest.main()
    