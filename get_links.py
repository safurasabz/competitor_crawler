import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By

# cat1 = 'https://shop.rewe.de/c/frische-kuehlung-joghurt-pudding-milchsnacks/'
# cat2 = 'https://shop.rewe.de/c/frische-kuehlung-molkereiprodukte-alternativen/'
# cat3 = 'https://shop.rewe.de/c/frische-kuehlung-milch-milchersatz/'
cat4 = 'https://shop.rewe.de/c/getraenke-soft-drinks/'
cat5 = 'https://shop.rewe.de/c/getraenke-wasser/'
cat6 = 'https://shop.rewe.de/c/frische-kuehlung/'
categories = [cat4, cat5, cat6]


try:
    connection = mysql.connector.connect(host='localhost',
                                         database='crawler',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
except Error as e:
    print("Error while connecting to MySQL", e)


for category in categories:
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(category)
    time.sleep(3)
    # cookieAcceptButton = driver.find_element(By.ID, 'uc-btn-accept-banner')
    # cookieAcceptButton.click()
    # print('Cookie Accept button ', cookieAcceptButton, ' clicked')
    # time.sleep(5)
    # #
    # lieferservice = driver.find_element(By.CLASS_NAME, 'gbmc-qa-delivery-intention')
    # lieferservice.click()
    # print('lieferservice is clicked: ', lieferservice)
    # time.sleep(10)
    # #
    # postalinput = driver.find_element(By.CLASS_NAME, 'gbmc-zipcode-input')
    # postalinput.send_keys('80')
    # print('Postal input ', postalinput, ' located')
    # time.sleep(1)
    # postalinput.send_keys('3')
    # time.sleep(1)
    # postalinput.send_keys('3')
    # time.sleep(1)
    # postalinput.send_keys('5')
    productItemLinks = []
    productLinks = driver.find_elements(By.CLASS_NAME, 'search-service-productDetailsLink')
    for link in productLinks:
        productItemLinks.append(link.get_attribute('href'))

    # find pagination element and extract last page number
    paginationContainer = driver.find_element(By.CLASS_NAME, 'Pagination_paginationPagesContainer__b2Lv_')
    paginationNumElements = paginationContainer.find_elements(By.CLASS_NAME,
                                                              'PaginationPagesList_paginationPage__yuWIE')
    paginationNumElements2 = paginationContainer.find_elements(By.CLASS_NAME,
                                                               'PostRequestGetForm_PostRequestGetFormButton__9Sp2R')
    paginationNumbers = []
    paginationNumbers2 = []
    for element in paginationNumElements:
        paginationNumbers.append(element.get_attribute('innerHTML'))
    for element in paginationNumElements2:
        paginationNumbers2.append(element.get_attribute('innerHTML'))
    print('paginationNumbers: ', paginationNumbers)
    print('paginationNumbers2: ', paginationNumbers2)
    pageNum = 1
    p = int(paginationNumbers[-1])
    while pageNum != p:
        try:
            pageNum = pageNum + 1
            print('Category Name: ', category, 'pageNumber: ', pageNum)
            link = category + '?page=' + str(pageNum)
            print('link: ', link)
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument("start-maximized")
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(link)
            time.sleep(1)
            productLinks = driver.find_elements(By.CLASS_NAME, 'search-service-productDetailsLink')
            for link in productLinks:
                productItemLinks.append(link.get_attribute('href'))
            print('productlinks: ', productItemLinks, len(productItemLinks))


        except:
            print(pageNum, ' is not available')
            break

    for links in productItemLinks:
        try:
            # query = """INSERT INTO products (link, status)
            #                            VALUES
            #                            ("""+links + """, 1) """
            cursor = connection.cursor()
            print(1)
            status = 1
            print(2)
            print(links, status)

            cursor.execute("INSERT INTO product_data (link, status) VALUES (%s , %s) ", (str(links), str(status)))
            print(3)
            connection.commit()

            print(cursor.rowcount, "Record inserted successfully into product table")

        except mysql.connector.Error as error:
            print("Failed to insert record into product table {}".format(error))


    print('product count: ', len(productItemLinks))
    print("Product LINKS", productItemLinks)
cursor.close()

