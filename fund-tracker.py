from importlib.resources import contents
from urllib.request import urlopen
import re
from bs4 import BeautifulSoup

FUND_DATA_URL = "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod="

def main():
    funds = get_funds()
    for fund in funds:
        html = get_fund_data(fund)
        scrape_html(html)
        break


def scrape_html(html):

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if len(script.contents) != 0 and "MainContent_FonFiyatGrafik" in script.contents[0]:
            series = re.search('series: \[\{\"name\":\"Fiyat\",\"data\":\[(.+?)\]\}\]',script.contents[0]).group(1)
            values = series.split(",")
            prices = [float(i) for i in values]
            print(prices)
            calculate_sortino_ratio(prices)


def calculate_sortino_ratio(prices):
    downside = []
    counter = 0
    for price in prices:
        if counter != 0:
            if price - prices[counter - 1] < 0:
                downside.append(price - prices[counter - 1])
        counter = counter + 1
    print(downside)



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