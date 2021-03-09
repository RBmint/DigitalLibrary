import flask
from flask import request, jsonify
from main import single_operation_handler
from scrap_from_soup import scrape_into_database
from pymongo import MongoClient
from project_const import const
from bson.json_util import dumps
from bs4 import BeautifulSoup

app = flask.Flask(__name__)
app.config["DEBUG"] = True

client = MongoClient(const.LOCALHOST)
database = client[const.MYDB]

def search_and_return(input_in, result_in):
    collection, query = single_operation_handler(input_in)
    for result in database[collection].find(query):
        result_in.append(result)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>CS242 Project2 Main Page</h1>
<p>A Digital library: search for a book or author</p>'''

@app.route('/api/book', methods=['GET'])
def api_book_id():
    # Check if an ID was provided as part of the URL.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return flask.Response(status=400)
    results = []
    # Modify the user input based on request
    user_input = "book.book_id:" + "\"" + str(id) +"\""
    # Connect to mongoDB and make the search
    search_and_return(user_input, results)
    return dumps(results)

@app.route('/api/author', methods=['GET'])
def api_author_id():
    # Check if an ID was provided as part of the URL.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return flask.Response(status=400)
    results = []
    # Modify the user input based on request
    user_input = "author.author_id:" + "\"" + str(id) +"\""
    # Connect to mongoDB and make the search
    search_and_return(user_input, results)
    return dumps(results)

@app.route('/api/search', methods = ['GET'])
def api_search_query():
    # Check if q was provided as part of the URL.
    # If not, display an error in the browser.
    if 'q' in request.args:
        user_input = request.args['q']
    else:
        return flask.Response(status=400)
    results = []
    # Connect to mongoDB and make the search
    search_and_return(user_input, results)
    return dumps(results)

@app.route('/api/book', methods = ['POST'])
def api_post_one_book():
    if request.content_type != 'application/json':
        return flask.Response(status=415)
    book_json = request.json
    if book_json:
        del book_json['_id']
        client = MongoClient(const.LOCALHOST)
        database = client[const.MYDB]
        book_collection = database[const.BOOKDB]
        book_collection.insert_one(book_json)
        return ("INSERT SUCCESS")
    else:
        raise Exception("No JSON file input!")

@app.route('/api/books', methods = ['POST'])
def api_post_books():
    if request.content_type != 'application/json':
        return flask.Response(status=415)
    book_json = request.json
    if book_json:
        client = MongoClient(const.LOCALHOST)
        database = client[const.MYDB]
        book_collection = database[const.BOOKDB]
        for book in book_json:
            del book_json['_id']
            book_collection.insert_one(book)
        return ("INSERT SUCCESS")
    else:
        raise Exception("No JSON file input!")

@app.route('/api/author', methods = ['POST'])
def api_post_one_author():
    if request.content_type != 'application/json':
        return flask.Response(status=415)
    author_json = request.json
    if author_json:
        del author_json['_id']
        client = MongoClient(const.LOCALHOST)
        database = client[const.MYDB]
        author_collection = database[const.BOOKDB]
        author_collection.insert_one(author_json)
        return ("INSERT SUCCESS")
    else:
        raise Exception("No JSON file input!")

@app.route('/api/authors', methods = ['POST'])
def api_post_authors():
    if request.content_type != 'application/json':
        return flask.Response(status=415)
    author_json = request.json
    if author_json:
        client = MongoClient(const.LOCALHOST)
        database = client[const.MYDB]
        author_collection = database[const.BOOKDB]
        for author in author_json:
            del author_json['_id']
            author_collection.insert_one(author)
        return ("INSERT SUCCESS")
    else:
        raise Exception("No JSON file input!")

@app.route('/api/scrape', methods = ['POST'])
def api_scrape_books():
    if 'attr' in request.args:
        url = request.args['attr']
    else:
        return flask.Response(status=400)
    valid_book_soup = BeautifulSoup(url.content, const.HTML)
    book_id = valid_book_soup.find("input", type = "hidden", id = "book_id")['value']
    if book_id != 0:
        print("Will now try start scraping")
        scrape_into_database(valid_book_soup, 200, 50)

@app.route('/api/book', methods = ['PUT'])
def api_put_book():
    if 'id' in request.args:
        id = request.args['id']
    else:
        return flask.Response(status=400)
    book = database[const.BOOKDB].find_one({"bookID" : id})
    if book:
        body = request.form
        for elem in body:
            database[const.BOOKDB].update_one(
                {"bookID" : id},
                {
                    "$set" : {elem : body[elem]}
                }
            )
        return ("UPDATE SUCCESS")
    else:
        return flask.Response(status=404)

app.run()