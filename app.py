from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# Function to scrape Amazon
def get_amazon_price(product_name):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # comment out to see browser
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
        driver.get(url)
        
        # Wait until product appears
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal"))
        )
        
        product_elem = driver.find_element(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal")
        price_elem = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole")
        
        result = {
            "site": "Amazon",
            "name": product_elem.text.strip(),
            "price": f"₹{price_elem.text.strip()}"
        }
        driver.quit()
        return result
    except Exception as e:
        print("Amazon Error:", e)
        driver.quit()
        return None

# Function to scrape Flipkart
def get_flipkart_price(product_name):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # comment out to see browser
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}"
        driver.get(url)
        time.sleep(2)  # wait for popup
        
        # Close login popup if exists
        try:
            close_btn = driver.find_element(By.CSS_SELECTOR, "button._2KpZ6l._2doB4z")
            close_btn.click()
            time.sleep(1)
        except:
            pass
        
        # Wait for product
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._2kHMtA div._4rR01T"))
        )
        
        product_elem = driver.find_element(By.CSS_SELECTOR, "div._2kHMtA div._4rR01T")
        price_elem = driver.find_element(By.CSS_SELECTOR, "div._2kHMtA div._30jeq3")
        
        result = {
            "site": "Flipkart",
            "name": product_elem.text.strip(),
            "price": price_elem.text.strip()
        }
        driver.quit()
        return result
    except Exception as e:
        print("Flipkart Error:", e)
        driver.quit()
        return None

# Flask route
@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    if request.method == "POST":
        product_name = request.form.get("product")
        amazon_result = get_amazon_price(product_name)
        flipkart_result = get_flipkart_price(product_name)

        if amazon_result:
            results.append(amazon_result)
        if flipkart_result:
            results.append(flipkart_result)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
