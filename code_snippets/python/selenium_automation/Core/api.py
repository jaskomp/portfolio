import base64
import json
import os
import requests

API_MAIN_URL = 'xxx'
API_MAIN_EXTERNAL_URL = 'xxx'
API_JSON_UPLOAD_ENDPOINT = 'xxx'
API_JSON_DOWNLOAD_ENDPOINT = 'xxx'
API_HTML_UPLOAD_ENDPOINT = 'xxx'
API_HTML_DOWNLOAD_ENDPOINT = 'xxx'
API_PREPARE_ENVIRONMENT_ENDPOINT = 'xxx'
API_SUMMARY_ENDPOINT = 'xxx'


class ApiCommunication:

    @staticmethod
    def check_api_is_alive(driver):
        try:
            r = requests.get(API_MAIN_URL, verify=False, timeout=5)
            if r.status_code == 200:
                driver.get_screenshot_as_file('TestResults/ServiceOrders/API_security.png')
                return True
            else:
                driver.get_screenshot_as_file('TestResults/ServiceOrders/API_security.png')
                return False
        except Exception:
            driver.get_screenshot_as_file('TestResults/ServiceOrders/API_security.png')
            return False
    
    @staticmethod
    def prepare_api_environment(driver):
        try:
            r = requests.get(API_MAIN_URL + API_PREPARE_ENVIRONMENT_ENDPOINT, verify=False, timeout=5)
            if r.status_code == 200:
                os.environ['API'] = 'True'
                print('Środowisko API przygotowane.')
                return True
            else:
                return False
        except Exception:
            driver.get_screenshot_as_file('TestResults/ServiceOrders/API_prepare.png')
            return False

    @staticmethod
    def send_stage_json_data(stage):
        with open(f'ValueStorage/{stage}.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            params = {'stageName': f'{stage}'}
            requests.post(API_MAIN_URL + API_JSON_UPLOAD_ENDPOINT, json=data, params=params, verify=False)
            print(f'Wysłano {stage}.json do API')

    @staticmethod
    def get_stage_json_data(stage):
        params = {'stage': stage}
        r = requests.get(API_MAIN_URL + API_JSON_DOWNLOAD_ENDPOINT, params=params, verify=False)
        content = r.json()
        with open(f"ValueStorage/api_{params['stage']}.json", 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)
        print(f'Pobrano z API plik z danymi stage {stage}')
    
    @staticmethod
    def send_html_summary_data():
        with open('ValueStorage/index2.html', 'rb') as f:
            encoded_string = base64.b64encode(f.read())
            data_to_send = {"file": str(encoded_string.decode('utf-8'))}
            params = {'stageName': 'false', 'html_summary': 'true', 'filename': 'index2.html'}
            r = requests.post(API_MAIN_URL + API_HTML_UPLOAD_ENDPOINT, json=data_to_send, params=params, verify=False)
            print('Wysłano do API HTML z podsumowaniem.')
