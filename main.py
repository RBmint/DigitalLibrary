""" This main runs a web scraper and collect 200 unique books into a JSON file"""
import json
import requests
import argparse

from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.json_util import dumps


def ExportBooksToJSON (file_name):
    client = MongoClient("localhost:27017")
    db = client['mydb']
    book_collection = db['book']
    cursor = book_collection.find({})
    type_documents_count = db['book'].estimated_document_count()
    with open(file_name, 'w') as file:
        file.write('[')
        for i, document in enumerate(cursor, 1):
            file.write(dumps(document,indent = 4))
            if i != type_documents_count:
                file.write(',')
        file.write(']')
    file.close()

def ExportAuthorsToJSON (file_name):
    client = MongoClient("localhost:27017")
    db = client['mydb']
    book_collection = db['author']
    cursor = book_collection.find({})
    type_documents_count = db['author'].estimated_document_count()
    with open(file_name, 'w') as file:
        file.write('[')
        for i, document in enumerate(cursor, 1):
            file.write(dumps(document,indent = 4))
            if i != type_documents_count:
                file.write(',')
        file.write(']')
    file.close()


# FIRSTBOOKURL = input("please enter the URL of first book\n")
# try:
#     url = requests.get(FIRSTBOOKURL)
#     print("URL is valid")
# except:
#     print("URL has been automatically set")
#     #FIRSTBOOKURL = "https://www.goodreads.com/book/show/4099.The_Pragmatic_Programmer"
#     FIRSTBOOKURL = "https://www.goodreads.com/book/show/3735293-clean-code"


# Converts the book_soup as well as the author_soup to a dictionary
# that is easily converted to a JSON file.
class SoupToJSON():
    """This class stores the information from the scraper"""
    def __init__(self, book_soup_in, author_soup_in):
        self.book_info = {}
        self.book_info["book_url"] = \
            book_soup_in.find("link")['href']
        self.book_info["title"] = \
            book_soup_in.title.contents[0]
        self.book_info["book_id"] = \
            book_soup_in.find("input", id = "book_id")['value']
        self.book_info["ISBN"] = \
            book_soup_in.find("meta", property = "books:isbn")['content']
        self.book_info["author_url"] = \
            book_soup_in.find("meta", property = "books:author")['content']
        self.book_info["author"] = \
            author_soup_in.find("meta", property = "og:title")['content']
        self.book_info["rating"] = \
            book_soup_in.find("span", itemprop = "ratingValue").text.strip()
        self.book_info["rating_count"] = \
            book_soup_in.find("meta", itemprop = "ratingCount")['content']
        self.book_info["review_count"] = \
            book_soup_in.find("meta", itemprop = "reviewCount")['content']
        self.book_info["image_url"] = \
            book_soup_in.find("img", id = "coverImage")['src']
        self.book_info["similar_books"] = \
            book_soup_in.find("a", class_ = "actionLink right seeMoreLink")['href']

        self.author_info = {}
        self.author_info["name"] = \
            author_soup_in.find("meta", property = "og:title")['content']
        self.author_info["author_url"] = \
            author_soup_in.find("link")['href']
        self.author_info["author_id"] = \
            ''.join([x for x in author_soup_in.find("link")['href'] if x.isdigit()])
        self.author_info["rating"] = \
            author_soup_in.find("span", itemprop = "ratingValue").text
        self.author_info["rating_count"] = \
            author_soup_in.find("span", itemprop = "ratingCount")['content']
        self.author_info["review_count"] = \
            author_soup_in.find("span", itemprop = "reviewCount")['content']
        self.author_info["image_url"] = \
            author_soup_in.find("meta", itemprop = "image")['content']
        self.author_info["related_authors"] = \
            "https://www.goodreads.com" \
            + author_soup_in.find("a", text = "Similar authors")['href']
        for url in author_soup_in.findAll("a", href = True):
            if "author/list" in str(url):
                self.author_info["author_books"] = \
                    "https://www.goodreads.com" + (url['href'])
            break
    def print_author_name(self):
        """Print the name of the author"""
        print(self.author_info["name"])
    def print_book_name(self):
        """Print the name of the book"""
        print(self.book_info["title"])


