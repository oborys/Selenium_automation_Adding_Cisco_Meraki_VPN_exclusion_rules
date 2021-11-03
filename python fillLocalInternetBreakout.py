from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
import configparser

# read variables from config
credential = configparser.ConfigParser()
credential.read('cred')

url_sd_wan_and_traffic_rules = credential['Meraki']['url_sd_wan_and_traffic_rules']
Org_Name = credential['Meraki']['Org_Names']
dashboardPass = credential['Meraki']['dashboardPass']
email = credential['Meraki']['email']

driver = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver')
driver.set_window_size(1920,1080)

driver.get('https://n210.meraki.com/login/dashboard_login')
username = driver.find_element_by_id("email")
username.send_keys(email)
driver.find_element_by_id("next-btn").click()


password = driver.find_element_by_id("password")
password.send_keys(dashboardPass)
driver.find_element_by_id("login-btn").click()

# wait the ready state to be complete
WebDriverWait(driver=driver, timeout=10).until(
    lambda x: x.execute_script("return document.readyState === 'complete'")
)
error_message = "Incorrect username or password."
# get the errors (if there are)
errors = driver.find_elements_by_class_name("flash-error")

if any(error_message in e.text for e in errors):
    print("[!] Login failed")
else:
    print("[+] Login successful")

link = driver.find_element_by_link_text(Org_Name)
link.click()


with open("IPandPorts.txt", 'r') as f:
    ipListAndPort = f.read().split('\n')
# Wait 5 sec
driver.get(url_sd_wan_and_traffic_rules)


for ipPort in ipListAndPort:

    lst = ipPort.split(';')
    IP = lst[0]
    ports = lst[2].split(',')
    for port in ports:
        print("IP ", IP, " Ports ", port)

        time.sleep(3)
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@data-toggle='dropdown']")))
        button.click()

        time.sleep(3)
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='vpn_exclusion_protocol_chosen']")))
        button.click()

        button=WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='TCP']")))
        button.click()
        time.sleep(3)


        driver.find_element_by_xpath("//a[@class='chosen-single']").click()
        print("Here click TCP")

        wait=WebDriverWait(driver,3)

        # Choose TCP or UDP
        # 0 - TCP, 1 - UDP, 2 - ICMP, 3 - DNS, 4 - Any
        if lst[1] == 'tcp':
            button=WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, "//li[text()='TCP']")))
            button.click()
        elif lst[1] == 'udp':
            button=WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, "//li[text()='UDP']")))
            button.click()
 

        print("TCP clicked")

        time.sleep(4)

        # Try to catch "could not be scrolled into view"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Enter a CIDR/hostname'))).click()

        time.sleep(2)
        inputElement = driver.find_element_by_xpath("//input[@placeholder='192.168.0.0/24']")
        inputElement.send_keys(IP)

        time.sleep(3)
        # Click button Add
        #driver.find_element_by_xpath('//button[text()="Add"]').click()
        button=WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Add']")))
        button.click()


        time.sleep(2)
        # Dst port field input class="dst_port"
        inputElement = driver.find_element_by_xpath("//input[@class='dst_port']")
        inputElement.clear()
        inputElement.send_keys(port)

        time.sleep(2)

        element = driver.find_element_by_xpath("//button[contains(@type, 'button') and contains(., 'expression')]")
        driver.execute_script("arguments[0].click();", element)
    
        # Click "Save Changes" button
        inputElement = driver.find_element_by_xpath("//input[@value='Save Changes']")
        inputElement.click()
    
        time.sleep(2)
        driver.refresh()

