"""This file contains the scrap function"""

from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

from project_const import const

class ScrapFromSoup():
    """This class stores the information from the scraper.
        Converts the book_soup as well as the author_soup to a dictionary
        that is easily converted to a JSON file."""
    def __init__(self, book_soup_in, author_soup_in):
        self.book_info = {}
        self.book_info["book_url"] = \
            book_soup_in.find("link")['href']
        self.book_info["title"] = \
            book_soup_in.title.contents[0]
        self.book_info["book_id"] = \
            book_soup_in.find("input", type = "hidden", id = "book_id")['value']
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
        for urls in author_soup_in.findAll("a", href = True):
            if "author/list" in str(urls):
                self.author_info["author_books"] = \
                    "https://www.goodreads.com" + (urls['href'])
            break
    def print_author_name(self):
        """Print the name of the author"""
        print(self.author_info["name"])
    def print_book_name(self):
        """Print the name of the book"""
        print(self.book_info["title"])

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
