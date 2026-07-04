import sqlite3

def init_db():
    print("💾 Initializing Database...")
    with sqlite3.connect('lexify.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                font_size TEXT DEFAULT '18',
                font_color TEXT DEFAULT '#333333',
                tts_volume TEXT DEFAULT '1.0',
                tts_speed TEXT DEFAULT '0.9'
            )
        ''')
        conn.commit()
    print("✅ Database Ready!")