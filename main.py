""" This runs a web scraper and can import/export JSON file to/from mongoDB"""
import argparse
import requests

from bs4 import BeautifulSoup
from query_parse_and_execution import single_operation_handler,\
    logical_operation_handler, print_result_with_counting
from scrap_from_soup import scrape_into_database
from project_const import const
from read_write import export_authors_to_json,export_books_to_json,\
    read_from_author_json,read_from_book_json
from api import api_book_id

parser = argparse.ArgumentParser(description = \
    "scrap book from URL and/or import/export JSON file to/from mongodb")
parser.add_argument("-u", "--url", type = str, help = "indicate the starting URL")
parser.add_argument("-a", "--author", type = int, help = "desired author count",\
    default = const.DEFAULT_AUTHOR_COUNT)
parser.add_argument("-b", "--book", type = int, help = "desired book count", \
    default = const.DEFAULT_BOOK_COUNT)
parser.add_argument("-rb", "--readbook", type = str, help = "read from book JSON file")
parser.add_argument("-ra", "--readauthor", type = str, help = "read from author JSON file")
parser.add_argument("-eb", "--exbook", type = str, help = \
    "export the book database to JSON file")
parser.add_argument("-ea", "--exauthor", type = str, help = \
    "export the author database to JSON file")
parser.add_argument("-g", "--get", type = str, help = "API GET")

args = parser.parse_args()

if args.readbook:
    try:
        read_from_book_json(args.readbook)
    except:
        print("JSON file is invalid")

if args.readauthor:
    try:
        read_from_author_json(args.readauthor)
    except:
        print("JSON file is invalid")

if args.author > const.DEFAULT_AUTHOR_COUNT:
    print("Scrapping until desired author number may take longer than expected.")

if args.book > const.DEFAULT_BOOK_COUNT:
    print("Scrapping until desired book number may take longer than expected.")

if args.url:
    try:
        url = requests.get(args.url)
        valid_book_soup = BeautifulSoup(url.content, const.HTML)
        book_id = valid_book_soup.find("input", type = "hidden", id = "book_id")['value']
        if book_id != 0:
            print("Will now try start scraping")
            scrape_into_database(valid_book_soup, args.book, args.author)
    except:
        print("URL is invalid")

if args.exbook:
    export_books_to_json(args.exbook)

if args.exauthor:
    export_authors_to_json(args.exauthor)

user_input = input("indicate the operator and operation:")

# added whitespace to make uniformity
if " and " in user_input:
    collection, final_query = logical_operation_handler(user_input, " and ")
    print_result_with_counting(collection, final_query)

# added whitespace to avoid confusion with "author" which contains "or"
elif " or " in user_input:
    collection, final_query = logical_operation_handler(user_input, " or ")
    print_result_with_counting(collection, final_query)

# all other operators can only exist in a single operation
else:
    collection, final_query = single_operation_handler(user_input)
    print_result_with_counting(collection, final_query)
