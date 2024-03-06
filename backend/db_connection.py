"""
MongoDB connection setup
"""
from typing import Any, Dict, List, Optional, Union

from pymongo import MongoClient, results
from pymongo.database import Database as MongoDBDatabase
from pymongo.cursor import Cursor
# from bson.json_util import dumps
# from bson.objectid import ObjectId

import os
from dotenv import load_dotenv

from utils import calculate_running_time

load_dotenv()  # take environment variables from .env.


class Database:
    def __init__(self, uri: str) -> None:
        """
        Initialize the Database with the given URI.

        Args:
            uri (str): The URI for the database connection.
        """
        self.URI: str = uri
        self.client: Optional[MongoClient] = None
        self.database: Optional[MongoDBDatabase] = None
        self.collection: Optional[str] = None

    def connect(self, database: str, collection: str) -> None:
        """
        Connect to the specified database and collection.

        Args:
            database (str): The name of the database to connect to.
            collection (str): The name of the collection to connect to.
        Returns:
            None
        """
        self.client = MongoClient(self.URI)
        self.database = self.client.get_database(database)
        self.collection = collection

    def disconnect(self) -> None:
        if self.client:
            self.client.close()

    def _validate_connection(self) -> None:
        if self.client is None:
            raise RuntimeError("Database connection not established.")
        if self.database is None:
            raise RuntimeError("Database not selected.")
        if self.collection is None:
            raise RuntimeError("Collection not specified.")

    def create_index(
        self,
        index: str,
        expire_after_seconds: int = 3600
    ) -> None:
        """
        Create an index with the given parameters.

        Args:
            index (str): The name of the index.
            expire_after_seconds (int): The number of seconds
              the index expires (default 3600).
        Returns:
            None
        """
        self._validate_connection()
        self.database[self.collection].create_index(
            index,
            expireAfterSeconds=expire_after_seconds
        )

    def list_indexes(self) -> dict:
        """
        List all indexes in the specified collection.

        Returns:
            dict: A dictionary containing index information.
        """
        self._validate_connection()
        return self.database[self.collection].index_information()

    def drop_index(self, index: str) -> None:
        """
        Drops the specified index from the collection.

        Parameters:
            index (str): The name of the index to be dropped.

        Returns:
            None
        """
        self._validate_connection()
        self.database[self.collection].drop_index(index)

    def list_collection_names(self) -> List[str]:
        """
        Return a list of collection names in the database.
        """
        self._validate_connection()
        return self.database.list_collection_names()

    def insert_one(self, data: Dict[str, Any]) -> results.InsertOneResult:
        """
        Insert one document into the collection.

        :param data: The document to insert.
        :type data: Dict[str, Any]
        :return: The result of the insertion operation.
        :rtype: results.InsertOneResult
        """
        self._validate_connection()
        return self.database[self.collection].insert_one(data)

    def find(self, query: Dict[str, Any] = {}) -> Union[Cursor, Any]:
        """
        Find documents in the collection that match the specified query.

        :param query: A dictionary representing the query to match documents.
        :type query: dict, optional
        :return: A list of dictionaries representing the matched documents.
        :rtype: list[dict]
        """
        self._validate_connection()
        cursor = self.database[self.collection].find(query)
        return cursor

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in collection that matches the specified query.

        Args:
            query (Dict[str, Any]): The query to match documents.

        Returns:
            Optional[Dict[str, Any]]: The matching document, or None
              if no match is found.
        """
        self._validate_connection()
        return self.database[self.collection].find_one(query)

    def update_one(
        self,
        query: Dict[str, Any],
        data: Dict[str, Any]
    ) -> results.UpdateResult:
        """
        Update a single document in the collection that matches the query.

        :param query: A dictionary representing the query to match
          the document to be updated.
        :param data: A dictionary containing the fields and values to be
          updated in the matched document.
        :return: An instance of results.UpdateResult representing the result
          of the update operation.
        """
        self._validate_connection()
        return self.database[self.collection].update_one(query, {"$set": data})

    def delete_many(self, query: Dict[str, Any]) -> results.DeleteResult:
        """
        Delete multiple documents that match the specified query.

        :param query: A dictionary representing the query to match the
          documents to delete.
        :type query: Dict[str, Any]
        :return: The result of the delete operation.
        :rtype: results.DeleteResult
        """
        self._validate_connection()
        return self.database[self.collection].delete_many(query)

    def delete_one(self, query: Dict[str, Any]) -> results.DeleteResult:
        """
        Delete a single document matching the specified query from collection.

        Args:
            query (Dict[str, Any]): The query used to match the document to be
              deleted.

        Returns:
            results.DeleteResult: The result of the delete operation.
        """
        self._validate_connection()
        return self.database[self.collection].delete_one(query)


@calculate_running_time
def main():
    uri = os.environ.get('MONGODB_URI')
    if not uri:
        raise Exception('MONGODB_URI not set')
    db = Database(uri)
    db.connect('TEST_DB', 'users')
    # db.list_indexes()

    # print(db.list_collection_names())
    print(list(db.find({})))
    # db.create_index("users", "created_at", expire_after_seconds=3600)
    # ids = db.insert_one({'name': 'test37'}).inserted_id
    # print(ids)
    # db.insert_one({'name': 'test2'})

    # print('------------')
    # print(db.find_one('users', {'_id': ObjectId(ids)}))
    # print(db.find_one({'name': 'test37'}))
    # print(db.delete_one({'name': 'test2'}))


if __name__ == '__main__':
    main()
