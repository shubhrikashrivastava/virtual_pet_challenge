import sqlite3
from datetime import datetime

# -------------------------
# Database Setup
# -------------------------
conn = sqlite3.connect("pets.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
)
""")

# Pets table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hunger REAL DEFAULT 50,
    happiness REAL DEFAULT 50,
    energy REAL DEFAULT 50,
    last_updated TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Pet history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pet_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER,
    action TEXT,
    timestamp TEXT,
    FOREIGN KEY(pet_id) REFERENCES pets(id)
)
""")

conn.commit()

# -------------------------
# Helper Functions
# -------------------------

def get_pet(pet_id):
    cursor.execute("SELECT * FROM pets WHERE id=?", (pet_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "hunger": row[2],
            "happiness": row[3],
            "energy": row[4],
            "last_updated": datetime.fromisoformat(row[5]) if row[5] else datetime.utcnow(),
            "user_id": row[6]
        }
    return None

def update_pet(pet):
    cursor.execute("""
        UPDATE pets SET hunger=?, happiness=?, energy=?, last_updated=? WHERE id=?
    """, (pet["hunger"], pet["happiness"], pet["energy"], pet["last_updated"].isoformat(), pet["id"]))
    conn.commit()

def log_history(pet_id, action):
    cursor.execute("""
        INSERT INTO pet_history (pet_id, action, timestamp) VALUES (?, ?, ?)
    """, (pet_id, action, datetime.utcnow().isoformat()))
    conn.commit()

# -------------------------
# Pet Actions
# -------------------------

def feed_pet(pet):
    pet["hunger"] = max(pet["hunger"] - 30, 0)
    pet["energy"] = min(pet["energy"] + 10, 100)
    pet["last_updated"] = datetime.utcnow()
    update_pet(pet)
    log_history(pet["id"], "Fed the pet")

def play_pet(pet):
    pet["happiness"] = min(pet["happiness"] + 25, 100)
    pet["energy"] = max(pet["energy"] - 15, 0)
    pet["hunger"] = min(pet["hunger"] + 10, 100)
    pet["last_updated"] = datetime.utcnow()
    update_pet(pet)
    log_history(pet["id"], "Played with the pet")

def train_pet(pet):
    pet["energy"] = max(pet["energy"] - 20, 0)
    pet["happiness"] = max(pet["happiness"] - 5, 0)
    pet["last_updated"] = datetime.utcnow()
    update_pet(pet)
    log_history(pet["id"], "Trained the pet")

def self_destructive(pet):
    pet["happiness"] = max(pet["happiness"] - 20, 0)
    pet["energy"] = max(pet["energy"] - 10, 0)
    pet["last_updated"] = datetime.utcnow()
    update_pet(pet)
    log_history(pet["id"], "Pet acted self-destructive")

def decay_stats(pet):
    now = datetime.utcnow()
    elapsed = (now - pet["last_updated"]).total_seconds() / 60  # minutes

    pet["hunger"] = min(pet["hunger"] + elapsed * 0.5, 100)
    pet["happiness"] = max(pet["happiness"] - elapsed * 0.2, 0)
    pet["energy"] = max(pet["energy"] - elapsed * 0.3, 0)

    pet["last_updated"] = now
    update_pet(pet)
    log_history(pet["id"], "Stats decayed over time")

# -------------------------
# Example Usage
# -------------------------

# Add a user if none exists
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO users (username) VALUES (?)", ("player1",))
    conn.commit()

# Get user_id
cursor.execute("SELECT id FROM users WHERE username=?", ("player1",))
user_id = cursor.fetchone()[0]

# Add a pet if none exists
cursor.execute("SELECT COUNT(*) FROM pets")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO pets (name, last_updated, user_id) VALUES (?, ?, ?)",
                   ("Fluffy", datetime.utcnow().isoformat(), user_id))
    conn.commit()

# Get the pet
pet = get_pet(1)
print("Before decay:", pet)

# Apply decay
decay_stats(pet)
print("After decay:", get_pet(1))

# Feed the pet
feed_pet(pet)
print("After feeding:", get_pet(1))

# Make pet self-destructive
self_destructive(pet)
print("After self-destructive act:", get_pet(1))

# Show pet history
cursor.execute("SELECT action, timestamp FROM pet_history WHERE pet_id=?", (1,))
print("History:", cursor.fetchall())
