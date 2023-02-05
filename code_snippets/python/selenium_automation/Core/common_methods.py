import base64
from email.encoders import encode_base64
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import requests
import smtplib
from smtplib import SMTPException
import string
from time import sleep
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from Core.common_locators import CommonLocators
from Core.dictionary import Dictionary
from Core.warehouse_locators import WarehouseLocators


def setup_driver(webdriver, proxy=False):
    if os.name == 'nt':
        chromedriver_path = 'Core/libs/'
        chromedriver_autoinstaller.install(path=chromedriver_path)
        newest = max([f for f in os.listdir(chromedriver_path)], key=lambda x: os.stat(os.path.join(chromedriver_path, x)).st_ctime)
        chrome_options = webdriver.ChromeOptions()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={PROXY}')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
        chrome_options.add_experimental_option("excludeSwitches", ["disable-automation"])
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chromedriver_full_path = f'Core\libs\{newest}\chromedriver.exe'
        service = ChromeService(executable_path=chromedriver_full_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        chrome_options = webdriver.ChromeOptions()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={PROXY}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
        chrome_options.add_experimental_option("excludeSwitches", ['disable-automation'])
        chrome_options.set_capability("pageLoadStrategy", "eager")
        return webdriver.Chrome(options=chrome_options)


class CommonMethods:

    def enter_valid_login_data_and_submit(self, driver):
        self.driver.find_element(By.ID, CommonLocators.LOGIN_FIELD_INPUT_ID).send_keys(Dictionary.validLoginAutomationUser)
        self.driver.find_element(By.ID, CommonLocators.PASSWORD_FIELD_INPUT_ID).send_keys(Dictionary.validPasswordAutomationUser)
        self.driver.find_element(By.ID, CommonLocators.LOGIN_SUBMIT_BUTTON_ID).click()

    def enter_invalid_login_data_and_submit(self, driver):
        self.driver.find_element(By.ID, CommonLocators.LOGIN_FIELD_INPUT_ID).send_keys(
            CommonMethods.generate_random_lowercase_string(self, 6))
        self.driver.find_element(By.ID, CommonLocators.PASSWORD_FIELD_INPUT_ID).send_keys(
            CommonMethods.generate_random_lowercase_string(self, 6))
        self.driver.find_element(By.ID, CommonLocators.LOGIN_SUBMIT_BUTTON_ID).click()

    def get_500_error_message(self, driver, use_wait=False):
        if use_wait:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, CommonLocators.PANEL_500_ERROR_ID)))
                self.driver.find_element(By.ID, CommonLocators.PANEL_500_ERROR_ID)
                self.driver.find_element(By.ID, CommonLocators.PANEL_500_ERROR_MESSAGE_BUTTON_ID).click()
                error_text = self.driver.find_element_by(By.ID, CommonLocators.PANEL_500_ERROR_MESSAGE_ID).text
                return error_text
            except TimeoutException:
                raise NoSuchElementException
        else:
            self.driver.find_element(By.ID, CommonLocators.PANEL_500_ERROR_ID)
            self.driver.find_element(By.ID, CommonLocators.PANEL_500_ERROR_MESSAGE_BUTTON_ID).click()
            error_text = self.driver.find_element(By.ID, CommonLocators.PANEL_500_ERROR_MESSAGE_ID).text
            return error_text

    def enter_to_searcher(self, driver, search_string):
        self.driver.find_element(By.XPATH, CommonLocators.SEARCHER_XPATH).send_keys(search_string)

    def generate_random_lowercase_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def set_first_option_from_select_by_id(self, driver, element_id):
        select = driver.find_element(By.ID, element_id)
        mySelect = Select(select)
        mySelect.select_by_index(1)

    def set_defined_index_option_from_select_by_id(self, driver, element_id, index=1):
        select = driver.find_element(By.ID, element_id)
        mySelect = Select(select)
        mySelect.select_by_index(index)

    def set_random_option_from_select_by_id(self, driver, element_id):
        select = driver.find_element(By.ID, element_id)
        mySelect = Select(select)
        values = [x for x in select.find_elements(By.TAG_NAME, "option")]
        vals = [element.get_attribute('value') for element in values if str(element.get_attribute('value')) != ""]
        mySelect.select_by_value(f"{vals[random.randint(0, len(vals) - 1)]}")

    def set_first_option_from_select_by_xpath(self, driver, xpath):
        select = driver.find_element(By.XPATH, xpath)
        mySelect = Select(select)
        mySelect.select_by_index(1)

    def set_first_option_from_select_without_placeholder_by_xpath(self, driver, xpath):
        select = driver.find_element(By.XPATH, xpath)
        mySelect = Select(select)
        mySelect.select_by_index(0)

    def get_attribute_from_selected_in_select_by_xpath(self, driver, xpath, attribute):
        select = driver.find_element(By.XPATH, xpath)
        mySelect = Select(select)
        return mySelect.first_selected_option.get_attribute(attribute)

    def set_random_option_from_select_by_xpath(self, driver, xpath):
        select = driver.find_element(By.XPATH, xpath)
        mySelect = Select(select)
        values = [x for x in select.find_elements(By.TAG_NAME, "option")]
        vals = [element.get_attribute('value') for element in values if str(element.get_attribute('value')) != ""]
        mySelect.select_by_value(f"{vals[random.randint(0, len(vals) - 1)]}")

    def count_html_elements_by_xpath(self, xpath):
        return len(self.driver.find_elements(By.XPATH, xpath))

    def find_first_in_multiple_class_elements_by_attribute_name_and_value(self, class_name, attribute, value):
        result = [x for x in self.driver.find_elements(By.CLASS_NAME, class_name) if x.get_attribute(attribute) == value]
        return result[0]

    def find_second_in_multiple_class_elements_by_attribute_name_and_value(self, class_name, attribute, value):
        result = [x for x in self.driver.find_elements(By.CLASS_NAME, class_name) if x.get_attribute(attribute) == value]
        return result[1]

    def find_last_in_multiple_class_elements_by_attribute_name_and_value(self, class_name, attribute, value):
        result = [x for x in self.driver.find_elements(By.CLASS_NAME, class_name) if x.get_attribute(attribute) == value]
        return result[-1]

    def find_first_in_multiple_name_elements_by_attribute_name_and_value(self, name, attribute, value):
        result = [x for x in self.driver.find_elements(By.NAME, name) if x.get_attribute(attribute) == value]
        return result[0]

    def insert_first_option_from_searcher(self):
        self.driver.find_element(By.CLASS_NAME, CommonLocators.SEARCHER_FIRST_OPTION_CLASS).click()

    def get_window_height(self):
        return self.driver.get_window_size()['height']

    def create_datafile(self, name, content):
        with open(name + '.txt', 'w') as file:
            file.write(content)
            file.close()

    def read_from_datafile(self, name):
        with open(name, 'r') as file:
            return file.read()

    def get_cash_balance_checkout(self, element_id):
        cash_balance = self.driver.find_element(By.ID, element_id).get_attribute("innerHTML").replace(' ', '').replace('\n', '')
        cash_balance_try_iterator = 0
        while cash_balance == '':
            cash_balance_try_iterator += 1
            print(f'nie pobrano stanu kasy, ponawiam próbę {cash_balance_try_iterator} z 10')
            sleep(1)
            cash_balance = self.driver.find_element(By.ID, element_id).get_attribute("innerHTML").replace(' ', '').replace('\n', '')
            if cash_balance_try_iterator == 10:
                print('nie pobrano stanu kasy - przerywam test')
                raise AssertionError
        return float(self.driver.find_element(By.ID, element_id).get_attribute("innerHTML").replace(' ', ''))

    def generate_random_float_value_under_10000(self):
        return round(random.uniform(0.01, 9999.99), 2)

    def send_email_only_text(self, subject, content):
        try:
            server = smtplib.SMTP_SSL('smtp.iq.pl', 465)
            server.login(Dictionary.memajl_u, Dictionary.memajl_p)
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = Dictionary.mailfrom
            msg['To'] = Dictionary.mailto
            msg.set_content(content)
            server.send_message(msg)
            server.quit()
        except SMTPException:
            print("Nie udało się wysłac maila")

    def send_email_with_image(self, subject, content, image, recipient=False):
        if recipient:
            recipient = recipient
        else:
            recipient = Dictionary.mailto
        try:
            server = smtplib.SMTP_SSL('smtp.iq.pl', 465)
            server.login(Dictionary.memajl_u, Dictionary.memajl_p)
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = Dictionary.mailfrom
            msg['To'] = recipient
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            with open(image, 'rb') as f:
                mime = MIMEBase('image', 'png', filename=image)
                mime.add_header('Content-Disposition', 'attachment', filename=image)
                mime.add_header('X-Attachment-Id', '0')
                mime.add_header('Content-ID', '<0>')
                mime.set_payload(f.read())
                encode_base64(mime)
                msg.attach(mime)
            server.send_message(msg)
            server.quit()
        except SMTPException:
            print("Nie udało się wysłac maila")

    def send_summary_email(self, subject, content, recipient=False):
        if recipient:
            recipient = recipient
        else:
            recipient = Dictionary.mailto
        try:
            server = smtplib.SMTP_SSL('smtp.iq.pl', 465)
            server.login(Dictionary.memajl_u, Dictionary.memajl_p)
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = Dictionary.mailfrom
            msg['To'] = recipient
            msg.set_type('text/html')
            msg.add_alternative(content, subtype='html')
            server.send_message(msg)
            server.quit()
        except SMTPException:
            print("Nie udało się wysłac maila")

    def save_summary_email_as_html(self, content, api=False):
        if api:
            fileName = 'ValueStorage/index2.html'
        else:
            fileName = 'ValueStorage/index.html'
        with open(fileName, 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()

    def get_number_list_of_attributes_by_attribute_name_and_xpath(self, target_xpath, attribute_name,
                                                                  attribute_xpath_left, attribute_xpath_right):
        """metoda zwraca listę atrybutów dla elementów np. tabel gdzie musimy klikać w buttony poza obszarem klikalności
        pierwszy indeks to liczba znalezionych elementów, potem są to elementy jak np. hrefy do pozycji slowników
        działa dla attribute_xpath wymagającego zmiennych wartości po każdym przebiegu pętli np. wykorzystującyh f'td[{i}]'"""
        list_of_attributes = [CommonMethods.count_html_elements_by_xpath(self, target_xpath)]
        for i in range(1, list_of_attributes[0] + 1):
            list_of_attributes.append(
                self.driver.find_element(By.XPATH, attribute_xpath_left + f'{i}' + attribute_xpath_right).get_attribute(
                    attribute_name))
        return list_of_attributes

    def get_is_checked_by_xpath(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).is_selected()

    def get_all_multiselect_active_values_by_xpath(self, xpath):
        """metoda zwraca w postaci stringa atrybuty wszystkich <li> w multiselekcie"""
        values = ''
        for position in self.driver.find_elements(By.XPATH, xpath):
            value = position.get_attribute("title")
            if value != '':
                values += str(value + ', ')
        values = values[:-2]
        return values

    def check_500_code_error_in_request_response(self, driver, module_name, mode_error=False):
        """metoda zwraca True jeśli jakiś request na stronie dostał w odpowiedzi kod 500"""
        for request in self.driver.requests:
            if request.response:
                if request.response.status_code == 500 and not ('fontawesome') in request.url and not ('/zabbix.php') in request.url and not ('/uploads/') in request.url and not ('.jpg') in request.url and not ('.jpeg') in request.url and not ('.png') in request.url:
                    if mode_error:
                        message = f'po wejsciu na: {module_name} {self.driver.current_url} wywołanie {request.url} w konsoli kończy się kodem 500'
                        print(message)
                        return [True, message]
                    else:
                        print(f'po wejsciu na: {module_name} {self.driver.current_url} wywołanie {request.url} w konsoli kończy się kodem 500')
                        return True

        if mode_error:
            return [False, '']
        else:
            return False

    def count_form_elements_by_form_id(self, form_id):
        return len(self.driver.find_elements(By.XPATH, f'//form[@id="{form_id}"]/*'))

    def get_required_form_elements_by_form_id(self, form_id):
        return self.driver.find_elements(By.XPATH, f'//form[@id="{form_id}"]//label[contains(@class, "required")]')

    def get_required_form_elements(self):
        return self.driver.find_elements(By.XPATH, '//form[boolean(@id) and not(contains(@id, "make") or contains(@id, "Ajax") or contains(@id, "department_context_choice"))]//label[contains(@class, "required")]')

    def edit_dictionary_without_changes_by_dictionary_direct_link(self, driver, direct_url):
        self.driver.get(direct_url)

    def change_order_select_value_by_id_in_order_edit_mode(self, driver, select_data, value_to_set):
        select = driver.find_element(By.ID, select_data)
        mySelect = Select(select)
        mySelect.select_by_visible_text(value_to_set)
