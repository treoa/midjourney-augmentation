import os 
import time
import requests

def GetResponse(url: str, json : dict, headers: dict) -> bool:
    """
        Send the post request and get the response, after validating it.
    """
    try:
        response = requests.post(url = url, json = json, headers = headers)
        print(f"Getting the response: {response.content}")
        return _ResponseCheck(response)
    except Exception as e:
        return (False, "ResponseError in Location:{}, Msg:{}".format("GetResponse", e))

def _ResponseCheck(Response):
    """
        Check whether the response corresponds to the successfull execution.
    """
    if Response.status_code >= 400:
        return (False, "ResponseError in Location:{}, Msg:{}, Code:{}".format("ResponseCheck" ,Response.text, Response.status_code))
    return (True, Response)