import sqlite3
from datetime import datetime
import random
import json
import os

class Database:
    def __init__(self, db_name='data/cards.db'):
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                series TEXT NOT NULL,
                rarity TEXT NOT NULL,
                image_url TEXT NOT NULL,
                description TEXT DEFAULT 'Anime collectible card',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                stellas INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_daily TIMESTAMP,
                last_weekly TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User collections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                card_id INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_cards ON user_cards(user_id, card_id)')
        
        # User deck table (max 12 cards)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_deck (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                card_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, position),
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                bio TEXT DEFAULT 'No bio set.',
                icon TEXT,
                favorite_card_id INTEGER,
                locked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (favorite_card_id) REFERENCES cards (id)
            )
        ''')

        # Wishlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlists (
                user_id INTEGER NOT NULL,
                card_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, card_id),
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Pokemon table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                data TEXT,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Cooldowns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                expiry TIMESTAMP NOT NULL,
                PRIMARY KEY (user_id, command)
            )
        ''')
        
        # Add description column if missing
        cursor.execute("PRAGMA table_info(cards)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'description' not in columns:
            cursor.execute("ALTER TABLE cards ADD COLUMN description TEXT DEFAULT 'Anime collectible card'")
        
        # Ensure columns in users table exist
        for col, coltype in [("last_weekly","TIMESTAMP"), ("gems","INTEGER DEFAULT 0"), ("xp","INTEGER DEFAULT 0"), ("level","INTEGER DEFAULT 1")]:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {col} {coltype}')
            except:
                pass

        # Ensure columns in profiles table exist
        cursor.execute("PRAGMA table_info(profiles)")
        profile_columns = [col[1] for col in cursor.fetchall()]
        if 'favorite_card_id' not in profile_columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN favorite_card_id INTEGER")
        
        conn.commit()
        conn.close()
    
    # ---------- CARD SYSTEM ----------
    def get_random_card(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        rarity_weights = {
            'Common': 40, 'Uncommon': 30, 'Rare': 15,
            'Epic': 10, 'Legendary': 4, 'Mythic': 1
        }
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        chosen_rarity = random.choices(rarities, weights=weights)[0]
        cursor.execute('SELECT * FROM cards WHERE rarity = ? ORDER BY RANDOM() LIMIT 1', (chosen_rarity,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def add_card_to_user(self, user_id, card_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)', (user_id, card_id))
        conn.commit()
        conn.close()
    
    def get_user_collection(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.series, c.rarity, c.image_url, COUNT(*) as count
            FROM user_cards uc
            JOIN cards c ON uc.card_id = c.id
            WHERE uc.user_id = ?
            GROUP BY c.id
            ORDER BY 
                CASE c.rarity
                    WHEN 'Mythic' THEN 1
                    WHEN 'Legendary' THEN 2
                    WHEN 'Epic' THEN 3
                    WHEN 'Rare' THEN 4
                    WHEN 'Uncommon' THEN 5
                    WHEN 'Common' THEN 6
                END, c.name
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_card_by_id(self, card_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cards WHERE id = ?', (card_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def check_user_owns_card(self, user_id, card_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM user_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    def get_user_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM user_cards WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(DISTINCT card_id) as unique_cards FROM user_cards WHERE user_id = ?', (user_id,))
        unique = cursor.fetchone()['unique_cards']
        cursor.execute('SELECT COUNT(*) as total FROM cards')
        avail = cursor.fetchone()['total']
        completion = (unique / avail * 100) if avail else 0
        conn.close()
        return {'total_cards': total, 'unique_cards': unique, 'completion_percentage': completion}

    def get_recent_cards(self, user_id, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.series, c.rarity, c.image_url, uc.obtained_at
            FROM user_cards uc
            JOIN cards c ON uc.card_id = c.id
            WHERE uc.user_id = ?
            ORDER BY uc.obtained_at DESC, uc.id DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_card_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM cards')
        total = cursor.fetchone()['total']
        cursor.execute('SELECT rarity, COUNT(*) as count FROM cards GROUP BY rarity')
        rarity_counts = {row['rarity']: row['count'] for row in cursor.fetchall()}
        cursor.execute('SELECT COUNT(*) as total FROM user_cards')
        claimed = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(DISTINCT user_id) as collectors FROM user_cards')
        collectors = cursor.fetchone()['collectors']
        conn.close()
        return {
            'total_cards': total,
            'claimed_cards': claimed,
            'collectors': collectors,
            'rarity_counts': rarity_counts
        }
    
    def add_custom_card(self, name, series, rarity, image_url, description=None):
        desc = description or "Anime collectible card"
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cards (name, series, rarity, image_url, description) VALUES (?,?,?,?,?)',
                       (name, series, rarity, image_url, desc))
        card_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return card_id
    
    # ---------- DECK SYSTEM (MOVE, NOT COPY) ----------
    def get_user_deck(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ud.id, ud.position, c.id as card_id, c.name, c.series, c.rarity, c.image_url, c.description
            FROM user_deck ud
            JOIN cards c ON ud.card_id = c.id
            WHERE ud.user_id = ?
            ORDER BY ud.position ASC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        deck = []
        for r in rows:
            d = dict(r)
            d['id'] = d['card_id']
            deck.append(d)
        return deck
    
    def add_to_deck(self, user_id, card_id):
        """Move ONE COPY from collection to deck. Returns (success, message)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if user owns at least one copy
        cursor.execute('SELECT COUNT(*) as count FROM user_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        owned = cursor.fetchone()['count']
        if owned == 0:
            conn.close()
            return False, "You don't own this card!"
        
        # Check deck size
        cursor.execute('SELECT COUNT(*) as count FROM user_deck WHERE user_id = ?', (user_id,))
        deck_count = cursor.fetchone()['count']
        if deck_count >= 12:
            conn.close()
            return False, "Your deck is full! Max 12 cards."
        
        # Remove ONE copy from user_cards
        cursor.execute(
            '''
            DELETE FROM user_cards
            WHERE id = (
                SELECT id FROM user_cards
                WHERE user_id = ? AND card_id = ?
                LIMIT 1
            )
            ''',
            (user_id, card_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            return False, "Failed to remove card from collection."
        
        # Add to deck at next available position
        position = deck_count + 1
        cursor.execute('INSERT INTO user_deck (user_id, card_id, position) VALUES (?, ?, ?)',
                       (user_id, card_id, position))
        conn.commit()
        conn.close()
        return True, f"Moved to deck position {position} (removed from collection)."
    
    def remove_from_deck(self, user_id, position):
        """Move a card from deck back to collection. Returns True if successful."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT card_id FROM user_deck WHERE user_id = ? AND position = ?', (user_id, position))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        card_id = row['card_id']
        
        # Remove from deck
        cursor.execute('DELETE FROM user_deck WHERE user_id = ? AND position = ?', (user_id, position))
        
        # Add back to user_cards
        cursor.execute('INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)', (user_id, card_id))
        
        # Reorder remaining deck positions
        cursor.execute('SELECT id, position FROM user_deck WHERE user_id = ? ORDER BY position ASC', (user_id,))
        remaining = cursor.fetchall()
        new_pos = 1
        for r in remaining:
            cursor.execute('UPDATE user_deck SET position = ? WHERE id = ?', (new_pos, r['id']))
            new_pos += 1
        
        conn.commit()
        conn.close()
        return True
    
    def transfer_all_to_collection(self, user_id):
        """Move ALL cards from deck back to collection. Returns number of cards moved."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT card_id FROM user_deck WHERE user_id = ?', (user_id,))
        deck_cards = cursor.fetchall()
        count = len(deck_cards)
        if count == 0:
            conn.close()
            return 0
        
        for row in deck_cards:
            cursor.execute('INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)', (user_id, row['card_id']))
        cursor.execute('DELETE FROM user_deck WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return count
    
    # ---------- ECONOMY (unchanged from your original, but keep all) ----------
    def get_user_stellas(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT stellas FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row['stellas']
        self.create_user(user_id)
        return 100
    
    def create_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, stellas) VALUES (?, 100)', (user_id,))
        conn.commit()
        conn.close()
    
    def add_stellas(self, user_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        self.create_user(user_id)
        cursor.execute('UPDATE users SET stellas = stellas + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
    
    def remove_stellas(self, user_id, amount):
        if self.get_user_stellas(user_id) < amount:
            return False
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET stellas = stellas - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
        return True
    
    def transfer_stellas(self, from_id, to_id, amount):
        if self.remove_stellas(from_id, amount):
            self.add_stellas(to_id, amount)
            return True
        return False
    
    def claim_daily(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        self.create_user(user_id)
        cursor.execute('SELECT last_daily FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        now = datetime.now()
        if row and row['last_daily']:
            last = datetime.fromisoformat(row['last_daily'])
            if (now - last).total_seconds() < 86400:
                hours = 24 - (now - last).total_seconds() / 3600
                conn.close()
                return False, 0, hours
        reward_min = int(self.get_config('daily_min', 50))
        reward_max = int(self.get_config('daily_max', 150))
        reward = random.randint(min(reward_min, reward_max), max(reward_min, reward_max))
        cursor.execute('UPDATE users SET stellas = stellas + ?, last_daily = ? WHERE user_id = ?',
                       (reward, now.isoformat(), user_id))
        conn.commit()
        conn.close()
        return True, reward, 24
    
    def claim_weekly(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        self.create_user(user_id)
        cursor.execute('SELECT last_weekly FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        now = datetime.now()
        if row and row['last_weekly']:
            last = datetime.fromisoformat(row['last_weekly'])
            if (now - last).total_seconds() < 604800:
                hours = 168 - (now - last).total_seconds() / 3600
                conn.close()
                return False, 0, hours
        reward_min = int(self.get_config('weekly_min', 300))
        reward_max = int(self.get_config('weekly_max', 700))
        reward = random.randint(min(reward_min, reward_max), max(reward_min, reward_max))
        cursor.execute('UPDATE users SET stellas = stellas + ?, last_weekly = ? WHERE user_id = ?',
                       (reward, now.isoformat(), user_id))
        conn.commit()
        conn.close()
        return True, reward, 168
    
    def get_user_gems(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT gems FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['gems'] if row else 0
    
    def add_gems(self, user_id, amount):
        self.create_user(user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET gems = COALESCE(gems,0) + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
    
    # ---------- PROFILE ----------
    def get_profile(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def update_profile(self, user_id, field, value):
        allowed_fields = {'username', 'bio', 'icon', 'locked', 'favorite_card_id'}
        if field not in allowed_fields:
            raise ValueError(f"Invalid profile field: {field}")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO profiles (user_id) VALUES (?)', (user_id,))
        cursor.execute(f'UPDATE profiles SET {field} = ? WHERE user_id = ?', (value, user_id))
        conn.commit()
        conn.close()

    def set_favorite_card(self, user_id, card_id):
        self.update_profile(user_id, 'favorite_card_id', card_id)

    def get_favorite_card(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*
            FROM profiles p
            JOIN cards c ON p.favorite_card_id = c.id
            WHERE p.user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ---------- XP ----------
    def get_user_xp(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['xp'] if row else 0
    
    def add_xp(self, user_id, amount=10):
        self.create_user(user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET xp = xp + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
        return self.check_level_up(user_id)
    
    def check_level_up(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'level_up': False}
        xp, level = row['xp'], row['level']
        needed = 1000 + (level - 1) * 2000
        if xp >= needed and level < 100:
            new_level = level + 1
            reward = 100 + new_level * 10
            cursor.execute('UPDATE users SET level = ?, stellas = stellas + ? WHERE user_id = ?',
                           (new_level, reward, user_id))
            conn.commit()
            conn.close()
            return {'level_up': True, 'new_level': new_level, 'reward': reward}
        conn.close()
        return {'level_up': False}
    
    def get_user_level(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT level FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['level'] if row else 1

    def get_level_info(self, user_id):
        self.create_user(user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return {'xp': row['xp'], 'level': row['level']} if row else {'xp': 0, 'level': 1}

    # ---------- WISHLIST ----------
    def add_to_wishlist(self, user_id, card_id):
        if not self.get_card_by_id(card_id):
            return False, "Card not found."
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO wishlists (user_id, card_id) VALUES (?, ?)', (user_id, card_id))
        added = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return added, "Added to wishlist." if added else "That card is already on your wishlist."

    def remove_from_wishlist(self, user_id, card_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wishlists WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        removed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return removed

    def get_wishlist(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.series, c.rarity, c.image_url, w.created_at
            FROM wishlists w
            JOIN cards c ON w.card_id = c.id
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ---------- LEADERBOARDS ----------
    def get_leaderboard(self, category='stellas', limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        if category == 'cards':
            cursor.execute('''
                SELECT user_id, COUNT(*) as score
                FROM user_cards
                GROUP BY user_id
                ORDER BY score DESC
                LIMIT ?
            ''', (limit,))
        elif category == 'unique':
            cursor.execute('''
                SELECT user_id, COUNT(DISTINCT card_id) as score
                FROM user_cards
                GROUP BY user_id
                ORDER BY score DESC
                LIMIT ?
            ''', (limit,))
        elif category == 'xp':
            cursor.execute('SELECT user_id, xp as score FROM users ORDER BY xp DESC LIMIT ?', (limit,))
        else:
            cursor.execute('SELECT user_id, stellas as score FROM users ORDER BY stellas DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ---------- COOLDOWNS ----------
    def set_cooldown(self, user_id, command, seconds):
        from datetime import datetime, timedelta
        expiry = (datetime.now() + timedelta(seconds=seconds)).isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO cooldowns (user_id, command, expiry) VALUES (?, ?, ?)',
                       (user_id, command, expiry))
        conn.commit()
        conn.close()
    
    def get_cooldown(self, user_id, command):
        from datetime import datetime
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT expiry FROM cooldowns WHERE user_id = ? AND command = ?', (user_id, command))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return 0
        expiry = datetime.fromisoformat(row['expiry'])
        now = datetime.now()
        if expiry > now:
            return int((expiry - now).total_seconds())
        else:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cooldowns WHERE user_id = ? AND command = ?', (user_id, command))
            conn.commit()
            conn.close()
            return 0
    
    def get_all_cooldowns(self, user_id):
        from datetime import datetime
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT command, expiry FROM cooldowns WHERE user_id = ? AND expiry > ?',
                       (user_id, datetime.now().isoformat()))
        rows = cursor.fetchall()
        conn.close()
        result = {}
        for row in rows:
            seconds = int((datetime.fromisoformat(row['expiry']) - datetime.now()).total_seconds())
            if seconds > 0:
                result[row['command']] = seconds
        return result
    
    # ---------- POKEMON ----------
    def add_pokemon_to_user(self, user_id, name, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_pokemon (user_id, name, data) VALUES (?, ?, ?)',
                       (user_id, name, json.dumps(data)))
        conn.commit()
        conn.close()
    
    def get_user_pokemon(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_pokemon WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            d = dict(row)
            try:
                d['data'] = json.loads(d.get('data', '{}'))
            except:
                d['data'] = {}
            result.append(d)
        return result
    
    # ---------- CONFIG ----------
    def set_config(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, str(value)))
        conn.commit()
        conn.close()
    
    def get_config(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default
    
    def enable_casino_channel(self, channel_id):
        self.set_config(f'casino_channel_{channel_id}', 'true')
    
    def disable_casino_channel(self, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM config WHERE key = ?', (f'casino_channel_{channel_id}',))
        conn.commit()
        conn.close()
    
    def is_casino_enabled(self, channel_id):
        return self.get_config(f'casino_channel_{channel_id}') is not None
    
    def get_casino_channels(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key FROM config WHERE key LIKE ?', ('casino_channel_%',))
        rows = cursor.fetchall()
        conn.close()
        return [int(row['key'].replace('casino_channel_', '')) for row in rows]
