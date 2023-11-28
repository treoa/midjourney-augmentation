import os
import re
import time
import json
import random
import requests

from globals import GlobalConfigs
from helpers import GetResponse, logme, crop_face

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
        self.midjourney_id = self.updated_json["application_commands"][0]["application_id"] # application_id that midjourney was given by Discord
        self.imagine_id = self.updated_json["application_commands"][0]["id"]
        self.version = self.updated_json["application_commands"][0]["version"]
    
    def generate_payload(self, prompt: str, realism: bool = True, close_up: bool = True) -> None:
        if realism:
            aspect_ratio_pattern = r"--ar \d+:\d+"
            aspect_ratio_match = re.search(aspect_ratio_pattern, prompt)

            additional_text = "perceptive Fashion Photography, cinematic shots, cinematic color grading, ultra realistic, Phantom High-Speed Camera, 35mm, f1/8, global illumination, film, RAW,"

            if close_up:
                additional_text = f"close up shot, looking directly at the camera, {additional_text}"

            # Extract and remove the aspect ratio substring
            if aspect_ratio_match:
                aspect_ratio = aspect_ratio_match.group(0)
                text_without_ar = re.sub(aspect_ratio_pattern, '', prompt).strip()
            else:
                aspect_ratio = ""  # Default aspect ratio if none found
                text_without_ar = prompt

            # Append the additional descriptive text and the aspect ratio
            prompt = f"{text_without_ar}, {additional_text} {aspect_ratio}"

        self.imagine_json = {
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
    
    def imagine(self, prompt:str, realism: bool = True, close_up: bool = True) -> bool:
        try:
            self.generate_payload(prompt=prompt, realism=realism, close_up=close_up)
            self.imagine_response = GetResponse(url=self.interaction_url, json=self.imagine_json, headers=self.headers)
            if self.imagine_response[0]:
                return True
            else:
                logme("Something went wrong in imagine function")
        except Exception as e:
            logme(e)
            
    def get_highest_index(self) -> int:
        files = os.listdir('.')
        return max((int(match.group(1)) for file in files if (match := re.match(r'image_(\d+)\.jpg', file))), default=0)
    
    def get_option_from_generated(self, idx: int, crop: bool=True) -> bool:
        """
        Send an option for upscale from the generated image.

        Args:
            idx (int): The index of the image option.
            crop (bool): Whether to crop the face or not

        Returns:
            bool: True if the option was successfully retrieved and saved as an image file, False otherwise.
        """
        # last_msg = self.get_last_message()
        time.sleep(10)
        try:
            while True:
                last_msg = self.get_last_message()
                if str(last_msg["content"]).endswith('%) (fast)') or str(last_msg["content"]).endswith('(Waiting to start)'):
                    time.sleep(8)
                else:
                    # logme(f"The last message got is: {last_msg['content']}")
                    break;
        except Exception as e:
            logme(f"Failed to check for messages. Error message: {e}")
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
        logme(f"Sending the upscaling of {idx} image")
        response = GetResponse(url=self.interaction_url,
                               json=generated_msg_payload,
                               headers=self.headers,)
        time.sleep(10)
        if response[0]:
            try:
                while True:
                    last_msg = self.get_last_message()
                    if str(last_msg["content"]).endswith('%) (fast)') or str(last_msg["content"]).endswith('(Waiting to start)'):
                        time.sleep(10)
                    else:
                        break;
            except Exception as e:
                logme(f"Failed to check for messages. Error message: {e}")
                return False
            try:
                attachment_url = last_msg["attachments"][0]["url"]
                image_response = requests.get(attachment_url)
            except Exception as e:
                logme(f"Failed to acquire the image url. {e}")
                return False
            try:
                highest_idx = self.get_highest_index()

                # Increment the index for the new image
                new_idx = highest_idx + 1
                filename = f'image_{new_idx}.jpg'
                if not image_response.status_code == 200:
                    raise Exception("Error occurred")
                with open(filename, 'wb') as file:
                    file.write(image_response.content)
                logme(f"File saved as {filename}")
                if crop:
                    crop_face(filename)
            except Exception as e:
                logme(f"Something went wrong during file saving. The error is {e}")
                return False
            return True
        else:
            logme("Something went wrong. See the error above.")
            return False