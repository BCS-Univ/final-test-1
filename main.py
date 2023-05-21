import requests     # 載入 requests 套件，讓 Python 可以使用 HTTP 協定發送網路請求
from bs4 import BeautifulSoup       # 載入 BeautifulSoup 套件，讓 Python 可以解析 HTML 網頁內容，並提取出我們需要的資訊
import csv      # 載入 csv 套件，讓 Python 可以讀寫 CSV 檔案，進行資料處理，或是將資料存入 CSV 檔案
import re       # 載入 re 套件，讓 Python 可以使用正規表達式進行文字處理，例如搜尋特定符號或文字，或是進行文字取代
import pandas as pd
import sqlite3


class PConeScraper:
    def __init__(self, url, output_path):
        """
        初始化 PConeScraper 類別，設定要爬取的網頁 URL 和輸出檔案路徑。
        """
        self.url = url      # 設定要爬取的網頁 URL
        self.output_path = output_path      # 設定輸出檔案路徑
        self.headers = {
            'content-type': 'text/plain;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }       # 設定 HTTP 請求的標頭，讓網站認為我們是透過瀏覽器存取網頁

    def fetch_page(self):
        """
        下載網頁內容，以 GET 請求方式取得指定 URL 的內容。
        Returns:
            str: 網頁的 HTML 內容。
        """

        try:        # 用 try-except 包住程式碼，以防止程式碰到錯誤而中斷
            response = requests.get(self.url, headers=self.headers)  # 以 GET 方式取得網頁資料，並存入 response 物件
            print("成功")       # 如果成功取得網頁資料，印出成功訊息
        except:     # 如果發生錯誤，印出失敗訊息，並回傳 None
            print("失敗")       # 如果發生錯誤，印出失敗訊息
            return None         # 回傳 None

        return response.text  # 返回網頁的 HTML 內容，以供後續程式碼解析

    def parse_page(self, html):
        """
        解析網頁內容，提取個別產品頁面的連結。
        Args:
            html (str): 網頁的 HTML 內容。
        Returns:
            list: 包含產品連結的列表。
        """
        if not html:        # 如果沒有收到 HTML 內容，回傳 None
            return None

        soup = BeautifulSoup(html, "html.parser")  # 使用 BeautifulSoup 解析 HTML 內容，並存入 soup 物件，以供後續程式碼解析
        product_links = soup.find_all("a", class_="product-list-item")  # 找到所有產品連結，尋找被a標籤包住，且class為product-list-item的元素，並存入 product_links
        return product_links        # 回傳產品連結列表

    def scrape_product(self, product_link):
        """
        爬取個別產品頁面的資訊。
        Args:
            product_link (Tag): 產品頁面的連結。
        Returns:
            list: 包含爬取到的產品資訊。
        """
        product_url = "https://www.pcone.com.tw/" + product_link.get("href")  # 構建產品頁面的 URL
        response = requests.get(product_url, headers=self.headers)  # 以 GET 方式取得產品頁面資料
        soup = BeautifulSoup(response.text, "html.parser")  # 使用 BeautifulSoup 解析 HTML 內容

        shop_name = soup.find("div", class_="merchant-name").text  # 提取店家名稱，尋找被div標籤包住，且class為merchant-name的元素，並提取文字部分
        product_name = soup.find("h1", class_="name x-large-font").text  # 提取產品名稱，尋找被h1標籤包住，且class為name x-large-font的元素，並提取文字部分

        shop_info = soup.find_all("p", class_="data medium-font")  # 提取店家相關資訊，尋找被p標籤包住，且class為data medium-font的元素，並存入 shop_info
        shop_quantity = shop_info[0].text  # 提取店家商品數量，shop_info[0]為第一個元素，並提取文字部分
        shop_rating = shop_info[1].text  # 提取店家評價，shop_info[1]為第二個元素，並提取文字部分
        shop_shipping_time = shop_info[2].text  # 提取店家出貨天數，shop_info[2]為第三個元素，並提取文字部分
        shop_reply_rate = shop_info[3].text  # 提取店家回覆率，shop_info[3]為第四個元素，並提取文字部分

        product_price = soup.find("div", class_="site-color medium-font site-color").text  # 提取商品價格，尋找被div標籤包住，且class為site-color medium-font site-color的元素，並提取文字部分
        product_price = product_price.split('$')[1]  # 提取價格部分，並去除$符號 (split() 方法會將字串切割成多個部分，並回傳一個列表)

        product_rating = soup.find("div", class_="review pointer").text  # 提取商品評分，尋找被div標籤包住，且class為review pointer的元素，並提取文字部分
        product_rating = product_rating.split('(')[0]  # 提取評分部分，並去除(符號

        try:        # 用 try-except 包住程式碼，以防止程式碰到錯誤而中斷
            original_price = soup.find_all("div", class_="minor tiny-font text-line-through")  # 提取原價，尋找被div標籤包住，且class為minor tiny-font text-line-through的元素，並存入 original_price
            original_price = original_price[0].text.split("$")[1]  # 提取原價部分，並去除$符號
        except:
            original_price = product_price  # 如果沒有特價，使用商品價格作為原價，以便計算折扣百分比

        discount_percentage = int(product_price) / int(original_price) * 100  # 計算折扣百分比，並轉為整數
        discount_percentage = int(discount_percentage)  # 將折扣百分比轉為整數

        purchase_info = soup.find("div", class_="review-info d-flex justify-content-start")  # 提取購買人數，尋找被div標籤包住，且class為review-info d-flex justify-content-start的元素，並存入 purchase_info
        purchase_count = re.findall(r"\d+\.?\d*", purchase_info.text)[2]  # 提取購買人數，並去除文字部分，只留下數字部分，並轉為整數

        return [shop_name, product_name, shop_quantity, shop_rating, shop_shipping_time, shop_reply_rate,
                product_price, discount_percentage, product_rating, purchase_count]         # 回傳爬取到的產品資訊

    def save_to_csv(self, data):
        """
        將爬取到的資料保存到 CSV 檔案中。
        Args:
            data (list): 要保存的爬取資料。
        """
        with open(self.output_path, 'w', newline='', encoding='utf-8-sig') as f:            # 開啟 CSV 檔案，並設定編碼為 utf-8-sig，以防止中文亂碼，並設定 newline=''，以防止換行時產生空行，並將檔案物件存入 f
            writer = csv.writer(f)                                                    # 建立 CSV 檔寫入器，並將檔案物件傳入 writer
            writer.writerow(["店家名稱", "產品名稱", "店家商品數量", "店家評價", "店家出貨天數", "店家回覆率", "特價", "折數", "商品評分", "購買人數"])     # 寫入欄位名稱

            for item in data:                                                  # 將爬取到的資料一筆一筆寫入 CSV 檔案
                writer.writerow(item)                                   # 寫入一列資料

    def run_scraper(self):
        """
        執行網頁爬蟲。
        """
        html = self.fetch_page()        # 取得網頁 HTML 原始碼
        product_links = self.parse_page(html)       # 解析網頁原始碼，取得產品連結

        scraped_data = []       # 建立一個空的 list 來保存爬取到的資料
        if product_links:       # 如果有爬取到產品連結
            for link in product_links:      # 對於每個產品連結
                item_data = self.scrape_product(link)       # 爬取產品資訊
                scraped_data.append(item_data)      # 將爬取到的資料加入 scraped_data

        self.save_to_csv(scraped_data)      # 將爬取到的資料保存到 CSV 檔案中


# 執行網頁爬蟲
scraper = PConeScraper("https://www.pcone.com.tw/product/603#ref=d_nav",
                       "/Users/sean/coding/hw 15.25.40/final-test/期末.csv")        # 建立 PConeScraper 物件，並傳入網址和要保存的檔案路徑
scraper.run_scraper()       # 執行網頁爬蟲
