import json
import os
from time import sleep, strftime
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from Core.common_locators import CommonLocators
from Core.common_methods import CommonMethods
from Core.dictionary import Dictionary
from Core.sale_locators import SaleLocators
from Core.serviceorders_locators import ServiceordersLocators


class FinancePartialOperations:

    def confirm_sale(self, sale_url, stageStatus=False, with_changes_on_document_positions=False):
        try:
            self.driver.get(sale_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SaleLocators.CONFIRM_SALE_CSS)))
            if with_changes_on_document_positions:
                '''dopisz weryfikacje danych w modalu jak zmieniasz ilosci czy kwoty na pozycjach'''
                pass
            self.driver.find_element(By.CSS_SELECTOR, SaleLocators.CONFIRM_SALE_CSS).click()
            sleep(1)
            try:
                error_message = CommonMethods.get_500_error_message(self, self.driver)
                print(f'przy zatwierdzaniu niezatwierdzonej fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                if stageStatus:
                    return [str(0) + f'|{error_message}', False]
                else:
                    return False
            except NoSuchElementException:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'confirmation-modal-confirm')))
                    self.driver.find_element(By.CLASS_NAME, 'approve-button').click()
                    sleep(1)
                    try:
                        error_message = CommonMethods.get_500_error_message(self, self.driver)
                        print(f'przy zatwierdzaniu niezatwierdzonej fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                        if stageStatus:
                            return [str(0) + f'|{error_message}', False]
                        return False
                    except NoSuchElementException:
                        try:
                            filename = f'po_zatwierdzanie_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                            self.driver.find_element(By.XPATH, SaleLocators.SALE_SUCCESSFULLY_APPROVED_XPATH)
                            if stageStatus:
                                return [1, True]
                            return True
                        except NoSuchElementException:
                            filename = f'po_zatwierdzeniu_niezatwierdzonej_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                            if stageStatus:
                                return ['Fail|brak potwierdzenia', False]
                            print(f'po zatwierdzeniu niezatwierdzonej fv {self.driver.current_url} nie znajduję potwierdzenia, zapisuje zrzut')
                            return False
                except TimeoutException:
                    filename = f'zatwierdzanie_niezatwierdzonej_fv_modal_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                    self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                    if stageStatus:
                        return ['Fail|brak modala potwierdzenia', False]
                    print(f'nie znajduje modala do potwierdzenia zatwierdzenia fv {self.driver.current_url} zapisuje zrzut')
                    return False
        except TimeoutException:
            filename = f'zatwierdzanie_niezatwierdzonej_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
            print(f'nie znajduje buttona do potwierdzenia zatwierdzenia fv {self.driver.current_url} zapisuje zrzut')
            if stageStatus:
                return ['Fail|brak buttona Zatwierdź', False]
            return False

    def invoice_all_incomes_from_order_fault(self, order_url, stageStatus=False):
        self.driver.get(f'{order_url}/calculations')
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, ServiceordersLocators.INVOICE_ALL_FAULT_POSITIONS_IN_ORDER_XPATH)))
            self.driver.find_element(By.XPATH, ServiceordersLocators.INVOICE_ALL_FAULT_POSITIONS_IN_ORDER_XPATH).click()
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, ServiceordersLocators.NORMALIA_MODAL_CONFIRM_BUTTON_XPATH)))
                sleep(2)
                self.driver.find_element(By.XPATH, ServiceordersLocators.NORMALIA_MODAL_CONFIRM_BUTTON_XPATH).click()
                try:
                    sleep(1)
                    error_message = CommonMethods.get_500_error_message(self, self.driver)
                    print(f'po wejsciu do formularza tworzenia fv {self.driver.current_url} jest 500 o tresci: {error_message}')
                    if stageStatus:
                        return [str(0) + f'|{error_message}', False]
                    return False
                except NoSuchElementException:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.ID, SaleLocators.SALE_FORM_ID)))
                        sleep(1)
                        CommonMethods.set_first_option_from_select_by_id(self, self.driver, 'sale_warehouse')
                        sleep(1)
                        self.driver.find_element(By.CLASS_NAME, 'js-formsubmit').click()
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_element_located(
                                    (By.XPATH, CommonLocators.RECORD_SUCCESSFULLY_CREATED_XPATH)))
                            CommonMethods.create_datafile(self, f'ValueStorage/url_faktury_ze_zlecenia',
                                                          self.driver.current_url)
                            print(f'utworzono poprawnie, zapisuje numer i url {self.driver.current_url} w pliku')
                            if stageStatus:
                                return [1, True, self.driver.current_url]
                            return [True, self.driver.current_url]
                        except TimeoutException:
                            try:
                                error_message = CommonMethods.get_500_error_message(self, self.driver)
                                print(f'przy zapisie fv ze zlecenia {self.driver.current_url} jest 500 o tresci: {error_message}')
                                if stageStatus:
                                    return [str(0) + f'|{error_message}', False]
                                return False
                            except NoSuchElementException:
                                filename = f'fv_ze_zlecnia_zapis_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                                print(f'po utworzeniu nowej fv {self.driver.current_url} z rozliczen nie znajduję potwierdzenia utworzenia, zapisuje zrzut')
                                if stageStatus:
                                    return ['Fail|brak potwierdzenia', False]
                                return False
                    except TimeoutException:
                        filename = f'fv_ze_zlecenia_formularz_fv_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                        self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                        print(f'po przejściu ze zlecenia nie widzę formularza faktury {self.driver.current_url} zapisuje zrzut')
                        if stageStatus:
                            return ['Fail|brak formularza faktury po akcji w zleceniu', False]
                        return False
            except TimeoutException:
                filename = f'fv_ze_zlecenia_modal_normalia_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
                self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
                print(f'nie widzę modala dodawania normaliów w zleceniu {self.driver.current_url} zapisuje zrzut')
                if stageStatus:
                    return ['Fail|brak modala dodawania normaliów w zleceniu', False]
                return False
        except TimeoutException:
            filename = f'fv_ze_zlecenia_{strftime("%Y%m%d_%H%M%S", self.t)}.png'
            self.driver.get_screenshot_as_file(f'TestResults/Sale/{filename}')
            print(f'nie znajduje buttona do fakturowania w zleceniu {self.driver.current_url} zapisuje zrzut')
            if stageStatus:
                return ['Fail|brak buttona do fakturowania w zleceniu', False]
            return False