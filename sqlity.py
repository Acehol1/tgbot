import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('chat_db.db')
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS profile(user_id TEXT PRIMARY KEY, model TEXT, prompt TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS history(user_id TEXT, role TEXT, content TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS cash_acc(user_id TEXT, usage REAL, cash REAL)')

async def get_profile(id,name_table):
    cur.execute(f"SELECT * FROM {name_table} WHERE user_id = ?", (id,))
    return cur.fetchone()

async def insert_prof(user_id: object, model: object, prompt: object, name_table: object) -> object:
    cur.execute(f"INSERT INTO {name_table} VALUES (?, ?, ?)", (user_id, model, prompt))
    db.commit()

async def insert_his(user_id, role, content):
    cur.execute("INSERT INTO history VALUES (?, ?, ?)", (user_id, role, content))
    db.commit()

async def del_prof(id):
    cur.execute("DELETE FROM profile WHERE user_id = ?", (id,))
    cur.execute("DELETE FROM history WHERE user_id = ?", (id,))
    db.commit()

async def get_sm(value, output, table, param):
    cur.execute(f"SELECT {output} FROM {table} WHERE {param} = ?", (value,))
    result = cur.fetchall()
    if result:
        return result
    return None
async def get_prompt(value):
    cur.execute(f"SELECT content, role FROM prompt WHERE name = ?", (value,))
    result = cur.fetchall()
    if result:
        return result
    return None
async def get_content(id):
    cur.execute(f"SELECT role , content FROM history WHERE user_id = ?", (id,))
    return cur.fetchall()

async def update_usage(id, amount):
    cur.execute(f"UPDATE cash_acc set usage =  {amount} where user_id = ?",(id,))
