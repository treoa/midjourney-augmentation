import os
import json

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
        self.config = self.load_config()
        self.server_id = server_id if server_id else self.server_id
        self.discord_token = discord_token if discord_token else self.discord_token
        self.channel_id = channel_id if channel_id else self.channel_id
        self.cookie = cookie if cookie else self.cookie
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.discord_token,
            'Cookie': self.cookie,
        }
        self.storage_url = storage_url if storage_url else f"{self.base_url}channels/{self.channel_id}/attachments"
        self.messages_url = messages_url if messages_url else f"{self.base_url}channels/{self.channel_id}/messages"
        self.interaction_url = interaction_url if interaction_url else f"{self.base_url}interactions"

    @staticmethod
    def load_config(file_path='config.json'):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError("Configuration file not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding the configuration file.")

    def __getattr__(self, name):
        return self.config.get(name, None)
