import discord
import random
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_embed(title: str, description: str, color: int = 0x7289DA, thumbnail_url: str = None) -> discord.Embed:
    """Create a standardized embed with enhanced styling."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    return embed

def create_advanced_embed(title: str, description: str, color: int = 0x7289DA, 
                         embed_type: str = "info") -> discord.Embed:
    """Create an advanced embed with type-specific styling."""

    # Type-specific styling
    type_configs = {
        "success": {"color": 0x00ff00, "emoji": "✅"},
        "error": {"color": 0xff0000, "emoji": "❌"},
        "warning": {"color": 0xffff00, "emoji": "⚠️"},
        "info": {"color": 0x0099ff, "emoji": "ℹ️"},
        "battle": {"color": 0xff6600, "emoji": "⚔️"},
        "shop": {"color": 0x9932cc, "emoji": "🛍️"},
        "rpg": {"color": 0xffd700, "emoji": "🎮"}
    }

    config = type_configs.get(embed_type, type_configs["info"])

    embed = discord.Embed(
        title=f"{config['emoji']} {title}",
        description=description,
        color=config['color'],
        timestamp=datetime.utcnow()
    )

    return embed

def create_progress_bar(percentage: float, length: int = 10, fill_char: str = "█", 
                       empty_char: str = "░") -> str:
    """Create a visual progress bar."""
    filled = int(length * percentage / 100)
    empty = length - filled

    # Color coding based on percentage
    if percentage > 70:
        bar_color = "🟢"  # Green
    elif percentage > 30:
        bar_color = "🟡"  # Yellow
    else:
        bar_color = "🔴"  # Red

    bar = fill_char * filled + empty_char * empty
    return f"{bar_color} {bar} {percentage:.1f}%"

def create_stat_display(stats: Dict[str, Any], title: str = "Stats") -> str:
    """Create a formatted stat display."""
    stat_lines = []

    stat_emojis = {
        "level": "📊",
        "hp": "❤️",
        "max_hp": "💗",
        "attack": "⚔️",
        "defense": "🛡️",
        "mana": "💙",
        "max_mana": "💫",
        "coins": "💰",
        "xp": "✨",
        "luck": "🍀",
        "energy": "⚡"
    }

    for stat_name, value in stats.items():
        emoji = stat_emojis.get(stat_name, "▪️")
        formatted_name = stat_name.replace("_", " ").title()

        if isinstance(value, (int, float)):
            if stat_name == "coins":
                stat_lines.append(f"{emoji} **{formatted_name}:** {format_number(value)}")
            else:
                stat_lines.append(f"{emoji} **{formatted_name}:** {value}")
        else:
            stat_lines.append(f"{emoji} **{formatted_name}:** {value}")

    return "\n".join(stat_lines)

def create_battle_status_display(player_data: Dict[str, Any], enemy_data: Dict[str, Any]) -> str:
    """Create a formatted battle status display."""
    player_hp = player_data.get('hp', 100)
    player_max_hp = player_data.get('max_hp', 100)
    enemy_hp = enemy_data.get('hp', 100)
    enemy_max_hp = enemy_data.get('max_hp', 100)

    player_hp_bar = create_progress_bar((player_hp / player_max_hp) * 100)
    enemy_hp_bar = create_progress_bar((enemy_hp / enemy_max_hp) * 100)

    return f"""
**🧑‍⚔️ You**
{player_hp_bar}
HP: {player_hp}/{player_max_hp}
ATK: {player_data.get('attack', 10)} | DEF: {player_data.get('defense', 5)}

