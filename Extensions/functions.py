import sqlite3

class Database():
    def __init__(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        self.connection = connection

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")

db = Database("C:/sqlite/otsu_rewrite.db")

def get_balance(user_id):
    try:
        return float(str(db.execute_read_query(f'SELECT hand_balance FROM Balances WHERE user_id = {user_id}'))[2:-3])
    except ValueError:
        db.execute_query(f"INSERT INTO Balances (user_id, hand_balance, bank_balance) VALUES ({user_id}, {0.}, {0.});")
        return 0

def get_bank_balance(user_id):
    try:
        return float(str(db.execute_read_query(f'SELECT bank_balance FROM Balances WHERE user_id = {user_id}'))[2:-3])
    except ValueError:
        db.execute_query(f'UPDATE Balances SET bank_balance = {0.} WHERE user_id = {user_id}')
        return 0

def update_balance(user_id, change):
    db.execute_query(f'UPDATE Balances SET hand_balance = {get_balance(user_id) + float(change)} WHERE user_id = {user_id}')

def update_bank_balance(user_id, change):
    db.execute_query(f'UPDATE Balances SET bank_balance = {get_bank_balance(user_id) + float(change)} WHERE user_id = {user_id}')



async def invalid_credit_amount(ctx, amount, messages):
    try:
        amount = float(amount)
    except ValueError:
        await ctx.send(messages["NotAFloat"])
        return True

    if round(amount * 100) / 100 != amount:
        await ctx.send(messages["MoreThanTwoDecimals"])
        return True

    if amount <= 0:
        await ctx.send(messages["LessThanOrEqualToZero"])
        return True
    
    return False
