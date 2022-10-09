from mysql.connector import Error
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import xlsxwriter
import re
from datetime import date
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.data = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'h1'):
            self.capture = True

    def handle_endtag(self, tag):
        if tag in ('p', 'h1'):
            self.capture = False

    def handle_data(self, data):
        self.data.append(data)


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



cursor.execute("SELECT link FROM product_data WHERE status=1")

products = cursor.fetchall()
row=0
rowCount = 0
allergendata=''
productCount=len(products)
dbrow = {1:'link', 2: 'status', 3: '', 4: '', 5:'', 6:'', 7:'', 8:'', 9:'', 10:'', 11:'', 12: '', 13:'', 14:''}
for product in products:
    print(product[0])
    link = product[0]
    try:
        rowCount = rowCount + 1
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(link)
        time.sleep(1)
        productName = driver.find_element(By.CLASS_NAME, 'pdpr-Title').text
        print('product Link:', link)
        print('product Name', productName)
        imageDiv = driver.find_element(By.CLASS_NAME, 'pdpr-ProductImage')
        productImage = imageDiv.find_element(By.TAG_NAME, 'img').get_attribute('src')
        #price = driver.find_element(By.CLASS_NAME, 'pdpr-Price__Price rs-qa-price')
        #print('PRICE: ', price)
        print("image src", productImage)
        productCategoriesTemporary = driver.find_elements(By.CLASS_NAME, 'lr-breadcrumbs__link')
        productCategories = []
        for c in productCategoriesTemporary:
            productCategories.append(c.get_attribute('innerHTML'))
        categoryData = ''
        col = 1
        categoryList = []
        for c in range(0, len(productCategories)):
            categoryString = re.sub('<.*?>', '', productCategories[c])
            categoryString = re.sub('&amp;', '&', categoryString)
            if c <= 5:
                #print('category string:', categoryString)
                categoryList.append(categoryString)
                #worksheet.write(row, col, categoryString)
                col = col + 1
            else:
                rowdata = ''
                for c in range(5, len(productCategories) + 1):
                    rowdata = rowdata + productCategories(c)
                    print('productCategories[c]',productCategories[c])
                    #worksheet.write(row, 5, productCategories[c])

            categoryData = categoryData + ' ; ' + categoryString
            #print('Category String: ', categoryString)
        print('prodyct categories', categoryList )
        productDesc = driver.find_element(By.CLASS_NAME, 'pdpr-ProductDescription')
        productDescription = productDesc.get_attribute('innerHTML')
        #print('product description: ', productDescription)
        productDescription = re.sub('<.*?>', ';', productDescription)
        productDescription = re.sub('&amp;', '&', productDescription)
        print('product description: ', productDescription)
        #productSorte = driver.find_element(By.CLASS_NAME, 'pdpr-SelectButton__placeholder').text
        #print("SORTE", productSorte)
        #print('product Categories: ', productCategories)
        productDetailElements = driver.find_elements(By.CLASS_NAME, 'pdpr-TabCordionItem__Content')
        productDetail = []
        productDetailTitle = []
        for detail in productDetailElements:
            productDetail.append(detail.get_attribute('innerHTML'))
        zutatenPartsElements = productDetailElements[0].find_elements(By.CLASS_NAME, 'pdpr-Attribute')
        zutatenParts = []
        for zutaten in zutatenPartsElements:
            zutatenParts.append(zutaten.get_attribute('innerHTML'))
        #print('zutatenPartsElements: ', zutatenParts)
        ztitles = []
        zdetails = []
        for like in zutatenParts:
            parser = MyHTMLParser()
            parser.feed(like)
            for d in parser.data:
                ztitles.append(parser.data[0])
                zdetails.append(parser.data[-1])
        #print('ztitles:', ztitles)
        #print('zdetails',zdetails)
        productDetailElements2 = driver.find_elements(By.CLASS_NAME, 'pdpr-TabCordionItem__Title')
        for detailTitle in productDetailElements2:
            productDetailTitle.append(detailTitle.get_attribute('innerHTML'))
        #print('product detail list', len(productDetail), productDetail)
        #print('product detail title list', len(productDetailTitle), productDetailTitle)
        print('prname', productName)
        # worksheet.write(row, 6, productName)
        print('link', link)
        # worksheet.write(row, 7, link)
        print('prudctImage', productImage)
        # worksheet.write(row, 8, productImage)
        print('desc', productDescription)
        # #worksheet.write(row, 9, productSorte)
        # worksheet.write(row, 10, productDescription)
        #write zutaten and Allergenhinweise descs
        print('zdetails0', zdetails[0])
        print('zdetails1', zdetails[1])
        # worksheet.write(row, 11, zdetails[0])
        # worksheet.write(row, 12, zdetails[1])


        col = 11
        extraFieldIds = []
        for i in range(len(productDetailTitle)):
            detail = re.sub('&amp;', '&', productDetail[i])
            #detail = re.sub('<.*?>', ';', detail)
            # print('LOOK AT RAW VERSION OF DETAIL DATA before parsing from html:', detail)
            # parser = MyHTMLParser()
            # parser.feed(detail)
            # print(parser.data)
            # detail = ";".join([str(i) for i in parser.data])
            # print('LOOK AT RAW VERSION OF DETAIL DATA after parsing from html:', detail)
            productDetailTitle[i] = re.sub('<.*?>', '', productDetailTitle[i])
            productDetailTitle[i] = re.sub('&amp;', '&', productDetailTitle[i])
            # data = productDetailTitle[i] + ' -> ' + detail
            if 'Zutaten' in productDetailTitle[i]:
                count = detail.count('<div ')
                parser = MyHTMLParser()
                parser.feed(detail)
                #print("parser.data: ", parser.data)
                parsedData = parser.data
                #print("len of parsed data", len(parsedData))
                for dataindex in range(len(parsedData)):
                    #print(dataindex)
                    if len(parsedData[dataindex]) <= 3:
                        parsedData[dataindex] = ''
                #print('after clarification of list parsed data:', parsedData)
                while True:
                    try:
                        parsedData.remove('')
                    except:
                        break
                #print('after remove empty elements from list parsed data:', parsedData)
                for dataindex in range(len(parsedData)):
                    if 'Zutaten' in parsedData[dataindex]:
                        data = parsedData[dataindex + 1]
                        print('data11', data)
                        zutatendata = data
                        #worksheet.write(row, 11, data)
                        #print('Zutaten index', parsedData[dataindex])
                        #print('Zutaten detail', parsedData[dataindex + 1])
                    elif 'Allergenhinweise' in parsedData[dataindex]:
                        data = parsedData[dataindex + 1]
                        #print('alerg index', parsedData[dataindex])
                        #print('alerg detail', parsedData[dataindex + 1])
                        allergendata = data
                        print('data12', data)
                        #worksheet.write(row, 12, data)

                data = ";".join([str(i) for i in parser.data])
            elif 'Nährwerte' in productDetailTitle[i]:
                #print('LOOK AT RAW VERSION OF DETAIL DATA before parsing from html:', detail)
                parser = MyHTMLParser()
                parser.feed(detail)
                #print(parser.data)
                detail = ";".join([str(i) for i in parser.data])
                #print('LOOK AT RAW VERSION OF DETAIL DATA after parsing from html:', detail)
                data = ";".join([str(i) for i in parser.data])
                detail2 = data
                print('data13 nahrwerte', data)
                #worksheet.write(row, 13, data)
            elif 'Artikeldetails' in productDetailTitle[i]:
                #print('LOOK AT RAW VERSION OF DETAIL DATA before parsing from html:', detail)
                parser = MyHTMLParser()
                parser.feed(detail)
                #print(parser.data)
                detail = ";".join([str(i) for i in parser.data])
                #print('LOOK AT RAW VERSION OF DETAIL DATA after parsing from html:', detail)
                data = ";".join([str(i) for i in parser.data])
                detail3 = data
                print('data14', data)
                #worksheet.write(row, 14, data)
            elif 'Kontakt' in productDetailTitle[i]:
                #print('LOOK AT RAW VERSION OF DETAIL DATA before parsing from html:', detail)
                parser = MyHTMLParser()
                parser.feed(detail)
                #print(parser.data)
                detail = ";".join([str(i) for i in parser.data])
                #print('LOOK AT RAW VERSION OF DETAIL DATA after parsing from html:', detail)
                data = ";".join([str(i) for i in parser.data])
                detail4 = data
                print('data15 kontakt', data)
                #worksheet.write(row, 15, data)
            elif 'Hinweise' in productDetailTitle[i]:
                #print('LOOK AT RAW VERSION OF DETAIL DATA before parsing from html:', detail)
                parser = MyHTMLParser()
                parser.feed(detail)
                #print(parser.data)
                detail = ";".join([str(i) for i in parser.data])
                #print('LOOK AT RAW VERSION OF DETAIL DATA after parsing from html:', detail)
                data = ";".join([str(i) for i in parser.data])
                detail5 = data
                print('data16 hinweise', data)
                #worksheet.write(row, 16, data)
                #print('col 13 done')
            else:
                extraFieldIds.append(i)
        #print('extra fields ID: ', extraFieldIds)
        col = 17
        for j in extraFieldIds:
            detail = re.sub('<.*?>', ';', productDetail[j])
            detail = re.sub('&amp;', '&', detail)
            productDetailTitle[j] = re.sub('<.*?>', ';', productDetailTitle[j])
            productDetailTitle[j] = re.sub('&amp;', '&', productDetailTitle[j])
            data = productDetailTitle[j] + ' : ' + detail
            print('data', data)
            # worksheet.write(row, col, data)
            col = col + 1
        row = row + 1
        productCount = productCount - 1
        print('Total product count is: ', len(products), 'Remaining product count: ', productCount)
        driver.close()
        category1=''
        category2=''
        category3=''
        category4=''
        category5=''
        if len(categoryList)>=1: category1 = categoryList[0]
        if len(categoryList)>=2: category2 = categoryList[1]
        if len(categoryList)>=3: category3 = categoryList[2]
        if len(categoryList)>=4: category4 = categoryList[3]
        if len(categoryList)>=5: category5 = categoryList[4]

        try:
            # query = """INSERT INTO products (link, status)
            #                            VALUES
            #                            ("""+links + """, 1) """
            cursor = connection.cursor()
            sql = "UPDATE product_data SET status = %s, category1=%s, category2=%s, category3=%s, category4=%s,category5=%s,productName=%s, imgSource=%s, produktbeschreibung=%s, zutaten = %s, allergenhinweise=%s, detail2=%s, detail3=%s, detail4=%s, detail5=%s   WHERE link = %s"
            val = (str(2), str(category1), str(category2), str(category3), str(category4), str(category5), str(productName), str(productImage), str(productDescription), str(zutatendata), str(allergendata), str(detail2),str(detail3), str(detail4), str(detail5), str(link))
            print(2)
            cursor.execute(sql,val)
            print(3)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into product table")
        except mysql.connector.Error as error:
            print("Failed to insert record into product table {}".format(error))



    except Exception as e:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('problem:', e)
        continue
    end = time.time()
    #worksheet.write(1, 1, 'Script execution duration(min): ')
    # worksheet.write(1, 2, str((end-start)/60))
    # worksheet.write(2, 1, 'Crawled category link: ')
    # worksheet.write(2, 2, category)
    # worksheet.write(3, 1, 'Total product count: ')
    # worksheet.write(3, 2, len(productItemLinks))
    # workbook.close()
