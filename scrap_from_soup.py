"""This file contains the scrap function"""
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