**👹 {enemy_data.get('name', 'Enemy')}**
{enemy_hp_bar}
HP: {enemy_hp}/{enemy_max_hp}
ATK: {enemy_data.get('attack', 10)} | DEF: {enemy_data.get('defense', 5)}
"""

def format_number(number: Union[int, float]) -> str:
    """Format large numbers with appropriate suffixes."""
    if number >= 1_000_000_000:
        return f"{number/1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return str(int(number))

def create_inventory_display(inventory: List[str], equipped: Dict[str, str] = None) -> str:
    """Create a formatted inventory display."""
    if not inventory:
        return "🎒 **Empty inventory**\n*Go shopping or complete adventures to get items!*"

    # Group items by type
    item_groups = {}
    for item in inventory:
        # Simple categorization - you can expand this
        if any(weapon in item.lower() for weapon in ['sword', 'axe', 'staff', 'blade']):
            category = "⚔️ Weapons"
        elif any(armor in item.lower() for armor in ['armor', 'shield', 'helmet', 'boots']):
            category = "🛡️ Armor"
        elif any(consumable in item.lower() for consumable in ['potion', 'food', 'scroll']):
            category = "🧪 Consumables"
        else:
            category = "📦 Other Items"

        if category not in item_groups:
            item_groups[category] = []
        item_groups[category].append(item)

    display_lines = []
    for category, items in item_groups.items():
        display_lines.append(f"\n**{category}**")
        for item in items[:5]:  # Show first 5 items per category
            equipped_marker = " ⚡" if equipped and item in equipped.values() else ""
            display_lines.append(f"• {item}{equipped_marker}")
        if len(items) > 5:
            display_lines.append(f"• ... and {len(items) - 5} more")

    return "\n".join(display_lines)

def create_leaderboard_display(leaderboard_data: List[Dict[str, Any]], 
                              title: str = "Leaderboard") -> discord.Embed:
    """Create a formatted leaderboard display."""
    embed = discord.Embed(
        title=f"🏆 {title}",
        color=0xffd700,
        timestamp=datetime.utcnow()
    )

    if not leaderboard_data:
        embed.description = "No data available yet!"
        return embed

    # Medal emojis for top 3
    medals = ["🥇", "🥈", "🥉"]

    leaderboard_text = ""
    for i, entry in enumerate(leaderboard_data[:10]):  # Top 10
        position = i + 1
        medal = medals[i] if i < 3 else f"{position}."

        username = entry.get('username', 'Unknown')
        value = entry.get('value', 0)

        # Format value based on type
        if isinstance(value, (int, float)):
            if 'coins' in title.lower():
                formatted_value = format_number(value)
            else:
                formatted_value = str(value)
        else:
            formatted_value = str(value)

        leaderboard_text += f"{medal} **{username}** - {formatted_value}\n"

    embed.description = leaderboard_text
    embed.set_footer(text=f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    return embed

def create_shop_item_display(item_data: Dict[str, Any], user_coins: int = 0) -> discord.Embed:
    """Create a detailed shop item display."""
    from utils.constants import RARITY_COLORS

    name = item_data.get('name', 'Unknown Item')
    description = item_data.get('description', 'No description available.')
    price = item_data.get('price', 0)
    rarity = item_data.get('rarity', 'common')

    color = RARITY_COLORS.get(rarity, 0x808080)

    embed = discord.Embed(
        title=f"🛍️ {name}",
        description=description,
        color=color
    )

    # Stats display
    stats = []
    if item_data.get('attack'):
        stats.append(f"⚔️ Attack: +{item_data['attack']}")
    if item_data.get('defense'):
        stats.append(f"🛡️ Defense: +{item_data['defense']}")
    if item_data.get('hp'):
        stats.append(f"❤️ HP: +{item_data['hp']}")
    if item_data.get('mana'):
        stats.append(f"💙 Mana: +{item_data['mana']}")

    if stats:
        embed.add_field(
            name="📊 Stats",
            value="\n".join(stats),
            inline=True
        )

    # Price and affordability
    can_afford = user_coins >= price
    afford_text = "✅ You can afford this!" if can_afford else f"❌ Need {format_number(price - user_coins)} more coins"

    embed.add_field(
        name="💰 Price",
        value=f"{format_number(price)} coins\n{afford_text}",
        inline=True
    )

    # Rarity indicator
    rarity_emojis = {
        'common': '⚪',
        'uncommon': '🟢',
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟠',
        'mythic': '🔴'
    }

    rarity_emoji = rarity_emojis.get(rarity, '⚪')
    embed.add_field(
        name="✨ Rarity",
        value=f"{rarity_emoji} {rarity.title()}",
        inline=True
    )

    return embed

def calculate_battle_damage(attacker_stats: Dict[str, Any], defender_stats: Dict[str, Any]) -> int:
    """Calculate damage in battle."""
    attack = attacker_stats.get('attack', 10)
    defense = defender_stats.get('defense', 5)

    # Base damage calculation
    base_damage = max(1, attack - defense)

    # Add some randomness (80% - 120% of base damage)
    damage_multiplier = random.uniform(0.8, 1.2)
    final_damage = int(base_damage * damage_multiplier)

    return max(1, final_damage)

def generate_random_stats() -> Dict[str, int]:
    """Generate random stats for monsters/items."""
    return {
        'hp': random.randint(50, 150),
        'attack': random.randint(8, 20),
        'defense': random.randint(3, 12)
    }

def format_time_remaining(seconds):
    """Format time remaining in a readable format."""
    if seconds <= 0:
        return "Ready!"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def create_animated_embed(title: str, description: str, color: int = 0x7289DA) -> discord.Embed:
    """Create an embed with animated elements."""
    # Add loading bars or spinning elements
    animations = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner = random.choice(animations)

    embed = discord.Embed(
        title=f"{spinner} {title}",
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )

    return embed

def create_quest_display(quest_data: Dict[str, Any]) -> str:
    """Create a formatted quest display."""
    title = quest_data.get('title', 'Unknown Quest')
    description = quest_data.get('description', 'No description')
    progress = quest_data.get('progress', 0)
    target = quest_data.get('target', 1)
    reward = quest_data.get('reward', {})

    progress_bar = create_progress_bar((progress / target) * 100)

    quest_text = f"**📜 {title}**\n"
    quest_text += f"{description}\n\n"
    quest_text += f"**Progress:** {progress}/{target}\n"
    quest_text += f"{progress_bar}\n\n"

    if reward:
        quest_text += "**Rewards:**\n"
        for reward_type, amount in reward.items():
            emoji = "💰" if reward_type == "coins" else "✨" if reward_type == "xp" else "🎁"
            quest_text += f"{emoji} {reward_type.title()}: {format_number(amount)}\n"

    return quest_text

async def send_paginated_embed(ctx, embeds: List[discord.Embed], timeout: int = 60):
    """Send a paginated embed with navigation."""
    if not embeds:
        return

    current_page = 0
    message = await ctx.send(embed=embeds[current_page])

    if len(embeds) == 1:
        return

    # Add navigation reactions
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("❌")

    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["⬅️", "➡️", "❌"] and 
                reaction.message.id == message.id)

    while True:
        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)

            if str(reaction.emoji) == "⬅️":
                current_page = (current_page - 1) % len(embeds)
            elif str(reaction.emoji) == "➡️":
                current_page = (current_page + 1) % len(embeds)
            elif str(reaction.emoji) == "❌":
                await message.delete()
                return

            await message.edit(embed=embeds[current_page])
            await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

def get_random_work_job() -> Dict[str, Any]:
    """Get a random work job with Plagg theme."""
    jobs = [
        {"name": "Cheese Mining", "min_coins": 50, "max_coins": 100, "min_xp": 5, "max_xp": 15},
        {"name": "Kwami Farming", "min_coins": 30, "max_coins": 80, "min_xp": 3, "max_xp": 10},
        {"name": "Miraculous Trading", "min_coins": 70, "max_coins": 120, "min_xp": 8, "max_xp": 20},
        {"name": "Cheese Crafting", "min_coins": 60, "max_coins": 110, "min_xp": 6, "max_xp": 18},
        {"name": "Kwami Watching", "min_coins": 40, "max_coins": 90, "min_xp": 4, "max_xp": 12},
        {"name": "Camembert Aging", "min_coins": 80, "max_coins": 130, "min_xp": 10, "max_xp": 25}
    ]
    return random.choice(jobs)

def get_random_adventure_outcome() -> Dict[str, Any]:
    """Get a random adventure outcome."""
    outcomes = [
        {
            "description": "You discovered a hidden treasure chest!",
            "coins": (100, 300),
            "xp": (50, 100),
            "items": ["Health Potion", "Mana Potion", "Ancient Coin"]
        },
        {
            "description": "You helped a lost traveler and received a reward!",
            "coins": (80, 200),
            "xp": (30, 70),
            "items": ["Traveler's Map", "Lucky Charm", "Bread"]
        },
        {
            "description": "You found rare materials while exploring!",
            "coins": (60, 150),
            "xp": (40, 80),
            "items": ["Iron Ore", "Mystic Crystal", "Healing Herbs"]
        },
        {
            "description": "You completed a mysterious quest!",
            "coins": (120, 250),
            "xp": (60, 120),
            "items": ["Quest Scroll", "Magic Ring", "Gold Coin"]
        }
    ]

    return random.choice(outcomes)

def level_up_player(player_data: Dict[str, Any]) -> Optional[str]:
    """Check if player levels up and apply bonuses."""
    current_level = player_data.get('level', 1)
    current_xp = player_data.get('xp', 0)
    max_xp = player_data.get('max_xp', 100)

    if current_xp >= max_xp:
        # Level up!
        new_level = current_level + 1

        # Calculate new max XP (exponential growth)
        new_max_xp = int(max_xp * 1.5)

        # Apply stat bonuses
        hp_bonus = random.randint(15, 25)
        attack_bonus = random.randint(3, 7)
        defense_bonus = random.randint(2, 5)
        coin_bonus = new_level * 50

        player_data['level'] = new_level
        player_data['xp'] = current_xp - max_xp  # Carry over excess XP
        player_data['max_xp'] = new_max_xp
        player_data['max_hp'] = player_data.get('max_hp', 100) + hp_bonus
        player_data['hp'] = player_data['max_hp']  # Full heal on level up
        player_data['attack'] = player_data.get('attack', 10) + attack_bonus
        player_data['defense'] = player_data.get('defense', 5) + defense_bonus
        player_data['coins'] = player_data.get('coins', 0) + coin_bonus

        return (f"Level {new_level}! "
                f"HP +{hp_bonus}, ATK +{attack_bonus}, DEF +{defense_bonus}, "
                f"Coins +{coin_bonus}")

    return None

def check_weapon_unlock_conditions(user_id: str, weapon_name: str) -> tuple[bool, str]:
    """Check if user meets weapon unlock conditions."""
    from utils.constants import WEAPON_UNLOCK_CONDITIONS
    from utils.database import get_user_rpg_data

    if weapon_name not in WEAPON_UNLOCK_CONDITIONS:
        return True, "No special conditions required"

    player_data = get_user_rpg_data(user_id)
    if not player_data:
        return False, "Player data not found"

    conditions = WEAPON_UNLOCK_CONDITIONS[weapon_name]["requirements"]
    failed_conditions = []

    for condition in conditions:
        if condition["type"] == "boss_defeat":
            boss_defeats = player_data.get("boss_defeats", {})
            if condition["boss"] not in boss_defeats:
                failed_conditions.append(f"Must defeat {condition['boss']}")
            elif condition.get("min_level") and player_data.get("level", 1) < condition["min_level"]:
                failed_conditions.append(f"Must be level {condition['min_level']} or higher")

        elif condition["type"] == "class_unlock":
            if player_data.get("player_class") != condition["class"]:
                failed_conditions.append(f"Must be {condition['class']} class")

        elif condition["type"] == "item_required":
            inventory = player_data.get("inventory", [])
            if condition["item"] not in inventory:
                failed_conditions.append(f"Must have {condition['item']}")

    if failed_conditions:
        return False, "; ".join(failed_conditions)

    return True, "All conditions met"

def check_chrono_weave_unlock(user_id: str) -> tuple[bool, str]:
    """Check if user can unlock Chrono Weave class."""
    from utils.database import get_user_rpg_data

    player_data = get_user_rpg_data(user_id)
    if not player_data:
        return False, "Player data not found"

    # Check boss defeat condition
    boss_defeats = player_data.get("boss_defeats", {})
    if "time_rift_dragon" not in boss_defeats:
        return False, "Must defeat Time Rift Dragon while level 30 or lower"

    # Check quest completion
    completed_quests = player_data.get("completed_quests", [])
    if "chrono_whispers" not in [q.get("name", "") for q in completed_quests]:
        return False, "Must complete Chrono Whispers quest"

    # Check ancient relics
    inventory = player_data.get("inventory", [])
    required_relics = ["relic_of_past", "relic_of_future", "relic_of_present"]
    missing_relics = [relic for relic in required_relics if relic not in inventory]

    if missing_relics:
        return False, f"Missing relics: {', '.join(missing_relics)}"

    return True, "All Chrono Weave requirements met"

def calculate_weapon_stats(weapon_name: str, player_data: dict) -> dict:
    """Calculate effective weapon stats based on player data."""
    from utils.constants import WEAPONS

    if weapon_name not in WEAPONS:
        return {"attack": 0, "defense": 0}

    weapon = WEAPONS[weapon_name]
    stats = {
        "attack": weapon.get("attack", 0),
        "defense": weapon.get("defense", 0)
    }

    # Apply class bonuses
    player_class = player_data.get("player_class")
    weapon_class = weapon.get("class_req")

    if weapon_class == "any" or player_class == weapon_class:
        # Apply special effects
        if weapon.get("special") == "randomized_boost" and weapon.get("random_stat_chance", 0) > 0:
            import random
            if random.random() < (weapon["random_stat_chance"] / 100):
                boost_stat = random.choice(["attack", "defense", "crit_chance"])
                boost_amount = weapon.get("random_stat_boost", 0)
                if boost_stat in stats:
                    stats[boost_stat] += boost_amount
                else:
                    stats[boost_stat] = boost_amount

    return stats

def format_weapon_info(weapon_name: str) -> str:
    """Format weapon information for display."""
    from utils.constants import WEAPONS, RARITY_COLORS

    if weapon_name not in WEAPONS:
        return f"Unknown weapon: {weapon_name}"

    weapon = WEAPONS[weapon_name]
    rarity = weapon.get("rarity", "common")

    info = f"**{weapon_name}** ({rarity.title()})\n"
    info += f"⚔️ Attack: {weapon.get('attack', 0)}\n"
    info += f"🛡️ Defense: {weapon.get('defense', 0)}\n"

    if weapon.get("class_req") != "any":
        info += f"🎭 Class: {weapon['class_req'].title()}\n"

    if weapon.get("special"):
        info += f"✨ Special: {weapon['special'].replace('_', ' ').title()}\n"

    return info

def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"

def deduplicate_items(items_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate items based on ID or name."""
    seen_ids = set()
    seen_names = set()
    unique_items = []
    
    for item in items_list:
        item_id = item.get('id')
        item_name = item.get('name')
        
        # Use ID if available, otherwise use name
        identifier = item_id if item_id else item_name
        
        if item_id and item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_items.append(item)
        elif not item_id and item_name and item_name not in seen_names:
            seen_names.add(item_name)
            unique_items.append(item)
    
    return unique_items

