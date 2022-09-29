import pandas
from bs4 import BeautifulSoup

import os
import re
import glob

if not os.path.exists("parsed_files"):
    os.mkdir("parsed_files")


df = pandas.DataFrame()

for file_name in glob.glob("html_files/*.html"):

	# file_name = "./html_files/goodrx_zoloft_tablet_50mg_30_20220915154804.html"
	base_name = os.path.basename(file_name) #only print the filename without path

	name = re.findall('goodrx_(.*)_(.*)_(.*)_(.*)_', base_name)[0][0]
	form = re.findall('goodrx_(.*)_(.*)_(.*)_(.*)_', base_name)[0][1]
	dosage = re.findall('goodrx_(.*)_(.*)_(.*)_(.*)_', base_name)[0][2]
	quantity = re.findall('goodrx_(.*)_(.*)_(.*)_(.*)_', base_name)[0][3]

	scrape_time = re.findall('\\d{14}',base_name)[0] #ask what does that mean,d means digit

	# print(name)
	# print(form)
	# print(dosage)
	# print(quantity)
	# print(scrape_time)

	f = open(file_name, "r")
	soup = BeautifulSoup(f.read(),"html.parser") #put everything in the file into the soup
	f.close() #close the file



	description = soup.find("span",{"data-qa": "drug-price-description"}).text
	generic_name = soup.find("div", {"data-qa": "drug-price-header-subtitle"}).text


	related_conditions = soup.find("div",{"data-qa": "related-conditions"})
	related_conditions_lists = related_conditions.find_all("span",{"class":"re-text"})

	related_conditions_string = "_".join([i.text for i in related_conditions_lists])
	print(related_conditions_string)
		
	# print(soup)

	pharmacy_list = soup.find("div",{"aria-label": "List of pharmacy prices"})
	pharmacy_row_box_list = pharmacy_list.find_all("div",{"data-qa":"pharmacy-row-box"})

	for pharmacy_row in pharmacy_row_box_list:
		pharmacy_name = pharmacy_row.find("span",{"aria-hidden": "true"}).text
		# print(pharmacy_name)
		price = pharmacy_row.find("span",{"data-qa":"pharmacy-row-price"}).text
		price = price.replace(" ", "") #replace the space to nothing in price
		# print(price)


		logo = pharmacy_row.find("img")['src'] 



		how_to_reg = pharmacy_row.find("span",{"class": "how_to_reg"})
		if how_to_reg is None:
			how_to_reg = "no-discount"
			discount_amount = "0"
		else:
			discount_amount = re.findall('\$(.*)', how_to_reg.parent.text)[0]
			how_to_reg = "with-discount"



		df = pandas.concat([df,    # concat means put two things together, put the name and price in one file
		pandas.DataFrame.from_records([{
			"pharmacy_name": pharmacy_name,
			"price": price,
			"goodrx_discount": how_to_reg,
			"name": name,
			"generic_name": generic_name,
			"form": form,
			"dosage": dosage,
			"quantity": quantity,
			"total_price": float(price) + float(discount_amount),
			"logo": logo,
			"related_conditions": related_conditions_string,
			"scrape_time": scrape_time
			}])
	    ])

df.to_csv("parsed_files/goodrx_dataset.csv",index=False)

print("done")
# pharmacy_name = soup.find("span",{"aria-hidden": "true"}) #id is always unique, but others are not
# print(pharmacy_name)
#  findall which is different from the findall before