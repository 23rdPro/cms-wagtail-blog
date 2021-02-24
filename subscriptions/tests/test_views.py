import time
import unittest
from django.test import TestCase
from selenium import webdriver


class SubscriptionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Chrome()

    def test_submit_email(self):
        self.driver.get("http://localhost:8000")
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="id_email"]').send_keys('admintest@mail.kom')
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="id_email"]').submit()
        time.sleep(1)
        self.assertEqual("http://localhost:8000/subscribe/", self.driver.current_url)

    def tearDown(self) -> None:
        self.driver.quit()


if __name__ == '__main__':
    unittest.main(warnings='ignore')
