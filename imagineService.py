import os
import re
import time
import json
import pprint
import random
import requests

from globals import GlobalConfigs
from helpers import GetResponse

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
        # pprint.pprint(messages[0]["id"])
        return messages[0]
    
    def get_option_from_generated(self, idx: int) -> bool:
        # last_msg = self.get_last_message()
        time.sleep(1)
        try:
            while True:
                last_msg = self.get_last_message()
                if str(last_msg["content"]).endswith('%) (fast)') or str(last_msg["content"]).endswith('(Waiting to start)'):
                    time.sleep(5)
                else:
                    break;
        except Exception as e:
            print(f"Failed to check for messages. Error message: {e}")
            return False
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
        response = GetResponse(url=self.interaction_url,
                               json=generated_msg_payload,
                               headers=self.headers,)
        time.sleep(10)
        if response[0]:
            try:
                while True:
                    last_msg = self.get_last_message()
                    if str(last_msg["content"]).endswith('%) (fast)') or str(last_msg["content"]).endswith('(Waiting to start)'):
                        time.sleep(5)
                    else:
                        break;
            except Exception as e:
                print(f"Failed to check for messages. Error message: {e}")
                return False
            attachment_url = last_msg["attachments"][0]["url"]
            try:
                image_response = requests.get(attachment_url)
                # List all files in the current directory
                files = os.listdir('.')

                # Find the highest index used so far in image_{number}.jpg
                highest_idx = 0
                for file in files:
                    match = re.match(r'image_(\d+)\.jpg', file)
                    if match:
                        idx = int(match.group(1))
                        highest_idx = max(highest_idx, idx)

                # Increment the index for the new image
                new_idx = highest_idx + 1
                filename = f'image_{new_idx}.jpg'
                if image_response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(image_response.content)
                    print(f"File saved as {filename}")
                else:
                    raise Exception
            except Exception as e:
                print("Something went wrong. The erorr is {e}")
                return False
            return True
        else:
            print("Something went wrong. See the error above.")
            return False