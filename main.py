import json
import unittest
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import re

index = 2

file = open('info.json')
settings = json.load(file)
conf = settings['settings'][index]


class TableTest(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        self.driver = webdriver.Edge()

    def test_1(self):
        driver = self.driver
        driver.get(conf['url'])
        driver.implicitly_wait(6)
        # driver.maximize_window()

        row_count = len(driver.find_elements(By.XPATH, conf['xpath'] + 'tbody/*'))
        # headers = driver.find_elements(By.XPATH, conf['xpath'] + 'tbody/tr[1]/*')
        table_not_str = False
        try:
            head = driver.find_element(By.XPATH, conf['xpath'] + 'thead')
            headers = head.find_elements(By.XPATH, 'tr/*')
        except:
            table_not_str = True
            headers = driver.find_elements(By.XPATH, conf['xpath'] + 'tbody/tr[1]/*')
        column_count = len(headers)
        print(row_count, column_count)
        grid = []
        typeMap = {}
        while (True):
            for x in range(row_count):
                if table_not_str and x == 0:
                    continue
                entry = {}
                for y in range(column_count):
                    value = driver.find_element(By.XPATH, self.getXPath(x + 1, y + 1)).text.replace('\n', ' ')
                    print(value)
                    typedValue = self.tryFloat(str(value))
                    typeMap[headers[y].text] = type(typedValue)
                    entry[headers[y].text] = self.tryFloat(str(value))
                grid.append(entry)
            if (conf['hasPaginator'] == True):
                next_btn = driver.find_element(By.XPATH, conf['xpathPaginator'])
                if next_btn.is_enabled():
                    next_btn.click()
                    driver.implicitly_wait(3)
                else:
                    break
            else:
                break

        frame = pd.DataFrame(grid)
        print(frame)
        file_name = re.sub(r'[^a-zA-Z\d]', '', driver.title)
        frame.to_csv(file_name + '.csv', index=False)
        print(frame.dtypes)
        for key in typeMap:
            frame[key].astype(typeMap[key])
        # print(frame.dtypes)
        if conf['xColumn'] != None:
            frame.plot.bar(x=conf['xColumn'])
        else:
            frame.plot.bar()
        plt.savefig(file_name + '.png')
        plt.show()

    def getXPath(self, row, column):
        return conf['xpath'] + 'tbody/tr[' + str(row) + ']/*[' + str(column) + ']'

    def tryFloat(self, value: str) -> float | str:
        try:
            return float(value)
        except:
            return str(value)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
