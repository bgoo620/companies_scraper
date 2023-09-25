from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def login(browser):
    userbox = browser.find_element(By.ID,"user")
    userbox.send_keys("") #ENTER YOUR USERNAME HERE
    passwordbox = browser.find_element(By.NAME,"password")
    passwordbox.send_keys("") #ENTER YOUR PASSWORD HERE
    passwordbox.send_keys(Keys.RETURN)

def searchAddressProperty(searchItem, browser):
    searchbox = browser.find_element(By.TAG_NAME,"input")
    searchbox.send_keys(searchItem)
    time.sleep(1)
    searchbox.send_keys(Keys.ENTER)

def getPageTable(browser, address):
    pageTable = ""
    rows=1+len(browser.find_elements(By.XPATH,"/html/body/div[6]/div[2]/div[1]/div[5]/div[1]/div[4]/div[1]/table/tbody/tr"))
    cols=len(browser.find_elements(By.XPATH,"/html/body/div[6]/div[2]/div[1]/div[5]/div[1]/div[4]/div[1]/table/tbody/tr[1]/td"))
    for r in range(1, rows):
        for p in range(1, cols):
            value = browser.find_element(By.XPATH, "html/body/div[6]/div[2]/div[1]/div[5]/div[1]/div[4]/div[1]/table/tbody/tr["+str(r)+"]/td["+str(p)+"]")
            if p == 2:
                pageTable += str(value.get_attribute("uncopyable-content")).replace("‑","_").replace(",","")+","
                elements = str(value.get_attribute("uncopyable-content")).split(",")
                for i in elements:
                    if "limited" in i.lower():
                        driver = searchCompanyStakeholders(i,browser.find_element(By.XPATH, "html/body/div[6]/div[2]/div[1]/div[5]/div[1]/div[4]/div[1]/table/tbody/tr["+str(r)+"]/td["+str(p-1)+"]").text, address)
                    else:
                        None
            else:
                pageTable+= str(value.text).replace("‑","_").replace(",","") +','
        pageTable+="\n"
    return(pageTable)


def scrapeTable(browser, address):
    tableText = "address, owners, suburb, town, ta_name, property_type, sale_date, RV, sale, bedrooms_min, land_area, floor_area, built, advertised_date,\n"
    while findNextButton(browser):
        tableText += getPageTable(browser, address)
        nxtbtn = browser.find_element(By.XPATH,"//a[@title='Next page']")
        nxtbtn.click()
        time.sleep(1)
    tableText+=getPageTable(browser, address)
    return(tableText)


def findNextButton(browser):
    nxtbtn = browser.find_element(By.XPATH,"//a[@title='Next page']")
    return(nxtbtn.value_of_css_property("visibility") == "visible")

#########################
### stakeholder stuff ###
#########################

def searchCompanyStakeholders(company, address, searchedLocation):
    driver = webdriver.Chrome(executable_path ="C:\Program Files (x86)\Google\Chrome\chromedriver.exe")
    driver.get("https://companies-register.companiesoffice.govt.nz/")
    searchBox = driver.find_element(By.XPATH,"//input[@id='search_input_text']")
    searchBox.send_keys(company)
    searchBox.send_keys(Keys.ENTER)
    firstCompany = driver.find_element(By.CLASS_NAME, "entityName")
    firstCompany.click()
    shareHoldings = driver.find_element(By.ID, "shareholdingsTab") 
    shareHoldings.click()
    writeStakeholderToFile(driver, company, address, searchedLocation)

def writeStakeholderToFile(driver, company, address, searchedlocation):
    companyFiles = open(searchedlocation+" companies.csv","a",encoding="utf-8")
    numberofallocations = 1+len(driver.find_elements(By.XPATH,"//div[@class='allocationDetail']"))
    text = ""
    for number in range(1,numberofallocations):
        rows=1+len(driver.find_elements(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row']"))
        share = driver.find_element(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row'][1]//span[@class='shareLabel']")
        r = 2
        check = 0
        while r < rows:
            if r%2==check:
                text+=(address+", ")
                text+=(company+", ")
                text+=(share.text+", ")
                text+=(driver.find_element(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row']["+str(r)+"]").text.replace(",","/")+",")
            else:
                text+=(driver.find_element(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row']["+str(r)+"]").text.replace(",","/")+",")
                try:
                    if driver.find_element(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row']["+str(r+1)+"]").text != " Director: Yes":
                        text+= "Director: No,\n"
                    else:
                        text+=driver.find_element(By.XPATH,"//div[@class='allocationDetail']["+str(number)+"]//div[@class='row']["+str(r+1)+"]").text+"\n"
                        r+=1
                        if check == 0:
                            check = 1
                        else:
                            check = 0
                except:
                    text+= "Director: No,\n"
            r+=1
    print(text)
    companyFiles.write(text)
    companyFiles.close()

def main():
    search = input("Please input the area you would like to search: ")
    time.sleep(3)
    browser = webdriver.Chrome(executable_path ="C:\Program Files (x86)\Google\Chrome\chromedriver.exe")
    browser.get("http://www.property-guru.co.nz/gurux/render.php?action=main")
    companyFiles = open(search+" companies.csv","w",encoding="utf-8")
    companyFiles.write("Address, company, share, name, address, director,\n")
    companyFiles.close()
    login(browser)
    time.sleep(1)
    searchAddressProperty(search, browser)
    time.sleep(1)
    file = open(search+".csv","w",encoding="utf-8")
    data = scrapeTable(browser, search)
    file.write(data)
    file.close()
    print("All done open the file saved in the same directory as the file.")
main()