from config import PREFIX_FILE, PREFIX_MSG, PREFIX_QUIT, PREFIX_REFRESH, PREFIX_REG


def print_options():
    print("Options:")
    print(f"{PREFIX_REG} <nickname>: Register with the server")
    print(f"{PREFIX_MSG} <message>: Send a message to all clients")
    print(f"{PREFIX_MSG} @<nickname> <message>: Send a private message to a client")
    print(f"{PREFIX_REFRESH}: Refresh to check for new messages")
    print(f"{PREFIX_FILE} <file>: Send a file to all clients")
    print(f"{PREFIX_FILE} @<nickname> <file>: Send a file to a client")
    print(f"{PREFIX_QUIT}: Disconnect from the server")
    print()
