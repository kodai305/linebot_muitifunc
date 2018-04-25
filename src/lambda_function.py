# -*- coding: utf-8 -*-
import requests
import json
import re
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

from translate import Translate
from search_image import SearchImage
from search_news import SearchNews
from cognition_image import CognitionImage

LINE_BOT_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
LINE_PUSH_ENDPOINT = 'https://api.line.me/v2/bot/message/push'
LINE_POST_HEADERS = {
        'Content-type': 'application/json; charset=UTF-8',
        'Authorization':'Bearer '+os.environ['ACCESS_TOKEN'],
}
LINE_GET_HEADERS = {
        'Authorization':'Bearer '+os.environ['ACCESS_TOKEN'],
}

def lambda_handler(event, context):
        print (event.keys())
        print (event.values())
        print (event.items())
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('linebot')
        
        to =''
        # user id の抽出
        if 'source' in event['events'][0]:
                user_id = event['events'][0]['source']['userId']
                if 'type' in event['events'][0]['source']:
                        if 'group' in event['events'][0]['source']['type']:
                                to = event['events'][0]['source']['groupId']
                        elif 'user' in event['events'][0]['source']['type']:
                                to = event['events'][0]['source']['userId']
        if 'replyToken' in event['events'][0]:
                reply_token = event['events'][0]['replyToken']
        print("userid:")
        print(user_id)
        
        '''
        payload={
                "to":to,
                "messages":[{
                        "type":"text",
                        "text":"push!!!"
            }]
        }
        try:
                post_response = requests.post(LINE_PUSH_ENDPOINT, headers=LINE_POST_HEADERS, data=json.dumps(payload))
        except ValueError:
                  print ("failed access")
        '''
        # メッセージの抽出
        msg_text="";
        msg_id="";
        if 'postback' in event['events'][0]['type']:
                postback_data = event['events'][0]['postback']['data']
                if postback_data == "action=set&mode=translate":
                        payload = {
                                "replyToken":event['events'][0]['replyToken'],
                                "messages":[{
                                        "type":"text",
                                        "text":"翻訳モードになりました。"
                                }]
                        }
                        # set BOT's mode
                        set_bot_mode(user_id,'Translate')
                        
                elif postback_data == "action=set&mode=searchImage":
                        payload = {
                                "replyToken":event['events'][0]['replyToken'],
                                "messages":[{
                                        "type":"text",
                                        "text":"画像検索モードです。\n \
                                                入力したワードで画像を検索します。\n"
                                }]
                        }
                        set_bot_mode(user_id,'SearchImage')
        
                elif postback_data == "action=set&mode=searchNews":
                        payload = {
                                "replyToken":event['events'][0]['replyToken'],
                                "messages":[{
                                        "type":"text",
                                        "text":"NEWS検索モードです。\n "
                                }]
                        }
                        set_bot_mode(user_id,'SearchNews')
                elif postback_data == "action=set&mode=cognitionImage":
                        payload = {
                                "replyToken":event['events'][0]['replyToken'],
                                "messages":[{
                                            "type":"text",
                                            "text":"画像認識モードです。\n "
                                }]
                        }
                        set_bot_mode(user_id,'CognitionImage')


        elif 'message' in event['events'][0]:
                if 'text' in event['events'][0]['message']:
                        msg_text = event['events'][0]['message']['text']
                elif 'image' in event['events'][0]['message']['type']:
                        msg_text = "image"
                        msg_id = event['events'][0]['message']['id']
                        msg_text = msg_text+msg_id
                else:
                        msg_text = 'the type of message is not text '
                
                print('msg_text:'+msg_text)
        
                # ユーザー名の取得　
                UserName="";
                get_response = requests.get('https://api.line.me/v2/bot/profile/'+user_id,headers=LINE_GET_HEADERS)
                if 'displayName' in json.loads(get_response.text):
                        UserName = json.loads(get_response.text)['displayName']
                else:
                        UserName = "Unknown"
                print('UserName:'+UserName)
        
              
                # get last message from dynamoDB 
                items = table.get_item(
                        Key={
                                 "userId": user_id
                        }
                )
                
                if msg_text == "reset":
                        set_bot_mode(user_id,"reset")

                mode=" "
                if 'Item' in items.keys() and 'mode' in items['Item']:
                        mode = items['Item']['mode']
                        
                # usage(ボタンの練習)
                if msg_text == "help" or mode == " ":
                        payload = get_usage_payload(reply_token)
                elif mode == "Translate":
                        # 翻訳
                        T = Translate(reply_token,UserName)
                        payload = T.translate(msg_text)
                elif mode == "SearchImage":
                        # 画像検索
                        S = SearchImage(reply_token)
                        payload = S.search(msg_text)
                elif mode == "SearchNews":
                        # ニュース検索
                        N = SearchNews(reply_token)
                        payload = N.search(msg_text)
                elif mode == "CognitionImage":
                        # 画像認識
                        C = CognitionImage(reply_token)
                        payload = C.cognition(msg_id)

                '''
                # DBに追加
                table.put_item(
                        Item={
                                'userId': user_id,
                                'text': msg_text,
                                'replyToken': reply_token
                        }
                )
                # mode との兼ね合いに注意
                '''
                
        # 送信
        try:
                post_response = requests.post(LINE_BOT_ENDPOINT, headers=LINE_POST_HEADERS, data=json.dumps(payload))
        except ValueError:
                  print ("failed access")

