import json
import os

class User:
    def __init__(self, number, name, id):
        self.name = name
        self.number = number
        self.id = id

    def to_dict(self):
        return {
            'name': self.name,
            'number': self.number,
            'id':self.id
        }

class UserDatabase:
    def __init__(self, filename='users.json'):
        self.filename = filename
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_users(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.users, file, ensure_ascii=False, indent=4)

    def add_user(self, user):
        self.users.append(user.to_dict())
        self.save_users()
