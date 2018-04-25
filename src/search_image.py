# -*- coding: utf-8 -*-
import os
import re
import json
import requests

class SearchImage:
    # end point
    url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    def __init__(self,reply_token):
        self.reply_token=reply_token
    
    def search(self,msg_text):
        # parameters
        query = msg_text
        count = 5       # 1リクエストあたりの最大取得件数 default:30 max:150
        mkt = "ja-JP"   # 取得元の国コード
        params = {'q':query,'count':count,'offset':1,'mkt':mkt}
        # header
        subscriptionKey=os.environ['BING_SEARCH_KEY'] #  Bing Search API Key
        headers = {'Ocp-Apim-Subscription-Key':subscriptionKey}
        # request
        response = requests.get(self.url,headers=headers,params=params)
        print(response.text)
        image_url=''
        output_url=[]
        image_num=0
        boolean_search_image='F'
        for i in range(count-1):
            if 'webSearchUrl' in json.loads(response.text):
                image_url = json.loads(response.text)['value'][i]['thumbnailUrl']
            else:
                continue
            print(image_url)
            match = re.search('https',image_url)
            if json.loads(response.text)['value'][i]['encodingFormat'] == "jpeg" and match:
                image_url = json.loads(response.text)['value'][i]['thumbnailUrl']
                output_url.append(image_url)
                boolean_search_image='T'
                image_num+=1
            if image_num > 4:
                break
        print(len(output_url))
        # 送信準備
        if boolean_search_image == 'T':
            payload = self.create_image_carousel(output_url)
        else:
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
