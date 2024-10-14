from beanie import Document, Indexed


class User(Document):
    username: str = Indexed(str, unique=True)
    hashed_password: str
    is_active: bool = True

    class Settings:
        name = 'users'
