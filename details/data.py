from selenium import webdriver
from details.constant import BASE_URLS, URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import os
import time
import pandas as pd


class Details(webdriver.Chrome):
    def __init__(self, driver_path="C:\Seleniumdrivers"):
        self.driver_path = driver_path
        os.environ["PATH"] = driver_path
        super(Details, self).__init__()
        self.maximize_window()
        self.implicitly_wait(15)

    def get_student_details(self):
        #  getting student details - email and phone number
        reg_nos = self.get_reg_no()
        data = self.get_full_details(reg_nos)

        return data

    def get_reg_no(self):
        """
        Get all registration number of student
        """
        students_regno = []

        for url in BASE_URLS:
            self.get(url)
            page_heading = self.find_element(By.CLASS_NAME, "contentheading")

            # excluding newly admitted student
            if "2023" in str(page_heading.text):
                print("Cannot Scrape Newly admitted student details :(")
                continue

            elements = self.find_element(By.TAG_NAME, "tbody")

            elements = elements.find_elements(
                By.XPATH, "//tr[td/@align='right']")

            # get reg number for individual student
            for student_info in elements:
                reg_no = student_info.text.split(" ")[1]
                students_regno.append(reg_no)

        return students_regno

    def add_data_to_list(self):

        student_full_details = []
        try:
            email_element = WebDriverWait(self, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email = email_element.get_attribute("value")

            phone_number_element = WebDriverWait(self, 20).until(
                EC.presence_of_element_located((By.ID, "phone"))
            )
            phone_number = phone_number_element.get_attribute("value")

            student_data = {"email": email, "phone number": phone_number}

            student_full_details.append(student_data)
        except (StaleElementReferenceException, TimeoutException):
            print("Element not available")
        return student_full_details

    def get_full_details(self, students_regno):
        self.find_element(By.TAG_NAME, "body").send_keys(Keys.COMMAND + "t")

        self.get(URL)

        for student_details in students_regno:
            # getting individual reg number
            elem = self.find_element(By.XPATH, "//input[@id='RegNo']")

            elem.send_keys(student_details)

            submit_btn = WebDriverWait(self, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@name='submit']"))
            )
            submit_btn.click()
            time.sleep(5)

            student_full_details = self.add_data_to_list()
            elem.clear()
            break

        return student_full_details

    def to_csv(self, data):
        df = pd.DataFrame(data)
        df.to_csv('studentinfo.csv')
