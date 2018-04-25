# -*- coding: utf-8 -*-
import os
import re
import json
import requests

class SearchNews:
    # end point
    url = "https://api.cognitive.microsoft.com/bing/v7.0/news/search"
    def __init__(self,reply_token):
        self.reply_token=reply_token
    
    def search(self,msg_text):
        # parameters
        query = msg_text
        count = 6       # 1リクエストあたりの最大取得件数 default:30 max:150
        mkt = "ja-JP"   # 取得元の国コード
        params = {'q':query,'count':count,'offset':1,'mkt':mkt,'encodingFormat':'jpeg'}
        # header
        subscriptionKey=os.environ['BING_SEARCH_KEY'] #  Bing Search API Key
        headers = {'Ocp-Apim-Subscription-Key':subscriptionKey}
        
        response = requests.get(self.url,headers=headers,params=params)
        print(response.text)
        output_url=[]
        output_name=[]
        output_imageurl=[]
        news_num=0
        boolean_search_image='F'
        
        for i in range(count-1):
            if 'totalEstimatedMatches' in json.loads(response.text):
                news_url = json.loads(response.text)['value'][i]['url']
                output_url.append(news_url)
                news_name = json.loads(response.text)['value'][i]['name']
                if len(news_name) > 60:
                    news_name = news_name[:60]
                    output_name.append(news_name)
                if 'image' in json.loads(response.text)['value'][i]:
                    image = json.loads(response.text)['value'][i]['image']['thumbnail']['contentUrl']
                    output_imageurl.append(image)
                else:
                    output_imageurl.append('no image')
                boolean_search_image='T'
                news_num+=1
                print(news_url)

            else:
                continue
            if news_num > 5:
                break
        print(len(output_url))
        # 送信準備
        if boolean_search_image == 'T':
            payload = self.create_news_carousel(output_url,output_name,output_imageurl)
        else:
            rep_text = "ニュースが見つかりませんでした"
            payload = {
                "replyToken":self.reply_token,
                "messages":[{
                            "type":"text",
                            "text":rep_text
                            }]
        }
        return payload

def create_news_carousel(self,urls,names,images):
    payload = {
        "replyToken":self.reply_token,
            "messages":[{
                        "type": "template",
                        "altText": "this is a carousel template",
                        "template": {
                        "type": "carousel",
                        "imageAspectRatio": "square",
                        "columns": [
                        ]
                        }
            }]
    }
    print(payload)
    i=0
    for url in urls:
        if images[i] == 'no image':
            images[i] = 'https://upload.wikimedia.org/wikipedia/ja/b/b5/Noimage_image.png'
        print(url)
        payload['messages'][0]['template']['columns'].append({
                                                                 "thumbnailImageUrl" : images[i],
                                                                 "text": names[i],
                                                                 "actions": [{
                                                                             "type": "uri",
                                                                             "label": "リンクへ",
                                                                             "uri": url
                                                                             }]
        })
        i+=1
    print(payload)
    return payload
