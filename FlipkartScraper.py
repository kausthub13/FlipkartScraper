from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from tkinter import *
import time
from datetime import date
import mmap
from random import randint
import csv
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import tkinter.font as font
import os
import ntpath

error_occurred = False
filename = None
row_count = 0
total_lines = 0
flipkart_val = 0
amazon_val = 0
directory = None
output_file = None

def UploadAction(event=None):
    global directory
    directory = filedialog.askdirectory()


def mapcount(filename):
    f = open(filename, "r+", encoding='utf8')
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines


def read_csv(file):
    isbn_list = []
    with open(file, encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                pass
            else:
                isbn_list.append(row[1])
            line_count += 1
    return isbn_list


def next_isbn(filename):
    # with open(filename, 'r', encoding='utf8') as input_file:
    #     for current_row in csv.reader(input_file):
    #         yield current_row[1]
    csv_file = pd.read_csv(filename)
    isbn_list = csv_file['ISBN13']
    for i in range(len(isbn_list)):
        yield str(isbn_list.iloc[i])


def setup_flipkart_driver():
    options = Options()
    options.headless = False
    # options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_driver_path = r"chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
    # driver.minimize_window()
    return driver


def setup_flipkart_header(filename):
    global output_file
    base_name = ntpath.basename(filename)[:-4] + '_flipkart_output.csv'
    base_file_path = os.path.join(output_file, base_name)
    writing_file = open(base_file_path, 'a', encoding="utf-8", newline='')
    amazon_flip_writer = csv.writer(writing_file, delimiter=',')
    amazon_flip_writer.writerow(
        ["Date", "ISBN13", "Flipkart Listing","Buybox","Buybox Seller","Buybox Price","Buybox Delivery Date","Other Seller","Other Seller Price", "Other Seller Delivery Date"])
    writing_file.close()


def flipkart_scraper(filename):
    global row_count
    global total_lines
    global output_file
    isbn_generator = next_isbn(filename)
    # next(isbn_generator)
    setup_flipkart_header(filename)
    driver = setup_flipkart_driver()
    base_file_path = ""
    line_count = 0
    for current_isbn in isbn_generator:
        line_count += 1
        found = False
        listed = "Not Listed"
        buybox = "No"
        buybox_seller = "NA"
        buybox_seller_price = "NA"
        buybox_seller_delivery = "NA"
        other_seller = "NA"
        other_seller_price = "NA"
        other_seller_delivery = "NA"

        # price = "NA"
        # curr_binding = "NA"
        # curr_pages = "NA"
        # curr_per_page_ratio = "NA"
        try:
            flipkart_link = "https://www.flipkart.com/books/pr?sid=bks&q="
            if not current_isbn.isdigit():
                flipkart_link = 'https://www.flipkart.com/vivo-s1-pro-jazzy-blue-128-gb/p/itm60bf6c78dfe9a?pid='
                driver.get(flipkart_link+str(current_isbn))
            else:
                driver.get(flipkart_link + str(current_isbn))
                search_result = driver.find_element_by_class_name('s1Q9rs')
                search_result_link = search_result.get_attribute("href")
                driver.get(search_result_link)
            # seller_name = driver.find_element_by_id("sellerName")
            if line_count == 1:
                pincode = driver.find_element_by_class_name('_36yFo0')
                pincode.send_keys('400013')
                pincode_check = driver.find_element_by_class_name('_2P_LDn')
                pincode_check.click()
                time.sleep(5)
            # highlights = driver.find_elements_by_class_name('_2-riNZ')
            # for highlight in highlights:
            #     curr_highlight = str(highlight.text)
            #     if 'Binding' in highlight.text:
            #         curr_binding = curr_highlight.replace('Binding:','').strip()
            #     if 'Pages' in highlight.text:
            #         curr_pages = curr_highlight.replace('Pages:','').strip()
            seller_name = driver.find_element_by_id("sellerName")
            buybox = "Yes"
            buybox_seller = seller_name.find_element_by_tag_name('span').find_element_by_tag_name('span').text
            buybox_seller_price = str(driver.find_element_by_css_selector("div[class='_30jeq3 _16Jk6d']").text).replace(
                '₹', '').strip()
            buybox_seller_delivery = str(driver.find_element_by_css_selector("div[class='_3XINqE']").text).replace("Delivery by",'')
            if 'repro' in str(seller_name.text).lower():
                found = True

                # price = driver.find_element_by_css_selector("div[class='_1vC4OE _3qQ9m1']").text
                # price = str(price).replace('₹','').strip()
                # try:
                #     curr_per_page_ratio = round(float(price) / float(curr_pages),2)
                # except:
                #     pass
                more_sellers = None
                try:
                    more_sellers = driver.find_element_by_class_name('_38I6QT')
                except:
                    pass
                if more_sellers:
                    a_tag = more_sellers.find_element_by_tag_name('a')
                    href_link = a_tag.get_attribute("href")
                    driver.get(href_link)
                    time.sleep(2)
                    sellers = driver.find_elements_by_css_selector("div[class='_2Y3EWJ']")
                    seller_id = -1
                    if sellers:
                        for seller in sellers:
                            seller_id += 1
                            if seller_id == 1:
                                other_seller = seller.find_element_by_css_selector("div[class='_3enH42']").text
                                other_seller_price = str(seller.find_element_by_css_selector("div[class='_30jeq3']").text).replace('₹','').strip()
                                other_seller_delivery = str(seller.find_element_by_css_selector("div[class='_3XINqE']").text).replace("Delivery by",'')
                                break
            else:
                more_sellers = None
                try:
                    more_sellers = driver.find_element_by_class_name('_38I6QT')
                except:
                    pass
                if more_sellers:
                    a_tag = more_sellers.find_element_by_tag_name('a')
                    href_link = a_tag.get_attribute("href")
                    driver.get(href_link)
                    time.sleep(2)
                    sellers = driver.find_elements_by_css_selector("div[class='_2Y3EWJ']")
                    seller_id = -1
                    if sellers:
                        for seller in sellers:
                            seller_id += 1
                            if 'repro' in str(seller.text).lower():
                                time.sleep(2)
                                found = True
                                other_seller = seller.find_element_by_css_selector("div[class='_3enH42']").text
                                other_seller_price = str(seller.find_element_by_css_selector("div[class='_30jeq3']").text).replace('₹','').strip()
                                other_seller_delivery = str(seller.find_element_by_css_selector(
                                    "div[class='_3XINqE']").text).replace("Delivery by",'')
                                break
                        # if found:
                        #     prices = driver.find_elements_by_css_selector("div[class='_1vC4OE']")
                        #     prices_id = -1
                        #     for price_tag in prices:
                        #         prices_id += 1
                        #         if prices_id == seller_id:
                        #             price = price_tag.text
                        #             break
                        #     price = str(price).replace('₹','').strip()
                        #     try:
                        #         curr_per_page_ratio = round(float(price) / float(curr_pages),2)
                        #     except:
                        #         pass
            if found:
                listed = "Listed"
        except NoSuchElementException:
            pass
        except Exception as e:
            with open(ntpath.basename(filename)[:-4] + "flip_error_log.csv", 'a', newline='') as error_file:
                error_writer = csv.writer(error_file)
                error_writer.writerow(['Flipkart', current_isbn])
        print(str(line_count) + "/" + str(total_lines), "Flipkart", current_isbn, listed,buybox,buybox_seller,buybox_seller_price,buybox_seller_delivery,other_seller,other_seller_price,other_seller_delivery)
        base_name = ntpath.basename(filename)[:-4] + '_flipkart_output.csv'
        base_file_path = os.path.join(output_file, base_name)
        writing_file = open(base_file_path, 'a', encoding="utf-8", newline='')
        amazon_flip_writer = csv.writer(writing_file, delimiter=',')
        amazon_flip_writer.writerow([date.today(), current_isbn,listed,buybox,buybox_seller,buybox_seller_price,buybox_seller_delivery,other_seller,other_seller_price,other_seller_delivery])
        writing_file.close()
    driver.close()
    driver.quit()
    return base_file_path

def setup_ui():
    global row_count
    global output_file
    global total_lines
    global flipkart_val
    global amazon_val
    root = tk.Tk()
    root.geometry("600x200")
    root.title("Select Your Folder To Find Details in Flipkart")
    select = tk.Label(root)
    select.pack()
    myFont = font.Font(size=20)
    button = tk.Button(root, bg='yellow', text='Select Folder', command=UploadAction, font=myFont)
    button.configure(width=600, height=2)
    button.pack()
    label = tk.Label(root)
    label.pack()

    def task():
        if directory:
            select.config(text="You have successfully selected the folder you can now close this window")
            label.config(text="Current Selected Folder Path: " + str(directory))
        root.after(1000, task)

    root.after(0, task)
    root.mainloop()
    if directory:
        output_file = os.path.join(directory, 'Output')
        try:
            os.mkdir(output_file)
        except FileExistsError:
            pass
        for name in os.listdir(directory):
            if name[-5:] == '.xlsx' or name[-4:] == '.xls':
                global total_records

                filename = os.path.join(directory, name)
                excel_reader = pd.read_excel(filename)
                filename = os.path.join(directory, name[:-5] + '.csv')
                excel_reader.to_csv(filename, index=None, header=True)
                total_lines = mapcount(filename) - 1
                print("Processing the file now")
                file_path = flipkart_scraper(filename)
                read_file = pd.read_csv(file_path)
                if os.path.exists(file_path[:-4] + '.xlsx'):
                    existing_file = pd.read_excel(file_path[:-4] + ".xlsx")
                    read_file = pd.concat([existing_file, read_file], ignore_index=True)
                    with pd.ExcelWriter(file_path[:-4] + '.xlsx', mode='w') as writer:
                        read_file.to_excel(writer, sheet_name='Sheet1', index=None, header=True)
                else:
                    with pd.ExcelWriter(file_path[:-4] + '.xlsx', mode='w') as writer:
                        read_file.to_excel(writer, sheet_name='Sheet1', index=None, header=True)
                os.remove(file_path)
                os.remove(filename)
                print("All Files Processed")
        for name in os.listdir(os.path.dirname(sys.argv[0])):
            if name[-4:] == '.csv':
                convert_to_excel = pd.read_csv(name)
                with pd.ExcelWriter(name[:-4] + '.xlsx', mode='w') as writer:
                    convert_to_excel.to_excel(writer, sheet_name='Sheet1', index=None, header=True)




setup_ui()