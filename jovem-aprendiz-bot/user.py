from database import Collection
from pymongo import MongoClient
from bson.objectid import ObjectId

class User():
    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.collection = MongoClient('localhost', 27017)['telegram_bot']['users']
        self._get_user_data()

    def _get_user_data(self):
        user_data = self.collection.find_one({'telegram_id': self.telegram_id})
        if user_data and ('targets' in user_data):
            self.targets = user_data['targets']
        else:
            self.targets = []

    def _put_user_data(self):
        self.collection.insert_one({'telegram_id':self.telegram_id, 'targets': self.targets})

    def _update_user_data(self):
        db_filter = {'telegram_id': self.telegram_id}
        db_update = {'$set': {'telegram_id': self.telegram_id, 'targets': self.targets}}
        self.collection.update_one(db_filter, db_update, upsert=True)

    def add_target(self, targetType, username):
        if targetType.lower() == 'twitter':
            # Create target object
            newTarget = {
                'targetType': 'twitter',
                'username': 'username',
            }

            # Apend target if user does not have it
            if not newTarget in self.targets:
                self.targets.append(newTarget)
                self._update_user_data()
            else:
                raise Exception('Target already exists')
        else:
            raise Exception('targetType not supported')

    def remove_target(self, targetType, username):
        if targetType.lower() == 'twitter':
            # Create target object
            delTarget = {
                'targetType': 'twitter',
                'username': 'username',
            }

            # Apend target if user does not have it
            if delTarget in self.targets:
                self.targets.remove(delTarget)
                self._update_user_data()
            else:
                raise Exception('Target does not exist in this user')
        else:
            raise Exception('targetType not supported')
