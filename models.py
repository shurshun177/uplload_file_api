from peewee import (
    Model, CharField, ForeignKeyField, AutoField,
    CompositeKey, SqliteDatabase
)


db = SqliteDatabase('my_db.db')


class BaseModel(Model):
    pass


class User(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True)

    class Meta:
        database = db
        db_table = 'users'


class File(Model):
    file_name = CharField(max_length=30)
    user_name = ForeignKeyField(User, field=User.name, backref='files')

    class Meta:
        database = db
        db_table = 'files'
        primary_key = CompositeKey(
            'file_name',
            'user_name'
        )


if __name__ == '__main__':
    with db:
        db.create_tables([User, File])

        users = [
            {'name': 'Artur'},
            {'name': 'Feliks'}
        ]
        User.insert_many(users).execute()

        files = [
            {'file_name': 'test_1.xlsx', 'user_name': 'Artur'},
            {'file_name': 'test_2.xlsx', 'user_name': 'Artur'},
            {'file_name': 'test_1.xlsx', 'user_name': 'Feliks'}
        ]
        File.insert_many(files).execute()