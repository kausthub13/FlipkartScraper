import datetime
import inspect
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

FIREFOX_PATH = ChromeDriverManager().install()
# FIREFOX_PATH=r'C:\Users\kesavadas.k\.wdm\drivers\chromedriver\win64\116.0.5845.188\chromedriver-win32\chromedriver.exe'
print(FIREFOX_PATH)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FLIPKART_LINK = "https://www.flipkart.com/books/pr?sid=bks&q="

threads = None
pincode = None
folder_path = None


import tkinter as tk
from tkinter import filedialog
from tkinter import *


class InputForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Input Form")

        # Configure the root window to stretch
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Label and entry widget for the pincode
        self.pincode_label = tk.Label(self, text="Enter Pincode:")
        self.pincode_label.grid(row=0, column=0, padx=10, pady=5)
        self.pincode_entry = tk.Entry(self)
        self.pincode_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Label and entry widget for the folder path
        self.folder_label = tk.Label(self, text="Select a Folder:")
        self.folder_label.grid(row=1, column=0, padx=10, pady=5)
        self.folder_path_var = tk.StringVar()
        self.folder_path_entry = tk.Entry(self, textvariable=self.folder_path_var, state='readonly')
        self.folder_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Button to open the folder dialog
        self.folder_browse_button = tk.Button(self, text="Browse", command=self.open_folder_dialog)
        self.folder_browse_button.grid(row=1, column=2, padx=10, pady=5)

        # Button to submit the form
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_and_close)
        self.submit_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)

    def submit_and_close(self):
        global pincode,folder_path
        pincode = self.pincode_entry.get()
        folder_path = self.folder_path_var.get()

        # You can perform actions with the pincode and folder_path here
        print(f"Pincode: {pincode}")
        print(f"Folder Path: {folder_path}")

        # Close the UI window
        self.destroy()


def set_logger(log_name=''):
    '''
    Handles Multithreading logging
    :param log_name: this gives unique log_name to each thread under the base folder
    :return:
    '''
    logger = logging.getLogger(log_name)
    filename = os.path.join(DAY_LOG_DIR, log_name + '.log')
    # print(filename)
    # print(logger.handlers)
    # print(logger.hasHandlers())
    if logger.handlers == []:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename=filename)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(funcName)s][%(levelname)s] %(message)s',
                                      datefmt='%d/%b/%Y %I:%M:%S %p %Z')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # print(logger.handlers)
    return logger


def get_number(text):
    price = ''
    for i in str(text):
        if i.isdigit() or i == '.':
            price += i
    if price:
        return float(price)
    else:
        return 0


