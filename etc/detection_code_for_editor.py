import json
import requests
import urllib.parse


def on_check_generation_score_button_click(path: List[Union[str, int]]):
    # Set loading while calling the API
    setLoading(True)

    # Get completion value and call service
    completion_text = getValue(textarea_completion) # TODO Add here your textarea of block that you would like to check for generation
    detection_report = call_detection_service(completion_text)

    # Turn off the loading
    setLoading(False)

    # Set generated score and author
    setValue(slider_generated_score, round(detection_report["generated_score"] * 100, 2))
    setValue(paragraph_author, detection_report["author"])

    return


def call_detection_service(text: str) -> dict:
    resp = requests.post(
        url=urllib.parse.urljoin(URL, "detect"),
        json={"text": text}
    )
    if resp.status_code != 200:
        raise Exception(f"The service returned an unknown error\nStatus code: {resp.status_code}\nContent: {resp.content}")
        
    res = json.loads(resp.content.decode('utf-8'))

    return res
