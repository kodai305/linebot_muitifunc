# -*- coding: utf-8 -*-
import os
import re
import json
import requests

class CognitionImage:
    # end point
    url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0"
    def __init__(self,reply_token):
        self.reply_token=reply_token
    
    def cognition(self,msg_text):
        # parameters
        params   = {'visualFeatures': 'Categories,Description,Color'}
        # header
        subscriptionKey=os.environ['ComputerVisionKey'] #  Bing Search API Key
        headers = {'Ocp-Apim-Subscription-Key':subscriptionKey}
        # image_url that you want to recognize 
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
        data = {'url' : image_url}
        # request
        response = requests.get(self.url+'analyze',headers=headers,params=params,json=data)
        print(response.json())

        
        # 送信準備
        rep_text = "画像が見つかりませんでした"
        payload = {
            "replyToken":self.reply_token,
                "messages":[{
                            "type":"text",
                            "text":rep_text
                            }]
        }
        return payload
    
    def create_image_carousel(self,urls):
        payload = {
            "replyToken":self.reply_token,
            "messages":[{
                        "type": "template",
                        "altText": "this is a carousel template",
                        "template": {
                        "type": "image_carousel",
                        "columns": [
                        ]
                        }
                        }]
        }
        for url in urls:
            payload['messages'][0]['template']['columns'].append(
                                                                 {
                                                                 "imageUrl": url,
                                                                 "action": {
                                                                 "type": "postback",
                                                                 "data":"storeId=12345"
                                                                 }
                                                                 })
        return payload
