import json
import os
import time
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from Core.api import ApiCommunication
from Core.common_methods import CommonMethods, setup_driver
from Core.dictionary import Dictionary

use_api = os.getenv('API', 'False')
if use_api:
    print('Używam API przy sale_smoke.')
else:
    print('API dla sale_smoke nie jest dostępne.')


class SaleSmoke(unittest.TestCase, CommonMethods):

    @classmethod
    def setUpClass(self):
        self.driver = setup_driver(webdriver)
        self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        self.errors = []
        with open('ValueStorage/smoke.json', 'r', encoding='utf-8') as f:
            self.stageStatus = json.loads(f.read())

    def setUp(self):
        self.t = time.localtime()

    def test_01_sale_list(self):
        self.test_successful = True
        self.driver.get(Dictionary.baseURL + Dictionary.saleListURL)
        CommonMethods.enter_valid_login_data_and_submit(self, self.driver)
        try:
            error_message = CommonMethods.get_500_error_message(self, self.driver)
            print(
                f'po wejsciu na listę sprzedaży {self.driver.current_url} jest 500 o tresci: {error_message}')
            self.stageStatus["smoke"]['Lista dokumentów sprzedaży'] = str(0) + f'|{error_message}'
            self.test_successful = False
        except NoSuchElementException:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'filtersPanel')))
                self.stageStatus["smoke"]['Lista dokumentów sprzedaży'] = 1
                self.assertEqual(self.test_successful, True)
            except TimeoutException:
                filename = f'lista_sprzedazy_{time.strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                self.stageStatus["smoke"]['Lista dokumentów sprzedaży'] = 'Fail|timeout'
                print(
                    f'po wejściu na listę sprzedaży {self.driver.current_url} nie widzę wyników, zapisuje zrzut')
                self.test_successful = False
                self.assertEqual(self.test_successful, True)

    def test_02_account_book(self):
        self.test_successful = True
        self.driver.get(Dictionary.baseURL + Dictionary.accountBookURL)
        try:
            error_message = CommonMethods.get_500_error_message(self, self.driver)
            print(
                f'po wejsciu do zeszytu {self.driver.current_url} jest 500 o tresci: {error_message}')
            self.stageStatus["smoke"]['Zeszyt'] = str(0) + f'|{error_message}'
            self.test_successful = False
        except NoSuchElementException:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'filtersPanel')))
                self.stageStatus["smoke"]['Zeszyt'] = 1
                self.assertEqual(self.test_successful, True)
            except TimeoutException:
                filename = f'zeszyt_{time.strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                self.stageStatus["smoke"]['Zeszyt'] = 'Fail|timeout'
                print(
                    f'po wejściu do zeszytu {self.driver.current_url} nie widzę wyników, zapisuje zrzut')
                self.test_successful = False
                self.assertEqual(self.test_successful, True)

    def summary(self):
        with open('ValueStorage/smoke.json', 'w', encoding='utf-8') as f:
            json.dump(self.stageStatus, f, ensure_ascii=False, indent=4)
        if use_api:
            ApiCommunication.send_stage_json_data('smoke')
        
    @classmethod
    def tearDownClass(self):
        self.summary(self)
        self.driver.quit()
