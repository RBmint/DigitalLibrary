""" This main runs a web scraper and collect 200 unique books into a JSON file"""
import json
import requests
from bs4 import BeautifulSoup



FIRSTBOOKURL = input("please enter the URL of first book\n")

try:
    url = requests.get(FIRSTBOOKURL)
    print("URL is valid")
except:
    print("URL has been automatically set")
    FIRSTBOOKURL = "https://www.goodreads.com/book/show/3735293-clean-code"


# Clear the JSON file each time we run this main.py
open('Books.json', 'w').close()
open('Authors.json', 'w').close()

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

# Get book soup first, do not create soupToBookJSON yet, get author URL first.
book_soup = BeautifulSoup(requests.get(FIRSTBOOKURL).content, "lxml")

# Get author URL manually
bookAuthorURL = book_soup.find("meta", property = "books:author")['content']

# Create author soup
author_soup = BeautifulSoup(requests.get(bookAuthorURL).content, "lxml")

# Create soupToBookJSON last
book = SoupToJSON(book_soup, author_soup)

# Get the soup of similar books
similar_books_soup = BeautifulSoup(requests.get(\
book.book_info["similar_books"]).content, "lxml")

book_dic = {}
author_dic = {}

# Scrap data from similar books URL until we have desired number of
# unique books inside the book_dic.
while True:
    # Scrap 10 similar books/authors at a time
    for i in range (0, 21, 2):
        book_soup = BeautifulSoup(requests.get("https://www.goodreads.com" \
            + similar_books_soup.findAll(\
            "a", itemprop = "url", limit = 22)[i]['href']).content, "lxml")
        bookAuthorURL = book_soup.find("meta", property = "books:author")['content']
        author_soup = BeautifulSoup(requests.get(\
        similar_books_soup.findAll(\
            "a", itemprop = "url", limit = 22)[i+1]['href']).content, "lxml")
        book = SoupToJSON(book_soup, author_soup)
        # Check if book/author is going to be a duplicate
        if book.book_info['title'] not in book_dic:
            book_dic[book.book_info['title']] = book
        if book.author_info['author_id'] not in author_dic:
            author_dic[book.author_info['author_id']] = book
    # The number of total books scraped
    if len(book_dic) >= 10:
        break
    # Find similar book based on the last book stored in dictionary
    similar_books_soup = BeautifulSoup(\
        requests.get(book.book_info["similar_books"]).content, "lxml")

# Convert the dictionary to a single JSON output and save to file.
bookJSON = [book.book_info for book in book_dic.values()]
authorJSON = [book.author_info for book in author_dic.values()]

with open("Books.json", "a") as fp:
    json.dump(bookJSON, fp, indent = 4)
with open("Authors.json", "a") as fp:
    json.dump(authorJSON, fp, indent = 4)

# Load the JSON file. Don't know how should we use this yet.
# with open("Books.json", "r") as read_file:
#     data = json.load(read_file)
