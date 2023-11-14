import os
import json
import pprint
import random
import asyncio
import requests

from typing import List

from globals import GlobalConfigs
from helpers import GetResponse, _ResponseCheck

class DescribeService(GlobalConfigs):
    """
        TODO:
        - Initiate the describe url method to get the values 
        - Update configs from the got values
        - Generate the json payload for the describe config
        - Init function that returns the json payload for that
    """
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
        pprint.pprint(self.updated_json)
        self.midjourney_id = self.updated_json["application_commands"][0]["application_id"] # application_id that midjourney was given by Discord
        self.describe_id = self.updated_json["application_commands"][0]["id"]
        self.version = self.updated_json["application_commands"][0]["version"]
        print(self.midjourney_id, self.describe_id, self.version)
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

class ImagineService(GlobalConfigs):
    def __init__(self, 
                 server_id: str = None, 
                 discord_token: str = None, 
                 channel_id: str = None, 
                 cookie: str = None, 
                 storage_url: str = None, 
                 messages_url: str = None,
                 interaction_url: str = None,
                 imagine_url: str = None) -> None:
        super().__init__(server_id, discord_token, channel_id, cookie, storage_url, messages_url, interaction_url)
        self.imagine_url = imagine_url if imagine_url else f"https://discord.com/api/v10/channels/{self.channel_id}/application-commands/search?type=1&include_applications=true&query=imagine"
        self.updated_json = json.loads(requests.request(
            "GET",
            self.imagine_url,
            headers=self.headers,
            data= {},
        ).text)
        # pprint.pprint(self.updated_json)s
        self.midjourney_id = self.updated_json["application_commands"][0]["application_id"] # application_id that midjourney was given by Discord
        self.imagine_id = self.updated_json["application_commands"][0]["id"]
        self.version = self.updated_json["application_commands"][0]["version"]
    
    def get_payload(self, prompt: str) -> dict:
        imagine_json = {
            "type": 2,
            "application_id": self.midjourney_id,
            "guild_id": self.server_id,
            "channel_id": self.channel_id,
            "session_id": random.randint(0, 8888),
            "data": {
                "version": self.version,
                "id": self.imagine_id, 
                "name": "imagine",
                "type": 1,
                "options": [
                {
                    "type": 3,
                    "name": "prompt",
                    "value": prompt,
                }
                ],
                "application_command": {
                "id": self.imagine_id,
                "application_id": self.midjourney_id,
                "version": self.version,
                "default_member_permissions": None,
                "type": 1,
                "nsfw": False,
                "name": "imagine",
                "description": "Create images with Midjourney",
                "dm_permission": True,
                "contexts": [
                    0,
                    1,
                    2
                ],
                "integration_types": [
                    0
                ],
                "options": [
                    {
                    "type": 3,
                    "name": "prompt",
                    "description": "The prompt to imagine",
                    "required": True
                    }
                ]
                },
                "attachments": [],
            }
        }

        return imagine_json
    
    def get_last_message(self) -> dict:
        messages = json.loads(
            requests.request(
                "GET",
                url=self.messages_url,
                headers=self.headers,
                data={},
            ).text
        )
        pprint.pprint(messages[0]["id"])
        return messages[0]
    
    def get_option_from_generated(self, idx: int) -> bool:
        last_msg = self.get_last_message()
        generated_msg_payload = {
            "type": 3,
            "guild_id": self.server_id,
            "application_id": self.midjourney_id,
            "session_id": random.randint(0, 8888),
            "channel_id": self.channel_id,
            "message_id": last_msg["id"],
            "data": {
                "component_type": 2,
                "custom_id": last_msg["components"][0]["components"][idx]["custom_id"]
            },}
        

# midjourney_id = "936929561302675456"

if __name__ == "__main__":
    a = ImagineService()
    imagine_json = a.get_payload(prompt="Will Smith")
    # response = GetResponse(url=a.interaction_url, json=imagine_json, headers=a.headers)
    last_msg = a.get_last_message()
    # pprint.pprint(last_msg)
    
    # response = requests.request(
    #     "POST",
    #     url=a.interaction_url,
    #     json=msg_payload,
    #     headers=a.headers,
    # )
    
    # pprint.pprint(last_msg)
    # url = 'https://cdn.discordapp.com/attachments/1071628299194875937/1173850757976559697/toneest_Will_Smith_eb690c40-6c4c-4058-9394-bc9ad720554d.png?ex=656574b5&is=6552ffb5&hm=16b9a6c31edb049a27cf455655d6a83c28f25a652118b21580073671aa22ff19&'
    # filename = 'image11.jpg'

    # response = requests.get(url)
    # if response.status_code == 200:
    #     with open(filename, 'wb') as file:
    #         file.write(response.content)

    # print(f'Image saved as {filename}')

