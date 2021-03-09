import argparse
import ast
from pprint import pprint
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient
from scrap_from_soup import ScrapFromSoup
from project_const import const

client = MongoClient(const.LOCALHOST)
database = client[const.MYDB]
book_collection = database[const.BOOKDB]
author_collection = database[const.AUTHORDB]

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
        if "not" in user_input_in:
            user_query = {field : {"$not" : value}}
        elif ">" in user_input_in:
            user_query = {field : {"$gt" : value}}
        elif "<" in user_input_in:
            user_query = {field : {"$lt" : value}}
        else:
            user_query = {field : value}
        return collection, user_query
    # check if there is a comparison operator while there does
    # not exist an exact search term. This is not allowed.
    if "<" in user_input_in or ">" in user_input_in:
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

def logical_operation_handler(user_input_in, operation_type):
    """handle the operator AND and OR"""
    # split by the operator
    first_part = user_input_in.split(operation_type)[0].strip()
    second_part = user_input_in.split(operation_type)[1].strip()
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
