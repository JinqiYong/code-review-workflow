```python
import sqlite3

def create_connection(db_file):
    """ 创建数据库连接 """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn

def login_user(conn, username, password):
    """ 用户登录功能 """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cur.fetchone()

# 创建数据库连接
conn = create_connection("example.db")

# 模拟用户登录
if conn:
    username = input("Enter username: ")
    password = input("Enter password: ")
    user = login_user(conn, username, password)
    if user:
        print("Login successful")
    else:
        print("Login failed")
    conn.close()
```