def format_shop_item(item_data: Dict[str, Any]) -> str:
    """Format a single shop item for display."""
    rarity = item_data.get('rarity', 'common')
    emoji = get_rarity_emoji(rarity)
    name = item_data.get('name', 'Unknown Item')
    price = item_data.get('price', 0)
    
    # Add attack/defense info if it's a weapon/armor
    stats = []
    if item_data.get('attack'):
        stats.append(f"⚔️{item_data['attack']}")
    if item_data.get('defense'):
        stats.append(f"🛡️{item_data['defense']}")
    
    stats_str = f" ({'/'.join(stats)})" if stats else ""
    
    return f"{emoji} **{name}**{stats_str} - {format_number(price)} coins"

def clear_item_cache():
    """Clear any cached item data to prevent duplicates."""
    logger.info("Item cache cleared")
    return True

def validate_shop_data() -> Dict[str, Any]:
    """Validate shop data for duplicates and errors."""
    from utils.constants import SHOP_ITEMS
    
    validation_results = {
        "total_items": len(SHOP_ITEMS),
        "duplicates_found": [],
        "missing_data": [],
        "valid": True
    }
    
    seen_names = set()
    
    # Check for required fields and name duplicates
    for item_id, item_data in SHOP_ITEMS.items():
        # Check required fields
        if not item_data.get('name'):
            validation_results["missing_data"].append(f"Item {item_id} missing name")
            validation_results["valid"] = False
        if not item_data.get('price'):
            validation_results["missing_data"].append(f"Item {item_id} missing price")
            validation_results["valid"] = False
        if not item_data.get('category'):
            validation_results["missing_data"].append(f"Item {item_id} missing category")
            validation_results["valid"] = False
            
        # Check for duplicate names
        name = item_data.get('name')
        if name:
            if name in seen_names:
                validation_results["duplicates_found"].append(f"Duplicate name: {name}")
                validation_results["valid"] = False
            seen_names.add(name)
    
    return validation_results

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to fit within Discord limits."""
    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."

def get_user_display_name(user: discord.User) -> str:
    """Get the best display name for a user."""
    return getattr(user, 'display_name', user.name)

def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed."""
    return create_embed(title, description, 0x00ff00)

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed."""
    return create_embed(title, description, 0xff0000)

def create_warning_embed(title: str, description: str) -> discord.Embed:
    """Create a warning embed."""
    return create_embed(title, description, 0xffff00)

def create_info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed."""
    return create_embed(title, description, 0x0099ff)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes} minutes, {remaining_seconds} seconds"
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours} hours, {remaining_minutes} minutes"
        return f"{hours} hours"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours > 0:
            return f"{days} days, {remaining_hours} hours"
        return f"{days} days"

def get_rarity_color(rarity: str) -> int:
    """Get color for item rarity."""
    rarity_colors = {
        'common': 0x95A5A6,      # Gray
        'uncommon': 0x2ECC71,    # Green
        'rare': 0x3498DB,        # Blue
        'epic': 0x9B59B6,        # Purple
        'legendary': 0xF39C12,   # Orange
        'mythical': 0xE74C3C     # Red
    }
    return rarity_colors.get(rarity.lower(), 0x95A5A6)

def get_rarity_emoji(rarity: str) -> str:
    """Get emoji for item rarity."""
    rarity_emojis = {
        'common': '⚪',
        'uncommon': '🟢',
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟠',
        'mythical': '🔴'
    }
    return rarity_emojis.get(rarity.lower(), '⚪')