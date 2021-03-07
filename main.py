""" This runs a web scraper and can import/export JSON file to/from mongoDB"""
import argparse
import requests
from bs4 import BeautifulSoup #pylint: disable=E0401 
from pymongo import MongoClient #pylint: disable=E0401 
from scrap_from_soup import ScrapFromSoup
from project_const import const
from read_write import export_authors_to_json,export_books_to_json,\
    read_from_author_json,read_from_book_json

def scrape_into_database(book_soup, book_count, author_count):
    """ Scrap data from similar books URL until we have desired number of
    unique books inside the book_dic."""
    # Stop early if desired book count is greater than 2000
    if book_count > 2000:
        book_count = 2000
    # Get author URL manually
    book_author_url = book_soup.find("meta", property = "books:author")['content']
    # Create author soup
    author_soup = BeautifulSoup(requests.get(book_author_url).content, const.HTML)
    # Create soupToBookJSON last
    book = ScrapFromSoup(book_soup, author_soup)
    # Get the soup of similar books
    similar_books_soup = BeautifulSoup(requests.get(\
    book.book_info["similar_books"]).content, const.HTML)
    # Connect to MongoDB
    client = MongoClient(const.LOCALHOST)
    database = client[const.MYDB]
    book_collection = database[const.BOOKDB]
    author_collection = database[const.AUTHORDB]
    # Drop any collection that existed before
    book_collection.drop()
    author_collection.drop()
    # Create dictionary to check possible duplicates
    book_dic = {}
    author_dic = {}
    count = 0
    unique_count = 0
    while len(book_dic) < book_count and len(author_dic) < author_count:
        # Scrap 20 similar books/authors at a time
        for i in range (const.START_NUM, const.ITERATION_COUNT, const.STEP):
            book_soup = BeautifulSoup(requests.get("https://www.goodreads.com" \
                + similar_books_soup.findAll(\
                "a", itemprop = "url", limit = const.LIMIT)[i]['href']).content, const.HTML)
            book_author_url = book_soup.find("meta", property = "books:author")['content']
            author_soup = BeautifulSoup(requests.get(\
            similar_books_soup.findAll(\
                "a", itemprop = "url", limit = const.LIMIT)[i+1]['href']).content, const.HTML)
            # In case some books may not work
            try:
                book = ScrapFromSoup(book_soup, author_soup)
            except:
                count += 1
                print("skipped")
                continue
            # Check if book/author is going to be a duplicate
            if book.book_info['title'] not in book_dic:
                book_collection.insert_one(book.book_info)
                book_dic[book.book_info['title']] = book
                unique_count += 1
                count += 1
                print("found ", unique_count, " unique books in ", count, " searches")
            else:
                count += 1
                continue
            if book.author_info['author_id'] not in author_dic:
                author_collection.insert_one(book.author_info)
                author_dic[book.author_info['author_id']] = book
            if len(book_dic) >= book_count or len(author_dic) >= author_count:
                break
        # Find similar book based on the last book stored in dictionary
        similar_books_soup = BeautifulSoup(\
            requests.get(book.book_info["similar_books"]).content, const.HTML)

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
    # try:
        url = requests.get(args.url)
        valid_book_soup = BeautifulSoup(url.content, const.HTML)
        book_id = valid_book_soup.find("input", type = "hidden", id = "book_id")['value']
        if book_id != 0:
            print("Will now try start scraping")
            scrape_into_database(valid_book_soup, args.book, args.author)
    # except:
        print("URL is invalid")

if args.exbook:
    export_books_to_json(args.exbook)

if args.exauthor:
    export_authors_to_json(args.exauthor)

# FIRSTBOOKURL = input("please enter the URL of first book\n")
# try:
#     url = requests.get(FIRSTBOOKURL)
#     print("URL is valid")
# except:
#     print("URL has been automatically set")
#     #FIRSTBOOKURL = "https://www.goodreads.com/book/show/4099.The_Pragmatic_Programmer"
#     FIRSTBOOKURL = "https://www.goodreads.com/book/show/3735293-clean-code"
