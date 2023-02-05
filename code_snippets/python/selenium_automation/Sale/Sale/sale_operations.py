import json
import os
import unittest
from time import localtime, sleep, strftime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from Core.api import ApiCommunication
from Core.sale_locators import SaleLocators
from Core.common_locators import CommonLocators
from Core.common_methods import CommonMethods, setup_driver
from Core.dictionary import Dictionary
from Core.serviceorders_locators import ServiceordersLocators
from Sale.partial_operations import FinancePartialOperations
from ServiceOrders.partial_operations import OrderPartialOperations

use_api = os.getenv('API', 'False')
if use_api:
    print('Używam API przy sale_operations.')
else:
    print('API dla sale_operations nie jest dostępne.')


class SaleOperations(unittest.TestCase, CommonMethods):

    @classmethod
    def setUpClass(self):
        self.driver = setup_driver(webdriver)
        self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        self.errors = []
        with open('ValueStorage/finanse.json', 'r', encoding='utf-8') as f:
            self.stageStatus = json.loads(f.read())

    def setUp(self):
        self.t = localtime()

    def test_01_create_sale(self):
        self.test_successful = True
        self.driver.get(Dictionary.baseURL + Dictionary.saleListURL)
        CommonMethods.enter_valid_login_data_and_submit(self, self.driver)
        for o in range(4):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, SaleLocators.NEW_SALE_PARTIAL_LINK)))
                self.driver.find_element(By.PARTIAL_LINK_TEXT, SaleLocators.NEW_SALE_PARTIAL_LINK).click()
                sleep(1)
                try:
                    error_message = CommonMethods.get_500_error_message(self, self.driver)
                    print(
                        f'po wejsciu do formularza tworzenia fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                    self.stageStatus["finanse"]['Tworzenie FV'] = str(0) + f'|{error_message}'
                    self.test_successful = False
                except NoSuchElementException:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.ID, 'sale_kind')))
                    try:
                        sleep(1)
                        CommonMethods.set_first_option_from_select_by_id(self, self.driver, 'sale_warehouse')
                        WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'createSearchModal')))
                        customer_searcher = CommonMethods.find_first_in_multiple_class_elements_by_attribute_name_and_value(
                            self,
                            'createSearchModal',
                            'insertfield',
                            'sale_buyer')
                        sleep(1)
                        customer_searcher.click()
                        WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, CommonLocators.SEARCHER_FIRST_OPTION_CLASS)))
                        CommonMethods.insert_first_option_from_searcher(self)
                        WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'modal-content')))
                        self.driver.find_element(By.ID, 'fillPayerDataConfirm').click()
                        sleep(1)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);",
                                                   self.driver.find_element(By.ID, SaleLocators.RECALCULATE_SALE_POSITIONS_ID))
                        sleep(1)
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_element_located((By.ID, SaleLocators.NEW_SALE_POSITION_ID)))
                            self.driver.find_element(By.ID, SaleLocators.NEW_SALE_POSITION_ID).click()
                            stock_searcher = CommonMethods.find_first_in_multiple_class_elements_by_attribute_name_and_value(
                                self,
                                'createSearchModal',
                                'insertfield',
                                'sale_positions_0_element')
                            sleep(1)
                            stock_searcher.click()
                            sleep(1)
                        except TimeoutException:
                            filename = f'nowa_fv_towary_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                            print(
                                f'po utworzeniu nowej fv {self.driver.current_url} nie znajduję buttona dodawania towaru, zapisuje zrzut')
                            self.stageStatus["finanse"]['Tworzenie FV'] = 'Fail|brak buttona dodawania towaru'
                            self.test_successful = False
                            self.assertEqual(self.test_successful, True)
                        WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, CommonLocators.SEARCHER_FIRST_OPTION_CLASS)))
                        CommonMethods.insert_first_option_from_searcher(self)
                        sleep(1)
                        self.driver.find_element(By.ID, 'sale_positions_0_quantity').send_keys(1)
                        sleep(1)
                        self.driver.find_element(By.CLASS_NAME, 'js-formsubmit').click()
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_element_located(
                                    (By.XPATH, CommonLocators.RECORD_SUCCESSFULLY_CREATED_XPATH)))
                            CommonMethods.create_datafile(self, f'ValueStorage/url_faktury_{o}',
                                                          self.driver.current_url)
                            print(f'utworzono poprawnie, zapisuje numer i url {self.driver.current_url} w pliku')
                            SaleOperations.sale_url = self.driver.current_url
                            self.stageStatus["finanse"]['Tworzenie FV'] = 1
                        except TimeoutException:
                            try:
                                error_message = CommonMethods.get_500_error_message(self, self.driver)
                                print(
                                    f'przy zapisie fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                                self.stageStatus["finanse"]['Tworzenie FV'] = str(0) + f'|{error_message}'
                                self.test_successful = False
                                self.assertEqual(self.test_successful, True)
                            except NoSuchElementException:
                                filename = f'nowa_fv_zapis_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                                print(
                                    f'po utworzeniu nowej fv {self.driver.current_url} nie znajduję potwierdzenia utworzenia, zapisuje zrzut')
                                self.stageStatus["finanse"]['Tworzenie FV'] = 'Fail|brak potwierdzenia'
                                self.test_successful = False
                                self.assertEqual(self.test_successful, True)
                        sleep(3)
                    except NoSuchElementException:
                        filename = f'nowa_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                        self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                        print(
                            f'przy tworzeniu nowej fv {self.driver.current_url} nie znajduję formularza, zapisuje zrzut')
                        self.stageStatus["finanse"]['Tworzenie FV'] = 'Fail|brak formularza FV'
                        self.test_successful = False
                        self.assertEqual(self.test_successful, True)
            except NoSuchElementException:
                filename = f'nowa_fv_lista_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                print(
                    f'na liście FV {self.driver.current_url} nie znajduję buttona do tworzenia FV, zapisuje zrzut')
                self.stageStatus["finanse"]['Tworzenie FV'] = 'Fail|brak buttona do tworzenia FV'
                self.test_successful = False
                self.assertEqual(self.test_successful, True)
            if o < 3:
                self.driver.get(Dictionary.baseURL + Dictionary.saleListURL)
                sleep(1)

    def test_02_delete_unconfirmed_sale(self):
        self.test_successful = True
        self.driver.get(Dictionary.baseURL + Dictionary.saleListURL)
        try:
            SaleOperations.sale_url = CommonMethods.read_from_datafile(self, 'ValueStorage/url_faktury_3.txt')
            if SaleOperations.sale_url != '':
                try:
                    self.driver.get(SaleOperations.sale_url)
                    self.driver.find_element(By.XPATH, SaleLocators.DELETE_SALE_XPATH)
                except NoSuchElementException:
                    filename = f'usuwanie_niezatwierdzonej_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                    self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                    print(
                        f'przy usuwaniu niezatwierdzonej fv {self.driver.current_url} nie znajduję buttona usuwania, zapisuje zrzut')
                    self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = 'Fail|brak buttona Usuń'
                    self.test_successful = False
                    self.assertEqual(self.test_successful, True)
                self.driver.find_element(By.XPATH, SaleLocators.DELETE_SALE_XPATH).click()
                sleep(2)
                try:
                    error_message = CommonMethods.get_500_error_message(self, self.driver)
                    print(
                        f'przy usuwaniu niezatwierdzonej fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                    self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = str(0) + f'|{error_message}'
                    self.test_successful = False
                    self.assertEqual(self.test_successful, True)
                except NoSuchElementException:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'confirmation-modal-confirm')))
                        self.driver.find_element(By.ID, 'confirmation-modal-confirm').click()
                        sleep(1)
                        try:
                            self.driver.find_element(By.XPATH, SaleLocators.SALE_SUCCESSFULLY_DELETED_XPATH)
                            self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = 1
                            self.assertEqual(self.test_successful, True)
                        except NoSuchElementException:
                            filename = f'po_usunieciu_niezatwierdzonej_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                            self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = 'Fail|brak potwierdzenia'
                            print(
                                f'po usunieciu niezatwierdzonej fv {self.driver.current_url} nie znajduję potwierdzenia, zapisuje zrzut')
                            self.test_successful = False
                            self.assertEqual(self.test_successful, True)
                    except TimeoutException:
                        filename = f'usuwanie_niezatwierdzonej_fv_modal_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                        self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                        self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = 'Fail|brak modala potwierdzenia'
                        print(
                            f'nie znajduje modala do potwierdzenia usunięcia fv {self.driver.current_url} zapisuje zrzut')
                        self.test_successful = False
                        self.assertEqual(self.test_successful, True)
        except FileNotFoundError:
            print('brak fv do usuniecia - nie znaleziono pliku z numerem')
            self.stageStatus["finanse"]['Usuwanie niezatwierdzonej FV'] = 'Fail|brak danych faktury'
            self.test_successful = False
            self.assertEqual(self.test_successful, True)

    def test_03_confirm_sale(self):
        self.test_successful = True
        self.stageStatus["finanse"]['Zatwierdzanie FV'] = 0
        for i in range(3):
            self.driver.get(Dictionary.baseURL + Dictionary.saleListURL)
            try:
                SaleOperations.sale_url = CommonMethods.read_from_datafile(self, f'ValueStorage/url_faktury_{i}.txt')
                if SaleOperations.sale_url != '':
                    data = FinancePartialOperations.confirm_sale(self, SaleOperations.sale_url, True)
                    self.stageStatus["finanse"]['Zatwierdzanie FV'] = data[0]
                    self.assertEqual(data[1], True)
            except FileNotFoundError:
                print('brak fv do usuniecia - nie znaleziono pliku z numerem')
                self.stageStatus["finanse"]['Zatwierdzanie FV'] = 'Fail|brak danych faktury'
                self.test_successful = False
                self.assertEqual(self.test_successful, True)

    def test_04_make_invoice_all_from_order_fault(self):
        order_url = CommonMethods.read_from_datafile(self, 'ValueStorage/url_zlecenia_1.txt')
        order_incomes = {'Robocizna blacharska': {'quantity': 2, 'price_net_before_discount': 180, 'discount': 0},
                         'Robocizna lakiernicza': {'quantity': 2, 'price_net_before_discount': 180, 'discount': 5}
                         }
        self.driver.get(order_url)
        sleep(1)
        self.driver.find_element(By.ID, ServiceordersLocators.EDIT_ORDER_BUTTON_ID).click()
        CommonMethods.change_order_select_value_by_id_in_order_edit_mode(self, self.driver, 'make_ordersbundle_serviceorder_status', 'NZ (Naprawa zakończona)')
        sleep(3)
        self.driver.find_element(By.XPATH, ServiceordersLocators.SAVE_ORDER_BUTTON_XPATH).click()
        sleep(3)
        self.add_incomes_to_order = OrderPartialOperations.add_income_to_fault(self, self.driver, order_url,
                                                                               data=order_incomes)
        if self.add_incomes_to_order:
            # na razie brak obsługi scenariusza gdy wywołujemy te akcje spoza kontekstu testu, czyli gdzie stageStatus=False
            self.sale_from_fault = FinancePartialOperations.invoice_all_incomes_from_order_fault(self, order_url, stageStatus=True)
            if self.sale_from_fault[1]:  # [0] to szczegóły, [1] to bool czy operacja się powiodła, [2] to adres url dokumentu do dalszej obróbki
                self.sale_from_fault = FinancePartialOperations.confirm_sale(self, self.sale_from_fault[2], stageStatus=True)
                if self.sale_from_fault[1]:  # [0] to szczegóły, [1] to bool czy operacja się powiodła
                    self.stageStatus["finanse"]['FV z rozliczeń'] = self.sale_from_fault[0]
                    self.assertEqual(self.sale_from_fault[1], True)
                else:
                    self.stageStatus["finanse"]['FV z rozliczeń'] = self.sale_from_fault[0]
                    self.assertEqual(self.sale_from_fault[1], True)
            else:
                self.stageStatus["finanse"]['FV z rozliczeń'] = self.sale_from_fault[0]
                self.assertEqual(self.sale_from_fault[1], True)
        else:
            self.stageStatus["finanse"]['FV z rozliczeń'] = self.add_incomes_to_order
            self.assertEqual(self.add_incomes_to_order, True)

    def summary(self):
        with open('ValueStorage/finanse.json', 'w', encoding='utf-8') as f:
            print(f'dopisuję: {self.stageStatus}')
            json.dump(self.stageStatus, f, ensure_ascii=False, indent=4)
        if use_api:
            ApiCommunication.send_stage_json_data('finanse')

    @classmethod
    def tearDownClass(self):
        self.summary(self)
        self.driver.quit()