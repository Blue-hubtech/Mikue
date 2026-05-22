"""
Shoob API Card Fetcher
Fetches real Shoob cards from the API and spawns them in Discord
"""

import urllib.request
import json
import random
from database import Database

db = Database()

SHOOB_API_BASE = "https://rjdev-apis-eta.vercel.app/api/cards"

def fetch_shoob_card():
    """Fetch a random card from Shoob API"""
    try:
        url = f"{SHOOB_API_BASE}?mode=spawn"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        if not data.get('status') or not data.get('result'):
            return None
        
        card_data = data['result']
        
        # Parse Shoob card data
        return {
            'shoob_id': card_data.get('id'),
            'name': card_data.get('title'),
            'series': card_data.get('series', 'Unknown Series'),
            'image_url': card_data.get('imageUrl'),
            'tier': card_data.get('tier', 1),
            'claim_code': card_data.get('claim', 'N/A'),
            'price': card_data.get('price', 0),
            'owners_count': len(card_data.get('owners', [])),
            'want_count': card_data.get('wantCount', 0),
            'detail_url': card_data.get('detailUrl', ''),
            'creators': card_data.get('creators', []),
        }
        
    except Exception as e:
        print(f"Shoob API error: {e}")
        return None

def tier_to_rarity(tier):
    """Convert Shoob tier (1-7) to rarity name"""
    tier_map = {
        1: "Common",
        2: "Uncommon",
        3: "Rare",
        4: "Epic",
        5: "Legendary",
        6: "Mythic",
        7: "Mythic"  # Special tier
    }
    return tier_map.get(tier, "Common")

def fetch_shoob_card_by_tier(tier):
    """Fetch a card from Shoob API filtered by specific tier (1-5)"""
    if not isinstance(tier, int) or tier < 1 or tier > 5:
        return None
    
    try:
        url = f"{SHOOB_API_BASE}?mode=spawn&tier={tier}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        if not data.get('status') or not data.get('result'):
            return None
        
        card_data = data['result']
        
        # Parse Shoob card data
        return {
            'shoob_id': card_data.get('id'),
            'name': card_data.get('title'),
            'series': card_data.get('series', 'Unknown Series'),
            'image_url': card_data.get('imageUrl'),
            'tier': card_data.get('tier', tier),
            'claim_code': card_data.get('claim', 'N/A'),
            'price': card_data.get('price', 0),
            'owners_count': len(card_data.get('owners', [])),
            'want_count': card_data.get('wantCount', 0),
            'detail_url': card_data.get('detailUrl', ''),
            'creators': card_data.get('creators', []),
        }
        
    except Exception as e:
        print(f"Shoob API error (tier {tier}): {e}")
        return None

def add_shoob_card_to_database(card_data):
    """Add Shoob card to local database if it doesn't exist"""
    if not card_data:
        return None
    
    # Check if card already exists
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id FROM cards WHERE name=? AND series=?',
        (card_data['name'], card_data['series'])
    )
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return existing['id']
    
    # Add new card
    rarity = tier_to_rarity(card_data['tier'])
    
    cursor.execute(
        'INSERT INTO cards (name, series, rarity, image_url) VALUES (?, ?, ?, ?)',
        (card_data['name'], card_data['series'], rarity, card_data['image_url'])
    )
    conn.commit()
    card_id = cursor.lastrowid
    conn.close()
    
    return card_id

def get_random_shoob_card_for_spawn():
    """Fetch a Shoob card and prepare it for spawning"""
    card_data = fetch_shoob_card()
    
    if not card_data:
        # Fallback to local database if API fails
        return db.get_random_card()
    
    # Add to database
    card_id = add_shoob_card_to_database(card_data)
    
    if not card_id:
        return db.get_random_card()
    
    # Get the card from database
    return db.get_card_by_id(card_id)

def get_shoob_card_by_tier(tier):
    """Fetch a Shoob card for a specific tier and prepare it for spawning"""
    if not isinstance(tier, int) or tier < 1 or tier > 5:
        return None
    
    card_data = fetch_shoob_card_by_tier(tier)
    
    if not card_data:
        # Fallback to local database if API fails
        return db.get_random_card()
    
    # Add to database
    card_id = add_shoob_card_to_database(card_data)
    
    if not card_id:
        return db.get_random_card()
    
    # Get the card from database
    return db.get_card_by_id(card_id)

def import_multiple_shoob_cards(count=100):
    """Import multiple Shoob cards to database"""
    print("=" * 60)
    print("🎴  Shoob Card Importer")
    print("=" * 60)
    print(f"\nImporting {count} cards from Shoob API...")
    print("This may take a few minutes...\n")
    
    added = 0
    skipped = 0
    errors = 0
    
    for i in range(count):
        try:
            card_data = fetch_shoob_card()
            
            if not card_data:
                errors += 1
                continue
            
            card_id = add_shoob_card_to_database(card_data)
            
            if card_id:
                added += 1
                tier_emoji = {1:"⚪",2:"🟢",3:"🔵",4:"🟣",5:"🟡",6:"🔴",7:"🔴"}
                emoji = tier_emoji.get(card_data['tier'], "⚪")
                rarity = tier_to_rarity(card_data['tier'])
                
                print(f"  {emoji} {added:3d}. {card_data['name'][:30]:30s} | {card_data['series'][:20]:20s} | {rarity}")
            else:
                skipped += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊  Import Complete!")
    print("=" * 60)
    print(f"✅  Added: {added} cards")
    print(f"⏭️   Skipped: {skipped} cards (duplicates)")
    print(f"❌  Errors: {errors}")
    print("=" * 60)
    print("\n🎤  Real Shoob cards are ready to spawn!")
    print("     Start your bot with: python bot.py")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎴  Shoob API Card Importer")
    print("=" * 60)
    print("\nOptions:")
    print("1. Test API (fetch 1 card)")
    print("2. Import 50 cards")
    print("3. Import 100 cards")
    print("4. Import 500 cards")
    print("5. Exit")
    
    choice = input("\nChoice (1-5): ").strip()
    
    if choice == "1":
        print("\n🎴  Testing Shoob API...")
        card = fetch_shoob_card()
        if card:
            print("\n✅  API works! Sample card:")
            print(f"  Name: {card['name']}")
            print(f"  Series: {card['series']}")
            print(f"  Tier: {card['tier']} ({tier_to_rarity(card['tier'])})")
            print(f"  Image: {card['image_url'][:50]}...")
            print(f"  Price: {card['price']:,}")
            print(f"  Owners: {card['owners_count']}")
        else:
            print("❌  API test failed!")
    elif choice == "2":
        import_multiple_shoob_cards(50)
    elif choice == "3":
        import_multiple_shoob_cards(100)
    elif choice == "4":
        import_multiple_shoob_cards(500)
    elif choice == "5":
        print("Bye~! 💚")
    else:
        print("Invalid choice!")