class FlipkartScraper:
    def __init__(self, id, total_rows, input_file, output_file, pincode, isbn):
        self.id = id
        self.total_rows = total_rows
        self.input_file = input_file
        # self.output_file = output_file.replace('xlsx', 'csv')
        self.output_file = output_file
        self.pincode = pincode
        self.isbn = str(isbn)
        self.logger = set_logger(str(self.isbn))
        self.logger.info(f'WRITING LOGS for ISBN : {self.isbn} \n\n\n')
        self.record = dict()
        self.buybox_repro = 'No'
        self.buybox_seller_name = ''
        self.buybox_seller_price = ''
        self.buybox_seller_delivery = ''
        self.other_sellers_list = []
        self.repro_listed = "No"
        self.seller_id = -1
        try:
            self.main()
        except Exception as e:
            self.logger.error(f'Exception : {e}')
        finally:
            self.prepare_record()
            self.write_excel_sheet()
            self.driver.quit()
            self.logger.info('Driver Closed')
        # self.main()

    # def write_excel_sheet(self):
    #     try:
    #         self.logger.info(f'Writing to excel sheet : {self.output_file}')
    #         # self.logger.info(f'Record To Write : {self.record}')
    #         with threading.Lock():
    #             if not os.path.exists(self.output_file):
    #                 self.write_header = True
    #             else:
    #                 self.write_header = False
    #             with open(self.output_file, 'a') as csvfile:
    #                 writer = csv.DictWriter(csvfile, fieldnames=self.record.keys())
    #                 if self.write_header:
    #                     writer.writeheader()
    #                 writer.writerow(self.record)
    #     except Exception as e:
    #         self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def write_excel_sheet(self):
        with threading.Lock():
            print(self.record)

            if os.path.exists(self.output_file):
                df = pd.read_excel(self.output_file,engine='openpyxl')
                df.loc[len(df)] = self.record
            else:
                for key in self.record:
                    self.record[key] = [self.record[key]]

                df = pd.DataFrame(self.record)
            df.to_excel(self.output_file,index=False,engine='openpyxl')
            self.logger.info('Write Entry To Excel Sheet')

    def setup_flipkart_driver(self):
        try:
            self.logger.info('setting up flipkart driver')
            options = Options()
            options.add_argument('--headless')
            # options.add_argument('--no-sandbox')
            # options.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.driver = webdriver.Chrome(service=Service(executable_path=FIREFOX_PATH),
                                            options=options)
            self.driver.implicitly_wait(10)
            self.logger.info('Driver initiated')
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def open_flipkart_page(self):
        try:
            self.current_page = FLIPKART_LINK + str(self.isbn)
            self.logger.info(f'Opening Page : {self.current_page}')
            self.driver.get(self.current_page)
            self.logger.info('Page Openend')
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def get_search_result(self):
        try:
            self.logger.info(f'Getting Search Link')
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "s1Q9rs"))
            # )
            self.search_result_link = self.driver.find_element(By.CLASS_NAME, 's1Q9rs').get_attribute('href')
            self.logger.info('Search Link Obtained')
            self.driver.get(self.search_result_link)
            self.logger.info('Opening Book Page')
            return True
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")
            return False

    def set_pincode(self):
        try:
            pincode_setter = self.driver.find_element(By.ID, 'pincodeInputId')
            pincode_setter.send_keys(self.pincode)
            pincode_check = self.driver.find_element(By.CLASS_NAME, '_2P_LDn')
            pincode_check.click()
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e.args[0]}")

    def get_buybox_seller(self):
        try:
            self.logger.info('Fetching Buybox Details')
            self.logger.info('Getting Buybox Seller Name')
            self.get_buybox_name()
            self.logger.info('Getting Buybox Seller Price')
            self.get_buybox_price()
            self.logger.info('Getting Buybox Seller Delivery Date')
            self.get_buybox_delivery()
            self.buybox_repro = self.check_repro_seller(self.buybox_seller_name)
            self.repro_listed = self.buybox_repro
            self.logger.info(f'Buybox Repro : {self.buybox_repro}')
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def get_buybox_name(self):
        self.buybox_seller_id = self.driver.find_element(By.ID, "sellerName")
        self.buybox_seller_name = str(
            self.buybox_seller_id.find_element(By.TAG_NAME, 'span').find_element(By.TAG_NAME, 'span').text)
        self.logger.info(f'Buybox Seller Name : {self.buybox_seller_name}')

    def get_buybox_price(self):
        self.buybox_seller_price = get_number(
            str(self.driver.find_element(By.CSS_SELECTOR, "div[class='_30jeq3 _16Jk6d']").text))
        self.logger.info(f'Buybox Seller Price : {self.buybox_seller_price}')

    def get_buybox_delivery(self):
        self.buybox_seller_delivery = str(
            self.driver.find_element(By.CSS_SELECTOR, "div[class='_3XINqE']").text).replace("Delivery by", '')
        self.logger.info(f'Buybox Delivery Price : {self.buybox_seller_delivery}')

    def get_other_sellers_page(self):
        try:
            self.logger.info('Getting Other Sellers Page')
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "div[class='_38I6QT']"))
            # )
            self.other_sellers_link = self.driver.find_element(By.CLASS_NAME, '_38I6QT').find_element(By.TAG_NAME,
                                                                                                      'a').get_attribute(
                "href")
            self.driver.get(self.other_sellers_link)
            time.sleep(4)
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def get_other_sellers_selector(self):
        try:
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='_2Y3EWJ']"))
            # )
            self.sellers_list = self.driver.find_elements(By.CSS_SELECTOR, "div[class='_2Y3EWJ']")

            if self.sellers_list:
                for sellers in self.sellers_list:
                    self.seller_id += 1
                    self.seller = sellers
                    self.get_seller_name()
                    self.get_seller_price()
                    self.get_seller_delivery()
                    self.add_seller_to_list()
                    if self.check_repro_seller(self.other_seller) == 'Yes':
                        self.repro_listed = 'Yes'
                final_list = [','.join(other_seller) for other_seller in self.other_sellers_list]
                final_list = ':'.join(final_list)
                self.other_sellers_list = final_list
            else:
                self.logger.info('No Other Sellers Found')
        except Exception as e:
            self.logger.debug('Other Sellers Not Found')
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def get_seller_name(self):
        self.other_seller = str(self.seller.find_element(By.CSS_SELECTOR, "div[class='_3enH42']").text)
        if not self.buybox_seller_name:
            self.buybox_seller_name = self.other_seller
        self.logger.info(f'Other Seller Name : {self.other_seller}')

    def get_seller_price(self):
        self.other_seller_price = get_number(
            str(self.seller.find_element(By.CSS_SELECTOR, "div[class='_30jeq3']").text))
        if not self.buybox_seller_price:
            self.buybox_seller_price = self.other_seller_price
        self.logger.info(f'Other Seller Price : {self.other_seller_price}')

    def get_seller_delivery(self):
        self.other_seller_delivery = str(self.seller.find_element(By.CSS_SELECTOR,
                                                                  "div[class='_3XINqE']").text).replace("Delivery by",
                                                                                                        '')
        if not self.buybox_seller_delivery:
            self.buybox_seller_delivery = self.other_seller_delivery
        self.logger.info(f'Other Seller Delivery : {self.other_seller_delivery}')

    def add_seller_to_list(self):
        self.other_sellers_list.append(
            [str(self.seller_id), str(self.other_seller), str(self.other_seller_price), str(self.other_seller_delivery)])

    def check_repro_seller(self, seller_name):
        return 'Yes' if 'repro' in seller_name.lower() else 'No'

    def prepare_record(self):
        self.record = {
            'DATE': str(date.today()),
            'ISBN13': str(self.isbn),
            'Repro Listing': self.repro_listed,
            'Buybox': self.buybox_repro,
            'Buybox Seller': self.buybox_seller_name,
            "Buybox Price": self.buybox_seller_price,
            "Buybox Delivery Date": self.buybox_seller_delivery,
            "Other Seller Details": str(self.other_sellers_list)
        }

    def main(self):
        self.setup_flipkart_driver()
        self.open_flipkart_page()
        if self.get_search_result():
            self.set_pincode()
            self.get_buybox_seller()
            self.get_other_sellers_page()
            self.get_other_sellers_selector()


