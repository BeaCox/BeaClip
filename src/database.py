import sqlite3
from os.path import expanduser, join
from os import makedirs

DB_PATH = join(expanduser("~"), ".beaclip", "clipboard.db")

def init_database():
    # if the database file does not exist, create it
    try:
        config_dir = join(expanduser("~"), ".beaclip")
        makedirs(config_dir, exist_ok=True)
        open(DB_PATH, "a").close()
    except Exception as e:
        print(f"Error creating database: {e}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (text TEXT, timestamp TEXT, tag TEXT)''')
    conn.commit()
    conn.close()

def load_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()
    conn.close()
    return entries

def save_entry(text, timestamp, tag=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE text = ? AND timestamp = ?", (text, timestamp))
    existing_entry = c.fetchone()

    if existing_entry:
        c.execute("UPDATE entries SET tag = ? WHERE text = ? AND timestamp = ?", (tag, text, timestamp))
    else:
        if tag is None:
            c.execute("INSERT INTO entries (text, timestamp) VALUES (?, ?)", (text, timestamp))
        else:
            c.execute("INSERT INTO entries (text, timestamp, tag) VALUES (?, ?, ?)", (text, timestamp, tag))
    
    conn.commit()
    conn.close()

def update_entry(text, timestamp, tag):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE entries SET tag=? WHERE text=? AND timestamp=?", (tag, text, timestamp))
    conn.commit()
    conn.close()

def delete_entry(text, timestamp, tag):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE text=? AND timestamp=?", (text, timestamp))
    conn.commit()
    conn.close()

def clear_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM entries")
    conn.commit()
    conn.close()

def delete_entry_created_before(timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE timestamp < ?", (timestamp,))
    conn.commit()
    conn.close()
