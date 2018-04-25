# -*- coding: utf-8 -*-
import os
import re
import requests
HEADERS = {
    'Content-type': 'application/json'
}

ENDPOINT = "https://gateway.watsonplatform.net/language-translator/api/v2/translate"

class Translate:
    def __init__(self,reply_token,UserName):
        self.reply_token=reply_token
        self.UserName=UserName
    def translate(self,msg_text):
        # 翻訳
        #        ACCESS_KEY = os.environ['AZURE_KEY']
        #   translator = Translator(ACCESS_KEY)
        match = re.search(r'^[a-zA-Z]',msg_text)        
        if match:
            params = {
                'model_id':'en-ja',
                'text':msg_text
            }
            post_response = requests.post(ENDPOINT,headers=HEADERS,params=params,auth=(os.environ['watson_username'],os.environ['watson_pass']))

            rep_text = "\""+self.UserName+"\""+"は\n"+post_response.text+"\n"+"と言っています"
        else:
            params = {
                'model_id':'ja-en',
                'text':msg_text
            }
            post_response = requests.post(ENDPOINT,headers=HEADERS,params=params,auth=(os.environ['watson_username'],os.environ['watson_pass']))


            rep_text = "\""+self.UserName+"\""+" said as follows:\n\n"+post_response.text
    
        # 送信準備
        payload = {
            "replyToken":self.reply_token,
            "messages":[{
                        "type":"text",
                        "text":rep_text
                        }]
        }
        
        return payload
