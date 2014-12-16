from pymongo import MongoClient

import config


class Connection(object):
    """
    Singleton Database connection object for the Mongo Database.

    Args:
        location: 'private' or 'public'
    Returns:
        A connection singleton to either the public or private Mongo database, or null if location is invalid.
    """

    _client_public = None
    _client_private = None

    def __new__(cls, *args, **kwargs):
        parser = config.Config()

        if args:
            if args[0] in ('public',):
                if not cls._client_public:
                    temp = MongoClient(parser['database']['public_mongo_url'])
                    cls._client_public = temp[parser['database']['public_mongo_db']]

                return cls._client_public

            if args[0] in ('private',):
                if not cls._client_private:
                    temp = MongoClient(parser['database']['private_mongo_url'])
                    cls._client_private = temp[parser['database']['private_mongo_db']]

                return cls._client_private

        return None