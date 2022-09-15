from datetime import date, datetime
from importlib.resources import contents
from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
import statistics
import pandas as pd
from datetime import datetime

FUND_DATA_URL = "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod="

def main():
    funds = get_funds()
    for fund in funds:
        html = get_fund_data(fund)
        data = scrape_html(html)
        sortino = calculate_sortino_ratio(data)
        print(fund, sortino)
        


def scrape_html(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if len(script.contents) != 0 and "MainContent_FonFiyatGrafik" in script.contents[0]:
            series = re.search('series: \[\{\"name\":\"Fiyat\",\"data\":\[(.+?)\]\}\]',script.contents[0]).group(1)
            values = series.split(",")
            prices = [float(i) for i in values]

            date_string = re.search('xAxis: \[\{\"categories\":\[(.+?)\]',script.contents[0]).group(1)
            date_string_list = date_string.split(",")

            dates = []
            for date_str in date_string_list:
                date_str = date_str[1:len(date_str) - 1]
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                dates.append(date_obj)
            
            data = {'date': dates, 'price': prices}
            df = pd.DataFrame(data)
            return df
            

def calculate_sortino_ratio(data):
    prices = data["price"]

    delta = ((prices.iloc[-1] - prices.iloc[0]) * 100) / prices.iloc[0]
    return delta

    # For multiple years
    # sortino_record = []
    # downside = []
    # counter = 0
    # for price in prices:
    #     if counter != 0:
    #         sortino_record.append(price - prices[counter - 1])
    #         if price - prices[counter - 1] < 0:
    #             downside.append(price - prices[counter - 1])
    #     counter = counter + 1
    # downside_std = statistics.stdev(downside)
    # mean_return = sum(sortino_record) / len(sortino_record)

    # sortino = (mean_return - 0.1) / downside_std
    # print(sortino)



def get_fund_data(fund):
    page = urlopen(f"{FUND_DATA_URL}{fund}")
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def get_funds():
    funds = []
    fhand = open('list.txt')

    for line in fhand:
        line = line.rstrip()
        funds.append(line)
    
    return funds


if __name__ == "__main__":
    main()