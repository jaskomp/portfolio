import json
import os
from time import sleep
from time import localtime
from time import strftime
import unittest
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from Core.api import ApiCommunication
from Core.common_locators import CommonLocators
from Core.common_methods import CommonMethods, setup_driver
from Core.dictionary import Dictionary
from Core.settings_locators import SettingsLocators

use_api = os.getenv('API', 'False')
if use_api:
    print('Używam API przy dictionaries_crud.')
else:
    print('API dla dictionaries_crud nie jest dostępne.')


class DictionariesCrud(unittest.TestCase, CommonMethods):

    @classmethod
    def setUpClass(self):
        self.driver = setup_driver(webdriver)
        self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        self.errors = []
        with open('ValueStorage/słowniki - tworzenie.json', 'r', encoding='utf-8') as f:
            self.stageStatusDictionaryCreate = json.loads(f.read())
        with open('ValueStorage/słowniki - edycja.json', 'r', encoding='utf-8') as f:
            self.stageStatusDictionaryUpdate = json.loads(f.read())
        with open('ValueStorage/słowniki - usuwanie.json', 'r', encoding='utf-8') as f:
            self.stageStatusDictionaryDelete = json.loads(f.read())

    def setUp(self):
        self.t = localtime()

    dict_urls = SettingsLocators.DICT_URLS

    def create_dictionary_element(self, dict_url):
        self.test_successful = True
        self.driver.get(Dictionary.baseURL + dict_url)
        try:
            error_message = CommonMethods.get_500_error_message(self, self.driver)
            print(f'po wejsciu w słownik pod adresem {self.driver.current_url} jest 500 o tresci: {error_message}')
            self.stageStatusDictionaryCreate["słowniki - tworzenie"][dict_url] = str(0) + f'|{error_message}'
            self.test_successful = False
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, '//*[text()[contains(.,"Tworzenie")]]').click()
            sleep(1)
            elements = CommonMethods.get_required_form_elements(self)
            for elem in elements:
                element = self.driver.execute_script("""return arguments[0].previousElementSibling""", elem)
                if element.get_attribute('type') == 'text' and 'colorPicker' not in element.get_attribute('class') \
                        and element.get_attribute('id') != 'make_order_position_element_surfaceAreaFactor'\
                        and element.get_attribute('id') != 'make_supplier_part_email'\
                        and element.get_attribute('id') != 'make_user_defined_mail_content_content'\
                        and element.get_attribute('id') != 'make_defined_contact_phoneNumber':
                    element.send_keys(CommonMethods.generate_random_lowercase_string(self, 6))
                if element.get_attribute('type') == 'text' and 'colorPicker' in element.get_attribute('class'):
                    element.send_keys('#000000')
                if element.get_attribute('type') == 'select-one':
                    mySelect = Select(element)
                    mySelect.select_by_index(1)
                if element.get_attribute('class') == 'input-group-btn':
                    element = self.driver.execute_script("""return arguments[0].firstChild""", element)
                    element.click()
                if element.get_attribute('id') == 'make_order_position_element_surfaceAreaFactor':
                    element.send_keys('1,00')
                if element.get_attribute('type') == 'text' and 'date-picker' in element.get_attribute('class'):
                    element.send_keys(strftime('%Y-%m-%d', localtime()))
                if element.get_attribute('type') == 'number':
                    element.send_keys(1)
                if element.get_attribute('id') == 'make_supplier_part_email':
                    element.send_keys('test@test.pl')
                if element.get_attribute('id') == 'make_user_defined_mail_content_content':
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'make_user_defined_mail_content_content_ifr')))
                    self.driver.execute_script("""tinymce.get('make_user_defined_mail_content_content').setContent('test content')""")
                    self.driver.execute_script("""tinymce.get('make_user_defined_mail_content_content').save()""")
                if element.get_attribute('id') == 'make_defined_contact_phoneNumber':
                    element.send_keys(Dictionary.helpdeskPhoneNumber)
                sleep(1)
            try:
                sleep(1)
                self.driver.find_element(By.XPATH, '//*[text()[contains(.,"Zapisz")]]').click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, CommonLocators.ELEMENT_SUCCESSFULLY_CREATED_XPATH)))
                self.stageStatusDictionaryCreate["słowniki - tworzenie"][dict_url] = 1
                try:
                    self.driver.find_element(By.XPATH, '//*[text()[contains(.,"Usuń")]]')
                    DictionariesCrud.dict_can_delete = True
                except NoSuchElementException:
                    DictionariesCrud.dict_can_delete = False
            except TimeoutException:
                try:
                    error_message = CommonMethods.get_500_error_message(self, self.driver)
                    print(f'po przy tworzeniu słownika pod adresem {self.driver.current_url} jest 500 o tresci: {error_message}')
                    self.stageStatusDictionaryCreate["słowniki - tworzenie"][dict_url] = str(0) + f'|{error_message}'
                    self.test_successful = False
                except NoSuchElementException:
                    print(f'po utworzeniu słownika pod adresem {self.driver.current_url} nie widzę potwierdzenia, zapisuje zrzut')
                    filename = f'tworzenie_slownika_{dict_url.replace("/", "")}_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                    self.driver.get_screenshot_as_file(f'TestResults/Settings/{filename}')
                    encoded = CommonMethods.encode_image_to_base64(f'TestResults/Settings/{filename}')
                    self.stageStatusDictionaryCreate["słowniki - tworzenie"][dict_url] = f'Fail|brak potwierdzenia utworzenia|{self.driver.current_url}|{encoded}'
                    self.test_successful = False
        with open('ValueStorage/słowniki - tworzenie.json', 'w', encoding='utf-8') as f:
            json.dump(self.stageStatusDictionaryCreate, f, ensure_ascii=False, indent=4)
        
        return self.test_successful

    def edit_dictionary_element_without_changes(self, dict_url):
        self.test_successful = True
        self.driver.get(self.driver.current_url + '/edit')
        try:
            error_message = CommonMethods.get_500_error_message(self, self.driver)
            print(f'po wejsciu w edycję słownika pod adresem {self.driver.current_url} jest 500 o tresci: {error_message}')
            self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = str(0) + f'|{error_message}'
            self.test_successful = False
        except NoSuchElementException:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, CommonLocators.DICTIONARY_BREADCRUMB_EDIT_INFO_XPATH)))
                try:
                    sleep(1)
                    self.driver.find_element(By.XPATH, '//*[text()[contains(.,"Zapisz")]]').click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, CommonLocators.ELEMENT_SUCCESSFULLY_UPDATED_XPATH)))
                    self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = 1
                except TimeoutException:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, CommonLocators.ELEMENT_SUCCESSFULLY_UPDATED_XPATH_2)))
                        self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = 1
                    except TimeoutException:
                        try:
                            error_message = CommonMethods.get_500_error_message(self, self.driver)
                            print(f'po zapisie słownika {dict_url} {self.driver.current_url} jest 500 o tresci: {error_message}')
                            self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = str(0) + f'|{error_message}'
                            self.test_successful = False
                        except NoSuchElementException:
                            print(f'po zapisie słownika pod adresem {self.driver.current_url} nie widzę potwierdzenia zapisu, zapisuje zrzut')
                            filename = f'zapis_slownika_{dict_url.replace("/", "")}_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                            self.driver.get_screenshot_as_file(f'TestResults/Settings/{filename}')
                            encoded = CommonMethods.encode_image_to_base64(f'TestResults/Settings/{filename}')
                            self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = f'Fail|brak formularza edycji|{self.driver.current_url}|{encoded}'
                            self.test_successful = False
            except TimeoutException:
                print(f'po wejsciu w edycję słownika pod adresem {self.driver.current_url} nie widzę formularza, zapisuje zrzut')
                filename = f'edycja_slownika_{dict_url.replace("/", "")}_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Settings/{filename}')
                encoded = CommonMethods.encode_image_to_base64(f'TestResults/Settings/{filename}')
                self.stageStatusDictionaryUpdate["słowniki - edycja"][dict_url] = f'Fail|brak formularza edycji|{self.driver.current_url}|{encoded}'
                self.test_successful = False
        with open('ValueStorage/słowniki - edycja.json', 'w', encoding='utf-8') as f:
            json.dump(self.stageStatusDictionaryUpdate, f, ensure_ascii=False, indent=4)
            
        return self.test_successful

    def delete_dictionary_element(self, dict_url):
        self.test_successful = True
        if self.dict_can_delete:
            self.driver.find_element(By.XPATH, '//*[text()[contains(.,"Usuń")]]').click()
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, 'confirmation-modal-confirm')))
                self.driver.find_element(By.ID, 'confirmation-modal-confirm').click()
                sleep(1)
                try:
                    try:
                        error_message = CommonMethods.get_500_error_message(self, self.driver)
                        print(f'po usunięciu słownika pod adresem {self.driver.current_url} jest 500 o tresci: {error_message}')
                        self.stageStatusDictionaryDelete["słowniki - usuwanie"][dict_url] = str(0) + f'|{error_message}'
                        self.test_successful = False
                    except NoSuchElementException:
                        self.driver.find_element(By.XPATH, CommonLocators.ELEMENT_SUCCESSFULLY_DELETED_XPATH)
                        self.stageStatusDictionaryDelete["słowniki - usuwanie"][dict_url] = 1
                except NoSuchElementException:
                    filename = f'po_usunieciu_slownika_{dict_url.replace("/", "")}_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                    self.driver.get_screenshot_as_file(f'TestResults/Settings/{filename}')
                    encoded = CommonMethods.encode_image_to_base64(f'TestResults/Settings/{filename}')
                    self.stageStatusDictionaryDelete["słowniki - usuwanie"][dict_url] = f'Fail|brak potwierdzenia{self.driver.current_url}|{encoded}'
                    print(f'po usunieciu slownika pod adresem  {self.driver.current_url} nie znajduję potwierdzenia, zapisuje zrzut')
                    self.test_successful = False
            except TimeoutException:
                print(f'przy próbie usunięcia słownika pod adresem {self.driver.current_url} nie widzę okna potwierdzenia, zapisuje zrzut')
                filename = f'usuwanie_slownika_{dict_url.replace("/", "")}_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Settings/{filename}')
                encoded = CommonMethods.encode_image_to_base64(f'TestResults/Settings/{filename}')
                self.stageStatusDictionaryDelete["słowniki - usuwanie"][dict_url] = f'Fail|brak formularza edycji{self.driver.current_url}|{encoded}'
                self.test_successful = False
        with open('ValueStorage/słowniki - usuwanie.json', 'w', encoding='utf-8') as f:
            json.dump(self.stageStatusDictionaryDelete, f, ensure_ascii=False, indent=4)
            
        return self.test_successful

    def test_01_crud_dictionary_test(self):
        self.driver.get(Dictionary.baseURL)
        CommonMethods.enter_valid_login_data_and_submit(self, self.driver)
        for dict_url in self.dict_urls:
            try:
                self.assertEqual(self.create_dictionary_element(dict_url), True)
                self.assertEqual(self.edit_dictionary_element_without_changes(dict_url), True)
                self.assertEqual(self.delete_dictionary_element(dict_url), True)
            except AssertionError:
                # dodaję except po to żeby test się nie przerwał i sprawdził pozostałe słowniki i na koniec wysłał szczegóły do API
                print('Wykryto błąd podczas testów, jednak został on pominięty, żeby zweryfikować pozostałe słowniki. Więcej szczegółów dostępne jest w podsumowaniu.')
        if use_api:
            ApiCommunication.send_stage_json_data('słowniki - tworzenie')
            ApiCommunication.send_stage_json_data('słowniki - edycja')
            ApiCommunication.send_stage_json_data('słowniki - usuwanie')

    @classmethod
    def tearDownClass(self):
        self.driver.quit()