def set_bot_mode(user_id,mode):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('linebot')
        
        if mode == "reset":
                mode = " "
        table.put_item(
                Item={
                'userId': user_id,
                'mode'  : mode
                }
        )

def get_usage_payload(reply_token):
        payload = {
                "replyToken":reply_token,
                "messages":[{
                        "type": "template",
                        "altText": "This is a buttons template",
                        "template": {
                                "type": "buttons",
        #                                "thumbnailImageUrl": "https://example.com/bot/images/image.jpg",
        #                                "imageAspectRatio": "rectangle",
        #                                "imageSize": "cover",
        #                                "imageBackgroundColor": "#FFFFFF",
        #                                "title": "Menu",
                                                "text": "Please select a mode\n \
                                                         使いたいモードを選択してください。\n",
        #                                "defaultAction": {
        #                                  "type": "uri",
        #                                  "label": "View detail",
        #                                  "uri": "http://example.com/page/123"
        #                                },
                                "actions": [{
                                        "type": "postback",
                                        "label": "Translate/翻訳",
                                        "data": "action=set&mode=translate"
                                },
                                {
                                        "type": "postback",
                                        "label": "SearchImage/画像検索",
                                        "data": "action=set&mode=searchImage"
                                },
                                {
                                        "type": "postback",
                                        "label": "SearchNews/NEWS検索",
                                        "data": "action=set&mode=searchNews"
                                },
                                {
                                        "type": "postback",
                                        "label": "SearchNews/画像認識",
                                        "data": "action=set&mode=cognitionImage"
                                },
                                ]
                        }
                                
                }]
        }
        return payload

'''
    # 場所
    "type": "location",
    "title": "my location",
    "address": "〒150-0002 東京都渋谷区渋谷２丁目２１−１",
    "latitude": 35.65910807942215,
    "longitude": 139.70372892916203
'''

'''
# カルーセルの練習
payload = {
        "replyToken":reply_token,
        "messages":[{
                        "type": "template",
                        "altText": "this is a carousel template",
                        "template": {
                                "type": "carousel",
                                "columns": [{
                                        "title": "this is menu",
                                        "text": "description",
                                        "actions": [{
                                                "type": "message",
                                                "label": "English",
                                                "text": "I speek English"
                                        }]
                                },
                                {
                                        "title": "this is menu",
                                        "text": "description",
                                        "actions": [{
                                                "type": "message",
                                                "label": "English",
                                                "text": "I speek English"
                                        }]
                                },
                                {
                                        "title": "this is menu",
                                        "text": "description",
                                        "actions": [{
                                                "type": "message",
                                                "label": "English",
                                                "text": "I speek English"
                                        }]
                                }
                                ],
                        }
                }]
}
'''

'''
# 使い方 (確認テンプレートの練習)
match = re.search('help|ヘルプ|使い方|usage',msg_text)
if(match):
        payload = {
                "replyToken":reply_token,
                        "messages":[{
                        "type": "template",
                        "altText": "this is a confirm template",
                        "template": {
                                "type": "confirm",
                                "text": "発言を翻訳します.\n"+
                                "何の言語を使いますか?\n\n"+
                                "I translate your statement.\n"+
                                "What's your first language?",
                                "actions": [
                                        {
                                        "type": "message",
                                        "label": "日本語",
                                        "text": "日本語を使います"
                                        },
                                        {
                                        "type": "message",
                                        "label": "English",
                                        "text": "I speek English"
                                       }
                                ]
                        }
                        }]
                }
        '''
