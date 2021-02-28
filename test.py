import unittest
import main
import json
import requests
from bs4 import BeautifulSoup
class TestStringMethods(unittest.TestCase):

    def setUp(self):
        FIRSTBOOKURL = "https://www.goodreads.com/book/show/3735293-clean-code"
        book_soup = BeautifulSoup(requests.get(FIRSTBOOKURL).content, "lxml")
        bookAuthorURL = book_soup.find("meta", property = "books:author")['content']
        author_soup = BeautifulSoup(requests.get(bookAuthorURL).content, "lxml")
        self.book = main.SoupToJSON(book_soup, author_soup)
        pass

    # Returns True if the id is correct.
    def test_book_id(self):
        self.assertEqual(self.book.book_info["book_id"], \
        "3735293")

    # Returns True if the title is correct.
    def test_book_title(self):
        self.assertEqual(self.book.book_info["title"], \
        "Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin")

    # Returns True if the ISBN is correct.
    def test_ISBN(self):
        self.assertEqual(self.book.book_info["ISBN"], \
        "9780132350884")

    # Returns True if the book rating is correct.
    def test_book_rating(self):
        self.assertEqual(self.book.book_info["rating"], \
        "4.40")

    # Returns True if the book rating count is correct.
    def test_book_rating_count(self):
        self.assertEqual(self.book.book_info["rating_count"], \
        "14891")

    # Returns True if the book review count is correct.
    def test_book_review_count(self):
        self.assertEqual(self.book.book_info["review_count"], \
        "876")

    # Returns True if the author name is correct.
    def test_author_name(self):
        self.assertEqual(self.book.author_info["name"], \
        "Robert C. Martin")

    # Returns True if the author_id is correct.
    def test_author_id(self):
        self.assertEqual(self.book.author_info["author_id"], \
        "45372")

    # Returns True if the author rating is correct.
    def test_author_rating(self):
        self.assertEqual(self.book.author_info["rating"], \
        "4.34")

    # Returns True if the author rating count is correct.
    def test_author_rating_count(self):
        self.assertEqual(self.book.author_info["rating_count"], \
        "26988")

if __name__ == '__main__':
    unittest.main()
