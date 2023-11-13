import os
import json
import pprint
import random
import asyncio
import requests

from typing import List

from globals import GlobalConfigs
from helpers import GetResponse, _ResponseCheck

class DescribeConfigs(GlobalConfigs):
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

class ImagineConfigs(GlobalConfigs):
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
        print(self.channel_id)
        self.updated_json = json.loads(requests.request(
            "GET",
            self.imagine_url,
            headers=self.headers,
            data= {},
        ).text)
        pprint.pprint(self.updated_json)
        self.midjourney_id = self.updated_json["application_commands"][0]["application_id"] # application_id that midjourney was given by Discord
        self.imagine_id = self.updated_json["application_commands"][0]["id"]
        self.version = self.updated_json["application_commands"][0]["version"]
        print(self.midjourney_id, self.imagine_id, self.version)
    
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

# midjourney_id = "936929561302675456"

if __name__ == "__main__":
    a = ImagineConfigs()
    imagine_json = a.get_payload(prompt="Will Smith")
    response = GetResponse(url=a.interaction_url, json=imagine_json, headers=a.headers)
    print(response)
