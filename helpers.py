import os
import cv2
import time
import requests
import inspect
import warnings

from deepface import DeepFace

warnings.filterwarnings("ignore")

def GetResponse(url: str, json : dict, headers: dict) -> bool:
    """
        Send the post request and get the response, after validating it.
    """
    stack = inspect.stack()


    try:
        class_name = stack[1].frame.f_locals["self"].__class__.__name__ or "Unknown"
        module_name = stack[1].frame.f_globals["__name__"] or "Unknown"
        function_name = stack[1].function or "Unknown"
        response = requests.post(url = url, json = json, headers = headers)
        logme(f"POST request from {module_name} -> {class_name} -> {function_name}")
        # print(f"This function was called from class_name {class_name}. Function name {function_name} in module {module_name}")
        # print(f"Getting the response: {response.text}")
        return _ResponseCheck(response)
    except Exception as e:
        return (False, f"ResponseError in Location: GetResponse, Msg: {e}")

def _ResponseCheck(Response):
    """
        Check whether the response corresponds to the successfull execution.
    """
    if Response.status_code >= 400:
        return (False, f"ResponseError in Location: ResponseCheck, Msg: {Response.text}, Code: {Response.status_code}")
    return (True, Response)

def logme(sometext: str) -> None:
    """
        Log the text with the function name and timestamp.
    """
    stack = inspect.stack()
    function_name = stack[1].function or "Unknown"
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}] - {function_name}: {sometext}\n")

def crop_face(file: str) -> None:
    backends = [
        'opencv', 
        'ssd', 
        'dlib', 
        'mtcnn', 
        'retinaface', 
        'mediapipe',
        'yolov8',
        'yunet',
        'fastmtcnn',
    ]
    # img = cv2.imread(file)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # face_cascade = cv2.CascadeClassifier(f"{cv2.data.haarcascades}haarcascade_frontalface_default.xml")
    # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(64, 64), flags = cv2.CASCADE_SCALE_IMAGE)
    # for (x, y, w, h) in faces:
    #     face_clip = img[y:y+h, x:x+w]
    #     file_name, file_extension = os.path.splitext(file)
    #     file = f"{file_name}_cropped{file_extension}"
    #     cv2.imwrite(file, face_clip)
    #     logme(f"File saved as {file}")
    face_objs = DeepFace.extract_faces(
        img_path = file, 
        target_size = (224, 224), 
        detector_backend = backends[4]
    )
    for face_obj in face_objs:
        print(face_obj)
        face = face_obj["face"]
        
        