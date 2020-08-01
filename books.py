from bs4 import BeautifulSoup as soup  
import requests
import pandas
from pandas import DataFrame
import csv

redirect_base_url = "http://books.toscrape.com/catalogue/"
base_url_start = "http://books.toscrape.com/catalogue/category/books_1/page-"
base_url_end = ".html"


with open('Books.csv', mode='w') as csv_file:
   fieldnames = ['Url', 'Title', 'Price', 'Rating', 'Availability']
   writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
   writer.writeheader()


# initialise variables
book_url = []
book_title = []
book_price = []
book_rating = []
book_availability = []
num_pages = 1

def rating_dict(argument):
    switcher = {
        "One": "1",
        "Two": "2",
        "Three":"3",
        "Four": "4",
        "Five": "5"
    }
    value_to_return = switcher.get(argument, "Invalid")
    if value_to_return == "Invalid":
    	raise Exception("Invalid rating value: " + str(argument))
    return value_to_return

def scrape_page(page_number):
	print("Page: " + str(page_number))
	url = base_url_start + str(page_number) + base_url_end
	response = requests.get(url)
	webpage = soup(response.content,"html.parser")

	# retrieve and set number of pages 
	if page_number == 1:
		global num_pages
		num_pages = int(webpage.find("li", {"class": "current"}).text.strip().split(" ")[3])

	# scrape data
	containers = webpage.findAll("article", {"class": "product_pod"})
	for container in containers:

		# get rating
		rating_html = container.find("p", class_=True)
		book_rating.append(rating_dict(rating_html["class"][1]))

		# get url and title
		url_and_title = container.h3.find("a", href=True, title=True)
		url = url_and_title.get('href').replace("../../", redirect_base_url)
		book_url.append(url)
		book_title.append(url_and_title.get('title'))

		# get price and availability
		price_and_availability = container.find("div", {"class": "product_price"})
		book_price.append(price_and_availability.find("p",{"class":"price_color"}).text.strip())
		book_availability.append(price_and_availability.find("p",{"class":"instock availability"}).text.strip())
		
page_number = 1
scrape_page(page_number)

# carry out pagination
while page_number != num_pages:
	page_number += 1
	scrape_page(page_number)


data = {
	'Book_Url': book_url,
	'Book_Title':book_title, 
	'Book_Price':book_price, 
	'Book_Rating':book_rating, 
	'Book_Availability':book_availability
}

df = DataFrame(data, columns = ['Book_Url','Book_Title','Book_Price','Book_Rating','Book_Availability'])

# encoding included to preserve currency symbol
df.to_csv('Books.csv', encoding='utf-8-sig')