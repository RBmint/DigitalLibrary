""" This file has the functions of import/export JSON file to/from mongoDB"""
import json
from pymongo import MongoClient #pylint: disable=E0401 
from bson.json_util import dumps #pylint: disable=E0401 
from project_const import const

def export_books_to_json (file_name):
    """ Export the book database to a JSON file"""
    client = MongoClient(const.LOCALHOST)
    database = client[const.MYDB]
    book_collection = database[const.BOOKDB]
    cursor = book_collection.find({})
    type_documents_count = database[const.BOOKDB].estimated_document_count()
    with open(file_name, 'w') as file:
        file.write('[')
        for i, document in enumerate(cursor, 1):
            file.write(dumps(document,indent = 4))
            if i != type_documents_count:
                file.write(',')
        file.write(']')
    file.close()

def export_authors_to_json (file_name):
    """ Export the author database to a JSON file"""
    client = MongoClient(const.LOCALHOST)
    database = client[const.MYDB]
    book_collection = database[const.AUTHORDB]
    cursor = book_collection.find({})
    type_documents_count = database[const.AUTHORDB].estimated_document_count()
    with open(file_name, 'w') as file:
        file.write('[')
        for i, document in enumerate(cursor, 1):
            file.write(dumps(document,indent = 4))
            if i != type_documents_count:
                file.write(',')
        file.write(']')
    file.close()

def read_from_book_json(file_to_read_from):
    """ Read from a JSON file containing books and add to database"""
    client = MongoClient(const.LOCALHOST)
    database = client[const.MYDB]
    book_collection = database[const.BOOKDB]
    with open(file_to_read_from, encoding="utf-8") as file:
        to_load = file.read()
        data = []
        data.extend(json.loads(to_load))
        book_collection.insert_many(data)

def read_from_author_json(file_to_read_from):
    """ Read from a JSON file containing authors and add to database"""
    client = MongoClient(const.LOCALHOST)
    database = client[const.MYDB]
    author_collection = database[const.AUTHORDB]
    with open(file_to_read_from, encoding="utf-8") as file:
        to_load = file.read()
        data = []
        data.extend(json.loads(to_load))
        author_collection.insert_many(data)