# Scrap data from similar books URL until we have desired number of
# unique books inside the book_dic.
def StartScrapping(book_soup, book_count, author_count):
    # Get author URL manually
    bookAuthorURL = book_soup.find("meta", property = "books:author")['content']
    # Create author soup
    author_soup = BeautifulSoup(requests.get(bookAuthorURL).content, "lxml")
    # Create soupToBookJSON last
    book = SoupToJSON(book_soup, author_soup)
    # Get the soup of similar books
    similar_books_soup = BeautifulSoup(requests.get(\
    book.book_info["similar_books"]).content, "lxml")
    # Connect to MongoDB
    client = MongoClient("localhost:27017")
    db = client['mydb']
    book_collection = db['book']
    author_collection = db['author']
    # Drop any collection that existed before
    book_collection.drop()
    author_collection.drop()
    # Create dictionary to check possible duplicates
    book_dic = {}
    author_dic = {}
    while True:
        # Scrap 5 similar books/authors at a time
        for i in range (0, 11, 2):
            book_soup = BeautifulSoup(requests.get("https://www.goodreads.com" \
                + similar_books_soup.findAll(\
                "a", itemprop = "url", limit = 22)[i]['href']).content, "lxml")
            bookAuthorURL = book_soup.find("meta", property = "books:author")['content']
            author_soup = BeautifulSoup(requests.get(\
            similar_books_soup.findAll(\
                "a", itemprop = "url", limit = 22)[i+1]['href']).content, "lxml")
            # In case some books may not work
            try:
                book = SoupToJSON(book_soup, author_soup)
            except:
                continue        
            # Check if book/author is going to be a duplicate
            if book.book_info['title'] not in book_dic:
                book_collection.insert_one(book.book_info)
                book_dic[book.book_info['title']] = book
            if book.author_info['author_id'] not in author_dic:
                author_collection.insert_one(book.author_info)
                author_dic[book.author_info['author_id']] = book
        # The number of total books scraped
        if len(book_dic) >= book_count or len(author_dic >= author_count):
            break
        # Find similar book based on the last book stored in dictionary
        similar_books_soup = BeautifulSoup(\
            requests.get(book.book_info["similar_books"]).content, "lxml")

def ReadFromBookJSON(file_to_read_from):
    client = MongoClient("localhost:27017")
    db = client['mydb']
    book_collection = db['book']
    with open(file_to_read_from, encoding="utf-8") as f:
        str = f.read()
        data = []
        data.extend(json.loads(str))
        book_collection.insert_many(data)

def ReadFromAuthorJSON(file_to_read_from):
    client = MongoClient("localhost:27017")
    db = client['mydb']
    author_collection = db['author']
    with open(file_to_read_from, encoding="utf-8") as f:
        str = f.read()
        data = []
        data.extend(json.loads(str))
        author_collection.insert_many(data)


parser = argparse.ArgumentParser(description = \
    "scrap book from URL and/or import/export JSON file to/from mongodb")
parser.add_argument("-u", "--url", type = str, help = "indicate the starting URL")
parser.add_argument("-a", "--author", type = int, help = "desired author count", default = 50)
parser.add_argument("-b", "--book", type = int, help = "desired book count", default = 200)
parser.add_argument("-rb", "--readbook", type = str, help = "read from book JSON file")
parser.add_argument("-ra", "--readauthor", type = str, help = "read from author JSON file")
parser.add_argument("-eb", "--exbook", type = str, help = \
    "export the book database to JSON file")
parser.add_argument("-ea", "--exauthor", type = str, help = \
    "export the author database to JSON file")
args = parser.parse_args()

if args.readbook:
    try:
        ReadFromBookJSON(args.readbook)
    except:
        print("JSON file is invalid")
if args.readauthor:
    try:
        ReadFromAuthorJSON(args.readauthor)
    except:
        print("JSON file is invalid")
if args.author > 50:
    print("Scrapping until desired author number may take longer than expected.")
if args.book > 200:
    print("Scrapping until desired book number may take longer than expected.")
if args.url:
    try:
        url = requests.get(args.url)
        book_soup = BeautifulSoup(requests.get(args.url).content, "lxml")
        book_id = book_soup.find("input", id = "book_id")['value']
        if (book_id != 0):
            print("URL is valid")
            StartScrapping(book_soup, args.book, args.author)
    except:
        print("URL is invalid")
if args.exbook:
    ExportBooksToJSON(args.exbook)
if args.exauthor:
    ExportAuthorsToJSON(args.exauthor)

