# ── Ranking System ──────────────────────────────────────────────────────────
RANK_TITLES = {
    1: "🌱 Beginner",
    5: "📚 Apprentice",
    10: "⚡ Adept",
    15: "💎 Expert",
    20: "👑 Master",
    25: "🔥 Prodigy",
    30: "⭐ Legend",
    40: "🌟 Mythic",
    50: "💫 Divine",
    60: "🎭 Celestial",
    70: "🏆 Eternal",
    80: "👸 Sovereign",
    90: "💰 Tyrant",
    100: "🎪 Grandmaster"
}

def get_rank_title(level):
    """Get the rank title for a given level"""
    # Find the closest rank title for this level
    titles = sorted(RANK_TITLES.keys(), reverse=True)
    for rank_level in titles:
        if level >= rank_level:
            return RANK_TITLES[rank_level]
    return "🌱 Beginner"

def get_xp_for_level(level):
    """Get total XP required to reach a level"""
    if level <= 1:
        return 0
    return 1000 + (level - 2) * 2000

def get_next_level_xp(level):
    """Get XP required to reach next level"""
    if level >= 100:
        return 0
    return 1000 + (level - 1) * 2000

def format_progress_bar(current_xp, target_xp, length=10):
    """Create a progress bar for XP"""
    if target_xp == 0:
        return "█" * length
    percent = min(current_xp / target_xp, 1.0)
    filled = int(percent * length)
    return "█" * filled + "░" * (length - filled)

def get_level_from_xp(total_xp):
    """Calculate level from total XP"""
    level = 1
    current_threshold = 1000
    xp_used = 0
    
    while level < 100 and xp_used + current_threshold <= total_xp:
        xp_used += current_threshold
        level += 1
        current_threshold = 1000 + (level - 1) * 2000
    
    return level
