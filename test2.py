import unittest
import ast
from pprint import pprint
from pymongo import MongoClient
import json
from query_parse_and_execution import check_field_name,\
     check_collection_name, single_operation_handler, split_by_dot, logical_operation_handler
from project_const import const
class TestStringMethods(unittest.TestCase):
    
    def setUp(self):
        self.client = MongoClient(const.LOCALHOST)
        self.database = self.client[const.MYDB]
        self.book_collection = self.database[const.BOOKDB]
        self.author_collection = self.database[const.AUTHORDB]
        pass

    # Check for a valid collection name.
    def test_valid_collection_name(self):
        check_collection_name("book")

    # Check for an invalid collection name.
    def test_invalid_collection_name(self):
        with self.assertRaises(Exception) as context:
            check_collection_name("bad")
        self.assertTrue('Collection bad does not exist' in str(context.exception))

    # Check for a valid field name.
    def test_valid_field_name(self):
        check_field_name("book", "book_id")

    # Check for an invalid field name.
    def test_invalid_field_name(self):
        with self.assertRaises(Exception) as context:
            check_field_name("book", "wrong")
        self.assertTrue('Field wrong does not exist' in str(context.exception))
    
    # Check the usage of > operator
    def test_greater_operator(self):
        user_input = 'book.rating_count:>"200"'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 32)

    # Check the usage of < operator
    def test_smaller_operator(self):
        user_input = 'book.rating_count:<"500"'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 36)
    
    # Check the usage of "" operator
    def test_regex_expression(self):
        user_input = 'book.book_id:50'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 3)

    # Check the regex for book rating
    def test_regex_expression2(self):
        user_input = 'book.rating:4'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 33)

    # Check the regex for author rating count
    def test_regex_expression_author(self):
        user_input = 'author.rating_count:5'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 21)

    # Check the simplest expression
    def test_exact_expression(self):
        user_input = 'book.book_id:320'
        collection, query = single_operation_handler(user_input)
        for result in self.database[collection].find(query):
            self.assertEqual(result['book_id'], '320')
    
    # Check for > and regex simultaneously
    def test_greater_and_regex(self):
        with self.assertRaises(Exception) as context:
            user_input = 'book.rating_count: > 320'
            single_operation_handler(user_input)
        self.assertTrue('Comparison operator \
            cannot be used simultaneously with regex expression' in str(context.exception))

    # Check for < and regex simultaneously
    def test_greater_and_regex(self):
        with self.assertRaises(Exception) as context:
            user_input = 'book.rating_count: < 320'
            single_operation_handler(user_input)
        self.assertTrue('Comparison operator \
            cannot be used simultaneously with regex expression' in str(context.exception))

    # Check the usage for NOT operator
    def test_not_operator(self):
        user_input = 'book.book_id:not 320'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 49)
    
    # Check usage for multiple NOT cases
    def test_not_operator2(self):
        user_input = 'author.author_id:not 30'
        collection, query = single_operation_handler(user_input)
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 36)
    
    # Check the split by dot function for book
    def test_split_by_dot(self):
        user_input = "book.book_id:123"
        result = user_input.split(":", maxsplit = 2)
        collcetion, field = split_by_dot(result)
        self.assertEqual(collcetion, "book")
        self.assertEqual(field, "book_id")
    
    # Check the split by dot function for author
    def test_split_by_dot2(self):
        user_input = "author.rating:123"
        result = user_input.split(":", maxsplit = 2)
        collcetion, field = split_by_dot(result)
        self.assertEqual(collcetion, "author")
        self.assertEqual(field, "rating")

    # Check AND operator and regex
    def test_and_operator_regex(self):
        user_input = "book.book_id:3 and book.title:hun"
        collection, query = logical_operation_handler(user_input, " and ")
        for result in self.database[collection].find(query):
            self.assertEqual(result['book_id'], '320')

    # Check OR operator and regex
    def test_or_operator_regex(self):
        user_input = "book.book_id:32 or book.title:on"
        collection, query = logical_operation_handler(user_input, " or ")
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 10)

    # Check AND operator with exact expression
    def test_and_operator_exact(self):
        user_input = 'book.review_count:"19322" and book.rating:"3.83"'
        collection, query = logical_operation_handler(user_input, " and ")
        for result in self.database[collection].find(query):
            self.assertEqual(result['book_id'], '485894')
    
    # Check OR operator with exact expression
    def test_or_operator_exact(self):
        user_input = 'book.book_id:"320" or book.rating:"4.46"'
        collection, query = logical_operation_handler(user_input, " or ")
        count = 0
        for _ in self.database[collection].find(query):
            count+=1
        self.assertEqual(count, 2)

    def test_wrong_operator(self):
        user_input = 'book.book_id:32 and rating:0'
        with self.assertRaises(Exception) as context:
            logical_operation_handler(user_input, " and ")
        self.assertTrue('Collection rating does not exist' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