class FlipkartReader:
    def __init__(self):
        self.directory = folder_path.replace(' ', '\ ')
        # self.threads = int(threads)
        self.pincode = pincode
        self.output_directory = os.path.join(self.directory, 'flipkart_output')
        self.logger = set_logger('main')
        os.makedirs(self.output_directory, exist_ok=True)
        self.get_list_of_files()

    def get_list_of_files(self):
        for self.file_name in os.listdir(self.directory):
            if '.xlsx' in self.file_name or '.xls' in self.file_name:
                self.logger.info(f'File Name : {self.file_name}')
                self.full_file_name = os.path.join(self.directory, self.file_name)
                self.logger.info(f'Full File Name : {self.full_file_name}')
                self.output_file_name = os.path.join(self.output_directory, self.file_name)
                self.logger.info(f'Output File Name : {self.output_file_name}')
                self.get_isbn_list()
                self.find_total_isbn_count()
                self.execute_normal()

    def get_isbn_list(self):
        try:
            self.logger.info('Obtaining ISBN List')
            self.isbn_list = pd.read_excel(self.full_file_name)['ISBN13']
            self.logger.info('ISBN List Obtained')
        except Exception as e:
            self.logger.debug('ISBN13 Column Not Found')
            self.logger.error(f"{inspect.currentframe().f_code.co_name} : {e}")

    def find_total_isbn_count(self):
        self.total_isbn_count = len(self.isbn_list)

    def execute_thread(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for current_isbn_idx in range(len(self.isbn_list)):
                self.logger.info(f'ISBN : {self.isbn_list[current_isbn_idx]}')
                executor.submit(FlipkartScraper,current_isbn_idx + 1, self.total_isbn_count, self.full_file_name, self.output_file_name, self.pincode,
                self.isbn_list[current_isbn_idx])

    def execute_normal(self):
        for current_isbn_idx in range(len(self.isbn_list)):
            FlipkartScraper(id=current_isbn_idx + 1, total_rows=self.total_isbn_count,
                            input_file=self.full_file_name, output_file=self.output_file_name,
                            pincode=self.pincode, isbn=self.isbn_list[current_isbn_idx])


if __name__ == '__main__':
    app = InputForm()
    app.mainloop()
    LOGS_DIR = os.path.join(folder_path, 'logs')
    os.makedirs(LOGS_DIR, exist_ok=True)
    DAY_LOG_DIR = os.path.join(LOGS_DIR, datetime.datetime.now().strftime('%Y-%m-%d'))
    os.makedirs(DAY_LOG_DIR, exist_ok=True)
    FlipkartReader()
