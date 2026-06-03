users = []

def register_user(username, password):
    user = {
        "username": username,
        "password": password
    }

    users.append(user)


def login(username, password):
    for user in users:
        if user["username"] == username and user["password"] == password:
            print("Login successful!")
            return True

    return False