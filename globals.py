import os
import json
import random

from typing import List


class GlobalConfigs:
    def __init__(self, 
                 server_id: str = None, 
                 discord_token: str = None, 
                 channel_id: str = None, 
                 cookie: str = None, 
                 storage_url: str = None,
                 messages_url: str = None,
                 interaction_url: str = None) -> None:
        self.server_id = server_id if server_id else "1071628299194875934"
        self.discord_token = discord_token if discord_token else "OTc5NDAzNTI4NjQ2ODQwMzIw.Gae6pZ.NrwHWCZpheDmg_SkvVOvwiuWw_HB_AyiF8Pkw0"
        self.channel_id = channel_id if channel_id else "1071628299194875937"
        self.cookie = cookie if cookie else '__cfruid=61abc7881b939246d72c5835162f298b0f406bcf-1698719546; __dcfduid=bb24565e779511ee84565ac1e2370008; __sdcfduid=bb24565e779511ee84565ac1e2370008125720b98f31796fc8b347145ddf986a2ca092084b53fe33174ea055f9dfaf82; _cfuvid=saJ3zrWbMHIsx5ISYIGH5Gu4AfWejCk2EkYJRL226Rg-1698719546871-0-604800000'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.discord_token,
            'Cookie': self.cookie,
        }
        self.storage_url = storage_url if storage_url else f"https://discord.com/api/v10/channels/{self.channel_id}/attachments"
        self.messages_url = messages_url if messages_url else f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
        self.interaction_url = interaction_url if interaction_url else f"https://discord.com/api/v10/interactions"


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

    def get_payload(self, prompt: str = "PROMPT PLACEHOLDER") -> dict:
        return {}

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
        self.imagine_url = imagine_url if imagine_url else f"https://discord.com/api/v10/channels/{channel_id}/application-commands/search?type=1&include_applications=true&query=imagine"

    def get_payload(self) -> dict:
        describe_json = {
            "session_id" : "5be666160a2dc210a99c460d38c30a61",
            "version" : "1166847114203123797",
            "id" : "1092492867185950852",
        }

        return describe_json

midjourney_id = "936929561302675456"

if __name__ == "__main__":
    a = DescribeConfigs()
    print(a.storage_url)