"""
AniList Auto Card Importer
Fetches anime characters from AniList API and creates cards automatically
"""

import urllib.request
import urllib.parse
import json
import random
import os
from database import Database

db = Database()

ANILIST_API = "https://graphql.anilist.co"

# GraphQL query to fetch popular anime characters
CHARACTERS_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      hasNextPage
      total
    }
    characters(sort: FAVOURITES_DESC) {
      id
      name {
        full
        native
      }
      image {
        large
        medium
      }
      description
      media(sort: POPULARITY_DESC, perPage: 1) {
        nodes {
          title {
            romaji
            english
          }
          type
        }
      }
      favourites
    }
  }
}
"""

def fetch_anilist_characters(page=1, per_page=50):
    """Fetch characters from AniList API"""
    try:
        variables = {"page": page, "perPage": per_page}
        
        data = json.dumps({
            "query": CHARACTERS_QUERY,
            "variables": variables
        }).encode('utf-8')
        
        req = urllib.request.Request(
            ANILIST_API,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result['data']['Page']
            
    except Exception as e:
        print(f"AniList API error: {e}")
        return None

def determine_rarity(favourites):
    """Determine rarity based on character popularity"""
    if favourites >= 5000:
        return "Mythic"
    elif favourites >= 2000:
        return "Legendary"
    elif favourites >= 1000:
        return "Epic"
    elif favourites >= 500:
        return "Rare"
    elif favourites >= 100:
        return "Uncommon"
    else:
        return "Common"

def import_characters_to_database(max_cards=500):
    """Import characters from AniList and add to database"""
    print("=" * 60)
    print("🎴  AniList Card Importer")
    print("=" * 60)
    print(f"\nFetching {max_cards} anime characters from AniList...")
    print("This may take a few minutes...\n")
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check existing cards to avoid duplicates
    cursor.execute("SELECT name FROM cards")
    existing_names = {row['name'] for row in cursor.fetchall()}
    
    added_count = 0
    skipped_count = 0
    page = 1
    
    while added_count < max_cards:
        print(f"📥  Fetching page {page}...")
        
        result = fetch_anilist_characters(page=page, per_page=50)
        
        if not result or not result['characters']:
            print("No more characters available!")
            break
        
        for char in result['characters']:
            if added_count >= max_cards:
                break
            
            # Get character info
            name = char['name']['full']
            name_jp = char['name'].get('native', '')
            image_url = char['image']['large']
            favourites = char['favourites']
            
            # Get anime/manga series
            if char['media']['nodes']:
                media = char['media']['nodes'][0]
                series = media['title'].get('english') or media['title']['romaji']
                media_type = media['type']
            else:
                series = "Unknown Series"
                media_type = "ANIME"
            
            # Skip if already exists
            if name in existing_names:
                skipped_count += 1
                continue
            
            # Determine rarity based on popularity
            rarity = determine_rarity(favourites)
            
            # Add to database
            try:
                cursor.execute(
                    'INSERT INTO cards (name, series, rarity, image_url) VALUES (?, ?, ?, ?)',
                    (name, series, rarity, image_url)
                )
                conn.commit()
                
                existing_names.add(name)
                added_count += 1
                
                # Print progress
                rarity_emoji = {
                    "Common": "⚪", "Uncommon": "🟢", "Rare": "🔵",
                    "Epic": "🟣", "Legendary": "🟡", "Mythic": "🔴"
                }
                emoji = rarity_emoji.get(rarity, "⚪")
                print(f"  {emoji} {added_count:3d}. {name[:30]:30s} | {series[:20]:20s} | {rarity}")
                
            except Exception as e:
                print(f"  ❌ Error adding {name}: {e}")
                skipped_count += 1
        
        page += 1
        
        # Check if there are more pages
        if not result['pageInfo']['hasNextPage']:
            break
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("📊  Import Complete!")
    print("=" * 60)
    print(f"✅  Added: {added_count} cards")
    print(f"⏭️   Skipped: {skipped_count} cards (duplicates)")
    print(f"💾  Total cards in database: {added_count + len(existing_names) - added_count}")
    print("=" * 60)
    print("\n🎤  Cards are ready to spawn in Discord!")
    print("     Start your bot with: python bot.py")

def show_rarity_distribution():
    """Show how many cards of each rarity were imported"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rarity, COUNT(*) as count 
        FROM cards 
        GROUP BY rarity 
        ORDER BY 
            CASE rarity
                WHEN 'Mythic' THEN 1
                WHEN 'Legendary' THEN 2
                WHEN 'Epic' THEN 3
                WHEN 'Rare' THEN 4
                WHEN 'Uncommon' THEN 5
                WHEN 'Common' THEN 6
            END
    ''')
    
    print("\n📊  Rarity Distribution:")
    print("─" * 40)
    
    rarity_emoji = {
        "Common": "⚪", "Uncommon": "🟢", "Rare": "🔵",
        "Epic": "🟣", "Legendary": "🟡", "Mythic": "🔴"
    }
    
    for row in cursor.fetchall():
        rarity = row['rarity']
        count = row['count']
        emoji = rarity_emoji.get(rarity, "⚪")
        bar = "█" * (count // 5)
        print(f"{emoji} {rarity:10s} │ {count:4d} │ {bar}")
    
    conn.close()

def preview_random_cards(count=5):
    """Preview some random cards from the database"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cards ORDER BY RANDOM() LIMIT ?", (count,))
    cards = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not cards:
        print("\n❌ No cards in database yet!")
        return
    
    print(f"\n🎴  Random Card Preview ({count} cards):")
    print("=" * 60)
    
    for card in cards:
        print(f"\n#{card['id']:04d} | {card['name']}")
        print(f"  📺 {card['series']}")
        print(f"  ⭐ {card['rarity']}")
        print(f"  🖼️  {card['image_url'][:50]}...")

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("🎤  AniList Card Importer for Miku Bot")
    print("=" * 60)
    print("\nOptions:")
    print("1. Import 100 cards (Quick start)")
    print("2. Import 500 cards (Recommended)")
    print("3. Import 1000 cards (Full database)")
    print("4. Preview existing cards")
    print("5. Show rarity distribution")
    print("6. Exit")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == "1":
        import_characters_to_database(100)
        show_rarity_distribution()
        preview_random_cards(5)
    elif choice == "2":
        import_characters_to_database(500)
        show_rarity_distribution()
        preview_random_cards(5)
    elif choice == "3":
        import_characters_to_database(1000)
        show_rarity_distribution()
        preview_random_cards(5)
    elif choice == "4":
        count = int(input("How many cards to preview? (default 10): ") or "10")
        preview_random_cards(count)
    elif choice == "5":
        show_rarity_distribution()
    elif choice == "6":
        print("Bye~! 💚")
    else:
        print("Invalid choice!")
