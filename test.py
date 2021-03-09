import unittest
from scrap_from_soup import ScrapFromSoup
import json
import requests
from bs4 import BeautifulSoup
class TestStringMethods(unittest.TestCase):

    def setUp(self):
        FIRSTBOOKURL = "https://www.goodreads.com/book/show/3735293-clean-code"
        book_soup = BeautifulSoup(requests.get(FIRSTBOOKURL).content, "lxml")
        bookAuthorURL = book_soup.find("meta", property = "books:author")['content']
        author_soup = BeautifulSoup(requests.get(bookAuthorURL).content, "lxml")
        self.book = ScrapFromSoup(book_soup, author_soup)
        pass

    # Returns True if the url is correct.
    def test_book_url(self):
        self.assertEqual(self.book.book_info["book_url"], \
        "https://www.goodreads.com/book/show/3735293-clean-code")

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

    # Returns True if the image url is correct.
    def test_image_url(self):
        self.assertEqual(self.book.book_info["image_url"], \
        "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1436202607l/3735293._SX318_.jpg")

    # Returns True if the similar book is correct.
    def test_similar_books(self):
        self.assertEqual(self.book.book_info["similar_books"], \
        "https://www.goodreads.com/book/similar/3779106-clean-code-a-handbook-of-agile-software-craftsmanship-robert-c-martin")

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

if __name__ == '__main__':
    unittest.main()
