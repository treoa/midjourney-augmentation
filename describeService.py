import os
import re
import time
import json
import uuid
import random
import requests

from typing import List

from globals import GlobalConfigs
from helpers import GetResponse, _ResponseCheck
from imagineService import ImagineService

class DescribeService(GlobalConfigs):
    def __init__(self, 
                 server_id: str = None, 
                 discord_token: str = None, 
                 channel_id: str = None, 
                 cookie: str = None, 
                 storage_url: str = None, 
                 messages_url: str = None,
                 interaction_url: str = None,
                 describe_url: str = None) -> None:
        super().__init__(server_id, discord_token, channel_id, cookie, storage_url, messages_url, interaction_url)
        self.describe_url = describe_url if describe_url else f"https://discord.com/api/v10/channels/{self.channel_id}/application-commands/search?type=1&include_applications=true&query=describe"
        self.updated_json = json.loads(requests.request(
            "GET",
            self.describe_url,
            headers=self.headers,
            data= {},
        ).text)
        self.midjourney_id = self.updated_json["application_commands"][0]["application_id"] # application_id that midjourney was given by Discord
        self.describe_id = self.updated_json["application_commands"][0]["id"]
        self.version = self.updated_json["application_commands"][0]["version"]
        self.describe_json = {
            "session_id": random.randint(0, 8888),
            "version": self.version,
            "id": self.midjourney_id,
        }

    def get_payload(self, attachments: list) -> dict:
        __payload = {
            "type":2,
            "application_id":self.midjourney_id,
            "guild_id": self.server_id,
            "channel_id": self.channel_id,
            "session_id": random.randint(0, 88888),
            "data":{
                "version": self.version,
                "id": self.describe_id,
                "name":"describe","type":1,"options":[{"type":11,"name":"image","value":0}],
                "application_command":{
                    "id": self.describe_id,
                    "application_id": self.midjourney_id,
                    "version": self.version,
                    "default_member_permissions":None,"type":1,"nsfw":False,"name":"describe",
                    "description":"Writes a prompt based on your image.","dm_permission":True,"contexts":None,
                    "options":[{"type":11,"name":"image","description":"The image to describe","required":True}]
                },"attachments":attachments,
            }
        }
        return __payload
    
    def get_last_message(self) -> dict:
        messages = json.loads(
            requests.request(
                "GET",
                url=self.messages_url,
                headers=self.headers,
                data={},
            ).text
        )
        return messages[0]
    
    def JsonRegImg(self, filename : str, filesize : int) -> dict:
        __payload = {"files": [{"filename": filename, "file_size": filesize, "id": 0}]}
        return __payload
    
    def ImageStorage(self, ImageName : str, ImageUrl : str, ImageSize : int) -> tuple:
        try:
            ImageName = ImageName.split(".")
            ImageName = "{}_{}".format(ImageName[0], ImageName[1])

            _response = requests.post(url = self.storage_url, json = self.JsonRegImg(ImageName, ImageSize), headers = self.headers)
            if _ResponseCheck(_response)[0]:
                __Res = _response.json()["attachments"][0]
                upload_url = __Res["upload_url"]
                upload_filename = __Res["upload_filename"]

                __response = requests.get(ImageUrl, headers={"authority":"cdn.discordapp.com"})
                if _ResponseCheck(__response)[0]:
                    if ImageUrl != "https://example.com":
                        my_data = __response.content
                    else:
                        my_data = open(ImageName, "rb")
                    # ___response = requests.put(upload_url,data=__response.content, headers={"authority":"discord-attachments-uploads-prd.storage.googleapis.com"})
                    ___response = requests.put(upload_url, data=my_data, headers={"authority":"discord-attachments-uploads-prd.storage.googleapis.com"})
                    if _ResponseCheck(___response)[0]:
                        return (True, (ImageName, upload_filename))
                    else:
                        return (False, "StorageError in Location:ImageStorage, Msg:Can't Storage!")
                else:
                    return (False, "ReadError in Location:Image, Msg:Image is not exist!")
            else:
                return (False, "ResponseError in Location:GetResponse, Msg:Fail to get Response from Discord!")
        except Exception as e:
            return (False, "RunningError in Location:{}, Msg:{}".format("ImageStorage", e))
    
    def get_descriptions(self, file: str) -> List[str]:
        image_url = file
        if not file.startswith('http'):
            image_url = "https://example.com"
        response = self.ImageStorage(ImageName=file, ImageUrl=image_url, ImageSize = random.randint(4444, 8888))
        if response[0]:
            # print(f"Got the response from ImageStorage")
            __attachments = [{"id":0, "filename":response[1][0],"uploaded_filename":response[1][1]}]
            # print(f"Printing out  the attachments: {__attachments}")
            __payload = self.get_payload(attachments=__attachments)
            response = GetResponse(url=self.interaction_url, json = __payload, headers=self.headers)
            time.sleep(10)
            last_msg = self.get_last_message()
            descs = last_msg["embeds"][0]["description"].split("\n")
            # cleaned_list = [element for element in descs if element]
            cleaned_list = []
            for item in descs:
                if item:  # Check if the string is not empty
                    # Remove URLs using regular expression
                    # item = re.sub(r'\[.*?\]\(https?:\/\/.*?\)', '', item)
                    item = re.sub(r'\(https?:\/\/.*?\)', '', item)
                    item = re.sub(r'\[', '', item)
                    item = re.sub(r'\]', '', item)
                    cleaned_list.append(item.strip()[4::])
        else:
            return []
        # print(cleaned_list)
        return cleaned_list
        


