import bcrypt
from databse import get_connection

def login(userid, password):
    conn = get_connection()      
    cursor = conn.cursor()       
    cursor.execute("SELECT password FROM users WHERE user_id = %s", (userid,))
    result = cursor.fetchone()
    if result:
        stored = result[0]
        if isinstance(stored, str):
            stored = stored.encode()
        if bcrypt.checkpw(password.encode(), stored):
            print("Login successful!")
            conn.close()
            cursor.close()
            return True
    print("Invalid userid or password.")
    cursor.close()
    conn.close()
    return False

def sign_up(name, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)", (name, hashed, 100000.0))
    conn.commit()
    userid = cursor.lastrowid
    print("Sign-up successful! Your user ID is:", userid)
    cursor.close()
    conn.close()
    return userid

def reset_password(userid, username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND username = %s",
        (userid, username)
    )
    result = cursor.fetchone()
    if not result:
        print("No account found with that userid and username.")
        cursor.close()
        conn.close()
        return False
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    cursor.execute(
        "UPDATE users SET password = %s WHERE user_id = %s",
        (hashed, userid)
    )
    conn.commit()
    print("Password reset successful!")
    cursor.close()
    conn.close()
    return True