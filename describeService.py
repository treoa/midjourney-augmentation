import os
import re
import time
import json
import uuid
import random
import requests

from typing import List

from globals import GlobalConfigs
from helpers import GetResponse, _ResponseCheck, logme, crop_face

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
        self.describe_url = describe_url or f"https://discord.com/api/v10/channels/{self.channel_id}/application-commands/search?type=1&include_applications=true&query=describe"
        try:
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
            # for attr in dir(self):
            #     if not attr.startswith("__"):
            #         print(f"{attr} : {getattr(self, attr)}\n")
        except Exception as e:
            logme(f"Error occurred. \n{e}")

    def get_payload(self, attachments: list) -> dict:
        return {
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
        return {"files": [{"filename": filename, "file_size": filesize, "id": 0}]}
    
    def ImageStorage(self, ImageName : str, ImageUrl : str, ImageSize : int) -> tuple:
        try:
            ImageName = ImageName.split(".")
            ImageName = f"{ImageName[0]}.{ImageName[1]}"
            _response = GetResponse(url=self.storage_url, json=self.JsonRegImg(ImageName, ImageSize), headers=self.headers)
            if not _response[0]:
                return (False, "ResponseError in Location:GetResponse, Msg:Fail to get Response from Discord!")
            __Res = _response[1].json()["attachments"][0]
            upload_url = __Res["upload_url"]
            upload_filename = __Res["upload_filename"]

            __response = requests.get(ImageUrl, headers={"authority":"cdn.discordapp.com"})
            if not _ResponseCheck(__response)[0]:
                return (False, "ReadError in Location:Image, Msg:Image is not exist!")
            my_data = __response.content if ImageUrl != "https://example.com" else open(ImageName, "rb")

            ___response = requests.put(upload_url, data=my_data, headers={"authority":"discord-attachments-uploads-prd.storage.googleapis.com"})
            if not _ResponseCheck(___response)[0]:
                return (False, "StorageError in Location:ImageStorage, Msg:Can't Storage!")
            return (True, (ImageName, upload_filename))
        except Exception as e:
            return (False, f"RunningError in Location:ImageStorage, Msg:{e}")
    
    def get_descriptions(self, file: str) -> List[str]:
        image_url = file
        if not file.startswith('http'):
            image_url = "https://example.com"
            crop_face(file)
            file_name, file_extension = os.path.splitext(file)
            file = f"{file_name}_cropped{file_extension}"
        response = self.ImageStorage(ImageName=file, ImageUrl=image_url, ImageSize = random.randint(4444, 8888))
        if response[0]:
            __attachments = [{"id":0, "filename":response[1][0],"uploaded_filename":response[1][1]}]
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
            logme(f"Something went wrong at getting descriptions with response: {response[1]}")
            return []
        return cleaned_list
        


