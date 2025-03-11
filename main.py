from bs4 import BeautifulSoup
import requests

initial_link = "https://www.ceneo.pl/"
modified_link = ""

number = input("Enter product number: ")

modified_link = initial_link + number
html_text = requests.get(modified_link).text
soup = BeautifulSoup(html_text, "lxml")
print(soup.prettify())