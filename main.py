""" This runs a web scraper and can import/export JSON file to/from mongoDB"""
import argparse
import ast
from pprint import pprint
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient
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
    # Use two counter to keep track of the scraping process
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
                # Beautifulsoup failed to create on a particular book
                count += 1
                continue
            # Check if book/author is going to be a duplicate
            if book.book_info['title'] not in book_dic:
                book_collection.insert_one(book.book_info)
                book_dic[book.book_info['title']] = book
                unique_count += 1
                count += 1
                print("found ", unique_count, " unique books in ", count, " searches")
            else:
                # The book scraped is a duplicate
                count += 1
                continue
            # Because every book has a corresponding author, no need to count separately
            if book.author_info['author_id'] not in author_dic:
                author_collection.insert_one(book.author_info)
                author_dic[book.author_info['author_id']] = book
            # Break out of the loop earlier if the desired num is already satisfied
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

def check_field_name(collection_name_in, field_name_in):
    """check if the field name is valid"""
    field_name = field_name_in
    # because the collection name has already been checked,
    # we can thus use database[collection] directly
    if database[collection_name_in].find({field_name:{"$exists": True}}).count() == 0:
        raise Exception("Field " + field_name + " does not exist.")

def check_collection_name(collection_name_in):
    """check if the collection name is valid"""
    collection_name = collection_name_in
    if collection_name not in database.list_collection_names():
        raise Exception("Collection " + collection_name + " does not exist.")

def single_operation_handler(user_input_in):
    """Handle situation for NOT and comparison operators"""
    # check if the operator specified the exact search term
    if "\"" in user_input_in:
        result = user_input_in.split(":", maxsplit = 2)
        value = result[1].split("\"")[1].strip()
        collection, field = split_by_dot(result)
        if "not" in user_input:
            user_query = {field : {"$not" : value}}
        elif ">" in user_input:
            user_query = {field : {"$gt" : value}}
        elif "<" in user_input:
            user_query = {field : {"$lt" : value}}
        else:
            user_query = {field : value}
        return collection, user_query
    # check if there is a comparison operator while there does
    # not exist an exact search term. This is not allowed.
    if "<" in user_input or ">" in user_input:
        raise Exception("Comparison operator \
            cannot be used simultaneously with regex expression")
    result = user_input_in.split(":", maxsplit = 2)
    value = result[1].strip()
    # check if there is a NOT operator and deal with the query accordingly
    if "not" in value:
        value = value.split("not")[1].strip()
        collection, field = split_by_dot(result)
        user_query = {field : {"$not" : {"$regex" : ".*" + value + ".*"}}}
        return collection, user_query
    # if no special operator at all, the query is simple as below
    collection, field = split_by_dot(result)
    user_query = {field : {"$regex" : ".*" + value + ".*"}}
    return collection, user_query

def split_by_dot(result):
    """split the field name by the dot"""
    # check the collection name first
    collection = result[0].split(".")[0].strip()
    check_collection_name(collection)
    # check the field in the corresponding collection
    field = result[0].split(".")[1].strip()
    check_field_name(collection, field)
    return collection, field

def logical_operation_handler(operation_type):
    """handle the operator AND and OR"""
    # split by the operator
    first_part = user_input.split(operation_type)[0].strip()
    second_part = user_input.split(operation_type)[1].strip()
    # handle both part as one single operation
    collection, first_query = single_operation_handler(first_part)
    collection, second_query = single_operation_handler(second_part)
    # link the two operations by the operator into one query
    final_query = ast.literal_eval("{'$" + operation_type.strip() + \
        "':[" + str(first_query) +","+ str(second_query) + "]}")
    print_result_with_counting(collection, final_query)

def print_result_with_counting(collection, result_in):
    """pretty print the result of the query"""
    count = 0
    # because the collection name has already been checked,
    # we can thus use database[collection] directly
    for result in database[collection].find(result_in):
        pprint(result)
        count += 1
    print("total count = " , count)

user_input = input("indicate the operator and operation:")
client = MongoClient(const.LOCALHOST)
database = client[const.MYDB]
book_collection = database[const.BOOKDB]
author_collection = database[const.AUTHORDB]

# added whitespace to make uniformity
if " and " in user_input:
    logical_operation_handler(" and ")
# added whitespace to avoid confusion with "author" which contains "or"
elif " or " in user_input:
    logical_operation_handler(" or ")
# all other operators can only exist in a single operation
else:
    collection, final_query = single_operation_handler(user_input)
    print_result_with_counting(collection, final_query)
