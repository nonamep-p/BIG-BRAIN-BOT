import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from config import COLORS, EMOJIS, get_server_config, is_module_enabled
from utils.helpers import create_embed, format_number, create_progress_bar
from utils.database import get_user_rpg_data, update_user_rpg_data, ensure_user_exists, create_user_profile, get_leaderboard
from utils.constants import RPG_CONSTANTS, WEAPONS, ARMOR, RARITY_COLORS, RARITY_WEIGHTS, PVP_ARENAS, OMNIPOTENT_ITEM
from utils.rng_system import roll_with_luck, check_rare_event, get_luck_status, generate_loot_with_luck, weighted_random_choice
from replit import db

logger = logging.getLogger(__name__)

def check_level_requirement(user_data: Dict[str, Any], required_level: int, feature_name: str) -> tuple[bool, str]:
    """Check if user meets level requirement for a feature."""
    current_level = user_data.get('level', 1)
    if current_level < required_level:
        return False, f"❌ **{feature_name}** requires Level {required_level}! You are Level {current_level}."
    return True, ""

def check_class_requirement(user_data: Dict[str, Any], feature_name: str) -> tuple[bool, str]:
    """Check if user has chosen a class."""
    player_class = user_data.get('player_class')
    if not player_class:
        return False, f"❌ **{feature_name}** requires choosing a class first! Use `$class` to see available classes."
    return True, ""

def check_profession_requirement(user_data: Dict[str, Any], feature_name: str) -> tuple[bool, str]:
    """Check if user has a profession for crafting features."""
    profession = user_data.get('profession')
    if not profession:
        return False, f"❌ **{feature_name}** requires a profession! Use `$profession` to unlock one."
    return True, ""

def get_player_abilities(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get available abilities based on class and level."""
    player_class = user_data.get('player_class')
    level = user_data.get('level', 1)

    if not player_class:
        return []

    from utils.constants import PLAYER_CLASSES

    if player_class not in PLAYER_CLASSES:
        return []

    class_data = PLAYER_CLASSES[player_class]
    available_abilities = []

    for skill_name, skill_data in class_data['skills'].items():
        required_level = skill_data.get('level_requirement', 1)
        if level >= required_level:
            available_abilities.append({
                'name': skill_name,
                'data': skill_data,
                'unlocked': True
            })
        else:
            available_abilities.append({
                'name': skill_name,
                'data': skill_data,
                'unlocked': False,
                'required_level': required_level
            })

    return available_abilities

def level_up_player(player_data):
    """Enhanced level up with progression unlocks."""
    current_level = player_data.get('level', 1)
    current_xp = player_data.get('xp', 0)

    base_xp = 100
    xp_needed = int(base_xp * (1.5 ** (current_level - 1)))

    if current_xp >= xp_needed:
        new_level = current_level + 1
        remaining_xp = current_xp - xp_needed

        player_data['level'] = new_level
        player_data['xp'] = remaining_xp
        player_data['max_xp'] = int(base_xp * (1.5 ** (new_level - 1)))

        # Stat increases
        player_data['max_hp'] = player_data.get('max_hp', 100) + 10
        player_data['hp'] = player_data.get('max_hp', 100)
        player_data['attack'] = player_data.get('attack', 10) + 2
        player_data['defense'] = player_data.get('defense', 5) + 1
        player_data['max_mana'] = player_data.get('max_mana', 50) + 5
        player_data['mana'] = player_data.get('max_mana', 50)

        # Feature unlocks
        unlocks = []
        if new_level == 5:
            unlocks.append("🏟️ **PvP Combat** - Challenge other players!")
        if new_level == 10:
            unlocks.append("🔨 **Professions** - Learn crafting skills!")
        if new_level == 15:
            unlocks.append("🏰 **Dungeons** - Explore dangerous depths!")
        if new_level == 20:
            unlocks.append("🏛️ **Factions** - Join powerful organizations!")
        if new_level == 25:
            unlocks.append("🎁 **Lootboxes** - Try your luck with rare rewards!")
        if new_level == 30:
            unlocks.append("🏛️ **Auction House** - Trade with other players!")

        level_msg = f"🎉 Level {new_level}! HP+10, ATK+2, DEF+1, MP+5"
        if unlocks:
            level_msg += f"\n\n**🚀 Features Unlocked:**\n" + "\n".join(unlocks)

        return level_msg

    player_data['max_xp'] = xp_needed
    return None

def get_random_adventure_outcome():
    """Get a random adventure outcome."""
    outcomes = [
        {
            'description': 'You discovered a hidden treasure chest!',
            'coins': (50, 150),
            'xp': (20, 50),
            'items': ['Health Potion', 'Iron Sword', 'Leather Armor']
        },
        {
            'description': 'You defeated a group of bandits!',
            'coins': (30, 100),
            'xp': (15, 40),
            'items': ['Health Potion', 'Lucky Charm']
        },
        {
            'description': 'You helped a merchant and received a reward!',
            'coins': (40, 120),
            'xp': (10, 30),
            'items': ['Health Potion', 'Iron Sword']
        },
        {
            'description': 'You found rare materials while exploring!',
            'coins': (20, 80),
            'xp': (25, 60),
            'items': ['Health Potion', 'Lucky Charm', 'Iron Sword']
        }
    ]
    return random.choice(outcomes)

def calculate_battle_damage(attack, defense):
    """Calculate battle damage."""
    base_damage = max(1, attack - defense)
    # Add some randomness
    damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
    return max(1, damage)

class ProfileView(discord.ui.View):
    """Interactive profile view."""

    def __init__(self, user: discord.Member, player_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user = user
        self.player_data = player_data
        self.current_page = "stats"

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player stats."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.secondary)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player inventory."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_inventory_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🍀 Luck", style=discord.ButtonStyle.success)
    async def luck_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player luck status."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_luck_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_stats_embed(self) -> discord.Embed:
        """Create stats embed."""
        level = self.player_data.get('level', 1)
        xp = self.player_data.get('xp', 0)
        max_xp = self.player_data.get('max_xp', 100)
        hp = self.player_data.get('hp', 100)
        max_hp = self.player_data.get('max_hp', 100)
        attack = self.player_data.get('attack', 10)
        defense = self.player_data.get('defense', 5)
        coins = self.player_data.get('coins', 0)

        # Calculate XP percentage
        xp_percent = (xp / max_xp) * 100 if max_xp > 0 else 0
        hp_percent = (hp / max_hp) * 100 if max_hp > 0 else 0

        embed = discord.Embed(
            title=f"📊 {self.user.display_name}'s Profile",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        embed.add_field(
            name="📊 Level & Experience",
            value=f"**Level:** {level}\n"
                  f"**XP:** {xp:,}/{max_xp:,}\n"
                  f"{create_progress_bar(xp_percent)}",
            inline=True
        )

        embed.add_field(
            name="❤️ Health",
            value=f"**HP:** {hp}/{max_hp}\n"
                  f"{create_progress_bar(hp_percent)}",
            inline=True
        )

        embed.add_field(
            name="💰 Wealth",
            value=f"**Coins:** {format_number(coins)}",
            inline=True
        )

        embed.add_field(
            name="⚔️ Combat Stats",
            value=f"**Attack:** {attack}\n"
                  f"**Defense:** {defense}",
            inline=True
        )

        # Stats
        stats = self.player_data.get('stats', {})
        embed.add_field(
            name="📈 Statistics",
            value=f"**Battles Won:** {stats.get('battles_won', 0)}\n"
                  f"**Adventures:** {self.player_data.get('adventure_count', 0)}\n"
                  f"**Work Count:** {self.player_data.get('work_count', 0)}",
            inline=True
        )

        return embed

    def create_inventory_embed(self) -> discord.Embed:
        """Create inventory embed."""
        inventory = self.player_data.get('inventory', [])
        equipped = self.player_data.get('equipped', {})

        embed = discord.Embed(
            title=f"🎒 {self.user.display_name}'s Inventory",
            color=COLORS['secondary']
        )

        # Equipped items
        weapon = equipped.get('weapon', 'None')
        armor = equipped.get('armor', 'None')
        accessory = equipped.get('accessory', 'None')

        embed.add_field(
            name="🔧 Equipped",
            value=f"**Weapon:** {weapon}\n"
                  f"**Armor:** {armor}\n"
                  f"**Accessory:** {accessory}",
            inline=False
        )

        # Inventory items
        if inventory:
            items_text = ""
            for item in inventory[:10]:  # Show first 10 items
                items_text += f"• {item}\n"
            if len(inventory) > 10:
                items_text += f"... and {len(inventory) - 10} more items"
        else:
            items_text = "Your inventory is empty!"

        embed.add_field(
            name="📦 Items",
            value=items_text,
            inline=False
        )

        return embed

    def create_luck_embed(self) -> discord.Embed:
        """Create luck embed."""
        luck_status = get_luck_status(str(self.user.id))

        embed = discord.Embed(
            title=f"🍀 {self.user.display_name}'s Luck",
            color=COLORS['success']
        )

        embed.add_field(
            name="🎲 Luck Status",
            value=f"**Level:** {luck_status['emoji']} {luck_status['level']}\n"
                  f"**Points:** {luck_status['points']}\n"
                  f"**Bonus:** +{luck_status['bonus_percent']}%",
            inline=False
        )

        return embed

def generate_random_item():
    """Generate a random item with rarity."""
    # Choose item type
    item_type = random.choice(["weapon", "armor"])

    # Choose rarity based on weights
    rarity_list = []
    for rarity, weight in RARITY_WEIGHTS.items():
        rarity_list.extend([rarity] * int(weight * 100))

    chosen_rarity = random.choice(rarity_list)

    # Get items of chosen rarity
    if item_type == "weapon":
        items = {k: v for k, v in WEAPONS.items() if v["rarity"] == chosen_rarity}
    else:
        items = {k: v for k, v in ARMOR.items() if v["rarity"] == chosen_rarity}

    if not items:
        # Fallback to common items
        if item_type == "weapon":
            items = {k: v for k, v in WEAPONS.items() if v["rarity"] == "common"}
        else:
            items = {k: v for k, v in ARMOR.items() if v["rarity"] == "common"}

    item_name = random.choice(list(items.keys()))
    return item_name, items[item_name]

def get_rarity_emoji(rarity):
    """Get emoji for rarity."""
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟠",
        "mythic": "🔴",
        "divine": "🟡",
        "omnipotent": "💖"
    }
    return emojis.get(rarity, "⚪")

class AdventureView(discord.ui.View):
    """Interactive adventure view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Choose your adventure location...",
        options=[
            discord.SelectOption(
                label="Forest",
                value="Forest",
                description="A peaceful forest with hidden treasures",
                emoji="🌲"
            ),
            discord.SelectOption(
                label="Mountains",
                value="Mountains", 
                description="Treacherous peaks with great rewards",
                emoji="⛰️"
            ),
            discord.SelectOption(
                label="Dungeon",
                value="Dungeon",
                description="Dark underground chambers",
                emoji="🏰"
            ),
            discord.SelectOption(
                label="Desert",
                value="Desert",
                description="Endless sands with ancient secrets",
                emoji="🏜️"
            )
        ]
    )
    async def adventure_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Start an adventure."""
        location = select.values[0]

        # Disable the select while processing
        select.disabled = True
        await interaction.response.edit_message(view=self)

        # Process adventure
        await self.process_adventure(interaction, location)

    async def process_adventure(self, interaction: discord.Interaction, location: str):
        """Process the adventure."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.followup.send("❌ Could not retrieve your data!", ephemeral=True)
                return

            # Get adventure outcome
            outcome = get_random_adventure_outcome()

            # Calculate rewards with luck
            base_coins = random.randint(*outcome['coins'])
            base_xp = random.randint(*outcome['xp'])

            enhanced_rewards = generate_loot_with_luck(self.user_id, {
                'coins': base_coins,
                'xp': base_xp
            })

            coins_earned = enhanced_rewards['coins']
            xp_earned = enhanced_rewards['xp']

            # Random item reward
            items_found = []
            if roll_with_luck(self.user_id, 0.3):  # 30% chance for item
                items_found = [random.choice(outcome['items'])]

            # Update player data
            player_data['coins'] = player_data.get('coins', 0) + coins_earned
            player_data['xp'] = player_data.get('xp', 0) + xp_earned
            player_data['adventure_count'] = player_data.get('adventure_count', 0) + 1

            # Add items to inventory
            if items_found:
                inventory = player_data.get('inventory', [])
                inventory.extend(items_found)
                player_data['inventory'] = inventory

            # Check for level up
            level_up_msg = level_up_player(player_data)

            update_user_rpg_data(self.user_id, player_data)

            # Create result embed
            embed = discord.Embed(
                title=f"🗺️ Adventure Complete - {location}",
                description=outcome['description'],
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Rewards",
                value=f"**Coins:** {format_number(coins_earned)}\n"
                      f"**XP:** {xp_earned}",
                inline=True
            )

            if items_found:
                embed.add_field(
                    name="📦 Items Found",
                    value="\n".join([f"• {item}" for item in items_found]),
                    inline=True
                )

            if level_up_msg:
                embed.add_field(
                    name="📊 Level Up!",
                    value=level_up_msg,
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Adventure error: {e}")
            await interaction.followup.send("❌ Adventure failed! Please try again.", ephemeral=True)

class ShopView(discord.ui.View):
    """Comprehensive interactive shop with categories and detailed item views."""

    def __init__(self, user_id: str):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.current_category = "weapons"
        self.current_page = 0
        self.selected_item = None
        self.update_shop_display()

    def update_shop_display(self):
        """Update the shop display based on current category and page."""
        self.clear_items()

        # Category selector
        category_options = [
            discord.SelectOption(
                label="Weapons",
                value="weapons",
                description="Swords, axes, and magical weapons",
                emoji="⚔️",
                default=self.current_category == "weapons"
            ),
            discord.SelectOption(
                label="Armor",
                value="armor", 
                description="Protective gear and clothing",
                emoji="🛡️",
                default=self.current_category == "armor"
            ),
            discord.SelectOption(
                label="Consumables",
                value="consumables",
                description="Potions, food, and temporary items",
                emoji="🧪",
                default=self.current_category == "consumables"
            ),
            discord.SelectOption(
                label="Accessories",
                value="accessories",
                description="Rings, amulets, and special items",
                emoji="💎",
                default=self.current_category == "accessories"
            )
        ]

        category_select = discord.ui.Select(
            placeholder="📂 Choose item category...",
            options=category_options,
            custom_id="category_select"
        )
        category_select.callback = self.category_callback
        self.add_item(category_select)

        # Get items for current category
        items = self.get_category_items()

        if items:
            # Item selector with pagination
            items_per_page = 10
            start_idx = self.current_page * items_per_page
            end_idx = start_idx + items_per_page
            page_items = list(items.items())[start_idx:end_idx]

            if page_items:
                item_options = []
                for item_id, item_data in page_items[:25]:  # Discord limit
                    rarity = item_data.get('rarity', 'common')
                    emoji = get_rarity_emoji(rarity)
                    price = item_data.get('price', 0)

                    # Create description with key stats
                    desc_parts = [f"{format_number(price)} coins"]
                    if item_data.get('attack'):
                        desc_parts.append(f"⚔️{item_data['attack']}")
                    if item_data.get('defense'):
                        desc_parts.append(f"🛡️{item_data['defense']}")
                    if item_data.get('effect'):
                        effect = item_data['effect'].replace('_', ' ')[:20]
                        desc_parts.append(f"✨{effect}")

                    description = " | ".join(desc_parts)

                    item_options.append(discord.SelectOption(
                        label=item_data.get('name', 'Unknown Item')[:100],
                        value=item_id,
                        description=description[:100],
                        emoji=emoji
                    ))

                if item_options:
                    item_select = discord.ui.Select(
                        placeholder=f"🛍️ Select an item to view details...",
                        options=item_options,
                        custom_id="item_select"
                    )
                    item_select.callback = self.item_callback
                    self.add_item(item_select)

        # Navigation buttons
        nav_row = []

        # Previous page button
        if self.current_page > 0:
            prev_button = discord.ui.Button(
                label="◀ Previous",
                style=discord.ButtonStyle.secondary,
                custom_id="prev_page"
            )
            prev_button.callback = self.prev_page_callback
            nav_row.append(prev_button)

        # Next page button  
        total_items = len(self.get_category_items())
        items_per_page = 10
        max_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1

        if self.current_page < max_pages - 1:
            next_button = discord.ui.Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                custom_id="next_page"
            )
            next_button.callback = self.next_page_callback
            nav_row.append(next_button)

        # Refresh button
        refresh_button = discord.ui.Button(
            label="🔄 Refresh",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh"
        )
        refresh_button.callback = self.refresh_callback
        nav_row.append(refresh_button)

        # Add navigation buttons
        for button in nav_row:
            self.add_item(button)

        # Purchase button (only if item selected)
        if self.selected_item:
            purchase_button = discord.ui.Button(
                label="💰 Purchase Item",
                style=discord.ButtonStyle.success,
                custom_id="purchase"
            )
            purchase_button.callback = self.purchase_callback
            self.add_item(purchase_button)

    def get_category_items(self) -> Dict[str, Any]:
        """Get items for the current category."""
        from utils.constants import SHOP_ITEMS

        category_items = {}
        for item_id, item_data in SHOP_ITEMS.items():
            if item_data.get('category') == self.current_category:
                category_items[item_id] = item_data

        return category_items

    async def category_callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_category = interaction.data['values'][0]
        self.current_page = 0
        self.selected_item = None
        self.update_shop_display()

        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        """Handle item selection to show details."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.selected_item = interaction.data['values'][0]
        self.update_shop_display()

        embed = self.create_item_detail_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_page_callback(self, interaction: discord.Interaction):
        """Handle previous page navigation."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_page = max(0, self.current_page - 1)
        self.selected_item = None
        self.update_shop_display()

        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        """Handle next page navigation."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_page += 1
        self.selected_item = None
        self.update_shop_display()

        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def refresh_callback(self, interaction: discord.Interaction):
        """Handle shop refresh."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.selected_item = None
        self.update_shop_display()

        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def purchase_callback(self, interaction: discord.Interaction):
        """Handle item purchase."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        if not self.selected_item:
            await interaction.response.send_message("❌ No item selected!", ephemeral=True)
            return

        await self.process_purchase(interaction)

    def create_shop_embed(self) -> discord.Embed:
        """Create the main shop embed."""
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0

        embed = discord.Embed(
            title="🏪 Plagg's Chaos Shop",
            description=f"*\"Welcome to my shop! I've got everything a kwami needs... and some cheese!\"* 🧀\n\n"
                       f"💰 **Your Coins:** {format_number(coins)}",
            color=COLORS['warning']
        )

        # Category info
        category_info = {
            "weapons": {"emoji": "⚔️", "desc": "Swords, axes, staffs, and mystical weapons"},
            "armor": {"emoji": "🛡️", "desc": "Protective gear, robes, and defensive equipment"},
            "consumables": {"emoji": "🧪", "desc": "Potions, food, and temporary enhancement items"},
            "accessories": {"emoji": "💎", "desc": "Rings, amulets, charms, and special trinkets"}
        }

        current_info = category_info.get(self.current_category, {"emoji": "📦", "desc": "Various items"})
        embed.add_field(
            name=f"{current_info['emoji']} Current Category: {self.current_category.title()}",
            value=current_info['desc'],
            inline=False
        )

        # Items in category
        items = self.get_category_items()
        items_per_page = 10
        start_idx = self.current_page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = list(items.items())[start_idx:end_idx]

        if page_items:
            items_text = ""
            for i, (item_id, item_data) in enumerate(page_items, 1):
                rarity = item_data.get('rarity', 'common')
                emoji = get_rarity_emoji(rarity)
                name = item_data.get('name', 'Unknown')
                price = item_data.get('price', 0)

                # Add quick stats preview
                stats = []
                if item_data.get('attack'):
                    stats.append(f"⚔️{item_data['attack']}")
                if item_data.get('defense'):
                    stats.append(f"🛡️{item_data['defense']}")
                if item_data.get('effect'):
                    stats.append("✨Special")

                stats_text = f" [{'/'.join(stats)}]" if stats else ""
                items_text += f"`{start_idx + i:2d}.` {emoji} **{name}**{stats_text} - {format_number(price)} coins\n"

            embed.add_field(
                name="📋 Available Items",
                value=items_text,
                inline=False
            )

            # Page info
            total_pages = (len(items) - 1) // items_per_page + 1 if len(items) > 0 else 1
            embed.add_field(
                name="📄 Page Navigation",
                value=f"Page {self.current_page + 1} of {total_pages} | Total Items: {len(items)}",
                inline=True
            )
        else:
            embed.add_field(
                name="📋 Available Items",
                value="No items available in this category.",
                inline=False
            )

        embed.set_footer(text="💡 Select an item to view detailed information and purchase options!")
        return embed

    def create_item_detail_embed(self) -> discord.Embed:
        """Create detailed item view embed."""
        from utils.constants import SHOP_ITEMS

        if not self.selected_item or self.selected_item not in SHOP_ITEMS:
            return self.create_shop_embed()

        item_data = SHOP_ITEMS[self.selected_item]
        rarity = item_data.get('rarity', 'common')
        color = RARITY_COLORS.get(rarity, COLORS['primary'])
        emoji = get_rarity_emoji(rarity)

        embed = discord.Embed(
            title=f"{emoji} {item_data.get('name', 'Unknown Item')}",
            description=item_data.get('description', 'A mysterious item from Plagg\'s collection.'),
            color=color
        )

        # Item stats
        stats_text = ""
        if item_data.get('attack'):
            stats_text += f"⚔️ **Attack:** +{item_data['attack']}\n"
        if item_data.get('defense'):
            stats_text += f"🛡️ **Defense:** +{item_data['defense']}\n"
        if item_data.get('hp'):
            ```python
            stats_text += f"❤️ **Health:** +{item_data['hp']}\n"
        if item_data.get('mana'):
            stats_text += f"💙 **Mana:** +{item_data['mana']}\n"

        if stats_text:
            embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        # Special effects
        if item_data.get('effect'):
            effect_desc = self.format_effect_description(item_data['effect'])
            embed.add_field(name="✨ Special Effect", value=effect_desc, inline=True)

        # Price and rarity
        price = item_data.get('price', 0)
        embed.add_field(
            name="💰 Purchase Info",
            value=f"**Price:** {format_number(price)} coins\n"
                  f"**Rarity:** {rarity.title()}\n"
                  f"**Category:** {item_data.get('category', 'unknown').title()}",
            inline=True
        )

        # Player's current coins
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0
        
        can_afford = coins >= price
        afford_status = "✅ You can afford this!" if can_afford else f"❌ Need {format_number(price - coins)} more coins"
        
        embed.add_field(
            name="💳 Your Wallet",
            value=f"**Your Coins:** {format_number(coins)}\n{afford_status}",
            inline=False
        )

        # Usage instructions
        if item_data.get('category') == 'consumables':
            embed.add_field(
                name="📖 Usage",
                value="This item can be used from your inventory with the `$use` command.",
                inline=False
            )
        elif item_data.get('category') in ['weapons', 'armor']:
            embed.add_field(
                name="📖 Equipment",
                value="This item can be equipped from your inventory with the `$equip` command.",
                inline=False
            )

        embed.set_footer(text="💡 Click 'Purchase Item' to buy this item!")
        return embed

    def format_effect_description(self, effect: str) -> str:
        """Format effect descriptions to be more readable."""
        effect_descriptions = {
            'heal_50': 'Restores 50 HP instantly',
            'heal_500': 'Restores 500 HP instantly',
            'mana_50': 'Restores 50 MP instantly',
            'luck_boost': 'Increases luck for next adventure',
            'xp_double': 'Doubles XP gain for next battle',
            'revive': 'Revives from defeat (one-time use)',
            'random_reward': 'Contains random valuable items'
        }
        
        return effect_descriptions.get(effect, effect.replace('_', ' ').title())

    async def process_purchase(self, interaction: discord.Interaction):
        """Process the item purchase."""
        from utils.constants import SHOP_ITEMS
        
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            if self.selected_item not in SHOP_ITEMS:
                await interaction.response.send_message("❌ Invalid item selected!", ephemeral=True)
                return

            item_data = SHOP_ITEMS[self.selected_item]
            price = item_data.get('price', 0)
            coins = player_data.get('coins', 0)

            if coins < price:
                await interaction.response.send_message(
                    f"❌ **Insufficient funds!**\n"
                    f"You need **{format_number(price)}** coins but only have **{format_number(coins)}**.\n"
                    f"You need **{format_number(price - coins)}** more coins!",
                    ephemeral=True
                )
                return

            # Process purchase
            player_data['coins'] = coins - price
            inventory = player_data.get('inventory', [])
            inventory.append(item_data['name'])
            player_data['inventory'] = inventory

            # Update stats if needed
            stats = player_data.get('stats', {})
            stats['items_purchased'] = stats.get('items_purchased', 0) + 1
            player_data['stats'] = stats

            update_user_rpg_data(self.user_id, player_data)

            # Create purchase confirmation
            rarity = item_data.get('rarity', 'common')
            emoji = get_rarity_emoji(rarity)
            
            embed = discord.Embed(
                title="🎉 Purchase Successful!",
                description=f"You successfully purchased **{emoji} {item_data['name']}** for {format_number(price)} coins!",
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Transaction Details",
                value=f"**Item:** {item_data['name']}\n"
                      f"**Price:** {format_number(price)} coins\n"
                      f"**Remaining Coins:** {format_number(coins - price)}",
                inline=True
            )

            embed.add_field(
                name="📦 Next Steps",
                value="• Check your `$inventory` to see the item\n"
                      "• Use `$equip <item>` for weapons/armor\n"
                      "• Use `$use <item>` for consumables",
                inline=True
            )

            embed.set_footer(text="💡 Thanks for shopping at Plagg's Chaos Shop!")

            # Reset selection and update view
            self.selected_item = None
            self.update_shop_display()

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Purchase error: {e}")
            await interaction.response.send_message("❌ Purchase failed! Please try again.", ephemeral=True)

class LootboxView(discord.ui.View):
    """Lootbox opening view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="📦 Open Lootbox", style=discord.ButtonStyle.primary, emoji="🎁")
    async def open_lootbox(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open a lootbox."""
        player_data = get_user_rpg_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
            return

        inventory = player_data.get('inventory', [])
        if "Lootbox" not in inventory:
            await interaction.response.send_message("❌ You don't have any lootboxes!", ephemeral=True)
            return

        # Remove lootbox from inventory
        inventory.remove("Lootbox")
        player_data['inventory'] = inventory

        # Generate loot
        rewards = []
        coins_reward = 0

        # Always get coins
        coins_reward = random.randint(100, 1000)

        # Chance for items
        for _ in range(3):  # 3 chances for items
            if roll_with_luck(self.user_id, 0.4):  # 40% chance per roll
                item_name, item_data = generate_random_item()
                rewards.append(item_name)
                inventory.append(item_name)

        # Super rare chance for omnipotent items
        if roll_with_luck(self.user_id, 0.001):  # 0.1% chance
            if random.choice([True, False]):
                rewards.append("World Ender")
                inventory.append("World Ender")
            else:
                rewards.append("Reality Stone")
                inventory.append("Reality Stone")

        player_data['coins'] = player_data.get('coins', 0) + coins_reward
        player_data['inventory'] = inventory
        update_user_rpg_data(self.user_id, player_data)

        # Create result embed
        embed = discord.Embed(
            title="🎁 Lootbox Opened!",
            description=f"**Coins:** {format_number(coins_reward)}",
            color=COLORS['success']
        )

        if rewards:
            items_text = ""
            for item in rewards:
                if item in WEAPONS:
                    rarity = WEAPONS[item]["rarity"]
                elif item in ARMOR:
                    rarity = ARMOR[item]["rarity"]
                elif item == "Reality Stone":
                    rarity = "omnipotent"
                else:
                    rarity = "common"

                emoji = get_rarity_emoji(rarity)
                items_text += f"{emoji} **{item}** ({rarity})\n"

            embed.add_field(name="🎯 Items Found", value=items_text, inline=False)

        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class PvPView(discord.ui.View):
    """Enhanced turn-based PvP battle view."""

    def __init__(self, challenger_id: str, target_id: str, arena: str):
        super().__init__(timeout=300)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.arena = arena
        self.accepted = False
        self.battle_started = False
        self.current_turn = challenger_id
        self.turn_count = 0
        self.challenger_data = None
        self.target_data = None
        self.battle_log = []
        self.challenger_buffs = {}
        self.target_buffs = {}
        self.challenger_energy = 100
        self.target_energy = 100

    @discord.ui.button(label="⚔️ Accept Challenge", style=discord.ButtonStyle.success, custom_id="accept")
    async def accept_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        self.accepted = True
        await self.start_pvp_battle(interaction)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger, custom_id="decline")
    async def decline_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Decline the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="❌ Challenge Declined",
            description=f"<@{self.target_id}> declined the challenge.",
            color=COLORS['error']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger, disabled=True, custom_id="attack")
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the opponent."""
        if not self.battle_started:
            await interaction.response.send_message("❌ Battle hasn't started yet!", ephemeral=True)
            return

        if str(interaction.user.id) != self.current_turn:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return

        if self.get_user_energy(str(interaction.user.id)) < 20:
            await interaction.response.send_message("❌ Not enough energy! (Need 20)", ephemeral=True)
            return

        await self.process_attack(interaction)

    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.secondary, disabled=True, custom_id="defend")
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against next attack."""
        if not self.battle_started:
            await interaction.response.send_message("❌ Battle hasn't started yet!", ephemeral=True)
            return

        if str(interaction.user.id) != self.current_turn:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return

        if self.get_user_energy(str(interaction.user.id)) < 15:
            await interaction.response.send_message("❌ Not enough energy! (Need 15)", ephemeral=True)
            return

        await self.process_defend(interaction)

    @discord.ui.button(label="⚡ Special Attack", style=discord.ButtonStyle.primary, disabled=True, custom_id="special")
    async def special_attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use special attack."""
        if not self.battle_started:
            await interaction.response.send_message("❌ Battle hasn't started yet!", ephemeral=True)
            return

        if str(interaction.user.id) != self.current_turn:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return

        if self.get_user_energy(str(interaction.user.id)) < 40:
            await interaction.response.send_message("❌ Not enough energy! (Need 40)", ephemeral=True)
            return

        await self.process_special_attack(interaction)

    @discord.ui.button(label="🧪 Use Item", style=discord.ButtonStyle.success, disabled=True, custom_id="use_item")
    async def use_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item."""
        if not self.battle_started:
            await interaction.response.send_message("❌ Battle hasn't started yet!", ephemeral=True)
            return

        if str(interaction.user.id) != self.current_turn:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return

        await self.process_use_item(interaction)

    def get_user_energy(self, user_id: str) -> int:
        """Get user's current energy."""
        if user_id == self.challenger_id:
            return self.challenger_energy
        else:
            return self.target_energy

    def set_user_energy(self, user_id: str, energy: int):
        """Set user's energy."""
        if user_id == self.challenger_id:
            self.challenger_energy = max(0, min(100, energy))
        else:
            self.target_energy = max(0, min(100, energy))

    def get_user_data(self, user_id: str):
        """Get user's battle data."""
        if user_id == self.challenger_id:
            return self.challenger_data
        else:
            return self.target_data

    def get_opponent_data(self, user_id: str):
        """Get opponent's battle data."""
        if user_id == self.challenger_id:
            return self.target_data
        else:
            return self.challenger_data

    def get_opponent_id(self, user_id: str) -> str:
        """Get opponent's ID."""
        if user_id == self.challenger_id:
            return self.target_id
        else:
            return self.challenger_id

    def switch_turns(self):
        """Switch to the next player's turn."""
        self.current_turn = self.target_id if self.current_turn == self.challenger_id else self.challenger_id
        self.turn_count += 1
        
        # Restore energy each turn
        self.challenger_energy = min(100, self.challenger_energy + 25)
        self.target_energy = min(100, self.target_energy + 25)

    async def process_attack(self, interaction: discord.Interaction):
        """Process attack action."""
        user_id = str(interaction.user.id)
        opponent_id = self.get_opponent_id(user_id)
        user_data = self.get_user_data(user_id)
        opponent_data = self.get_opponent_data(user_id)

        # Calculate damage
        base_damage = user_data.get('attack', 10)
        opponent_defense = opponent_data.get('defense', 5)
        
        # Check for critical hit
        crit_chance = 0.15
        is_critical = random.random() < crit_chance
        
        damage = max(1, base_damage - opponent_defense)
        if is_critical:
            damage = int(damage * 1.5)

        # Apply buffs/debuffs
        damage = self.apply_damage_modifiers(user_id, damage)

        # Deal damage
        opponent_data['hp'] = max(0, opponent_data['hp'] - damage)
        
        # Use energy - FIXED: Actually deduct the energy
        current_energy = self.get_user_energy(user_id)
        new_energy = max(0, current_energy - 20)
        self.set_user_energy(user_id, new_energy)

        # Log action
        crit_text = " **CRITICAL HIT!**" if is_critical else ""
        self.battle_log.append(f"⚔️ <@{user_id}> attacks for {damage} damage!{crit_text} (-20 energy)")

        # Check for battle end
        if opponent_data['hp'] <= 0:
            await self.end_battle(interaction, user_id)
            return

        self.switch_turns()
        await self.update_battle_display(interaction)

    async def process_defend(self, interaction: discord.Interaction):
        """Process defend action."""
        user_id = str(interaction.user.id)
        
        # Add defense buff
        buffs = self.challenger_buffs if user_id == self.challenger_id else self.target_buffs
        buffs['defense'] = buffs.get('defense', 0) + 50
        
        # Use energy - FIXED: Actually deduct the energy
        current_energy = self.get_user_energy(user_id)
        new_energy = max(0, current_energy - 15)
        self.set_user_energy(user_id, new_energy)

        # Log action
        self.battle_log.append(f"🛡️ <@{user_id}> takes a defensive stance! (+50% defense next turn) (-15 energy)")

        self.switch_turns()
        await self.update_battle_display(interaction)

    async def process_special_attack(self, interaction: discord.Interaction):
        """Process special attack action."""
        user_id = str(interaction.user.id)
        opponent_id = self.get_opponent_id(user_id)
        user_data = self.get_user_data(user_id)
        opponent_data = self.get_opponent_data(user_id)

        # Special attack does more damage and has additional effects
        base_damage = user_data.get('attack', 10) * 2
        opponent_defense = opponent_data.get('defense', 5)
        
        damage = max(1, base_damage - opponent_defense)
        
        # Apply buffs/debuffs
        damage = self.apply_damage_modifiers(user_id, damage)

        # Deal damage
        opponent_data['hp'] = max(0, opponent_data['hp'] - damage)
        
        # Use energy - FIXED: Actually deduct the energy
        current_energy = self.get_user_energy(user_id)
        new_energy = max(0, current_energy - 40)
        self.set_user_energy(user_id, new_energy)

        # Add debuff to opponent
        opponent_buffs = self.target_buffs if opponent_id == self.target_id else self.challenger_buffs
        opponent_buffs['stunned'] = 1

        # Log action
        self.battle_log.append(f"⚡ <@{user_id}> uses SPECIAL ATTACK for {damage} damage! Opponent is stunned! (-40 energy)")

        # Check for battle end
        if opponent_data['hp'] <= 0:
            await self.end_battle(interaction, user_id)
            return

        self.switch_turns()
        await self.update_battle_display(interaction)

    async def process_use_item(self, interaction: discord.Interaction):
        """Process item usage."""
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)
        
        inventory = user_data.get('inventory', [])
        health_potions = [item for item in inventory if 'Potion' in item]
        
        if not health_potions:
            await interaction.response.send_message("❌ You have no healing items!", ephemeral=True)
            return

        # Use first health potion
        potion = health_potions[0]
        inventory.remove(potion)
        
        # Heal
        heal_amount = 50
        max_hp = user_data.get('max_hp', 100)
        user_data['hp'] = min(max_hp, user_data['hp'] + heal_amount)
        
        # Log action
        self.battle_log.append(f"🧪 <@{user_id}> uses {potion} and heals for {heal_amount} HP!")

        self.switch_turns()
        await self.update_battle_display(interaction)

    def apply_damage_modifiers(self, user_id: str, damage: int) -> int:
        """Apply buffs and debuffs to damage."""
        buffs = self.challenger_buffs if user_id == self.challenger_id else self.target_buffs
        opponent_buffs = self.target_buffs if user_id == self.challenger_id else self.challenger_buffs
        
        # Apply defense buff to opponent
        if 'defense' in opponent_buffs:
            damage = int(damage * 0.5)  # 50% damage reduction
            opponent_buffs['defense'] -= 1
            if opponent_buffs['defense'] <= 0:
                del opponent_buffs['defense']
        
        return damage

    async def update_battle_display(self, interaction: discord.Interaction):
        """Update the battle display."""
        # Check for stunned players
        current_buffs = self.challenger_buffs if self.current_turn == self.challenger_id else self.target_buffs
        
        if 'stunned' in current_buffs:
            self.battle_log.append(f"😵 <@{self.current_turn}> is stunned and loses their turn!")
            current_buffs['stunned'] -= 1
            if current_buffs['stunned'] <= 0:
                del current_buffs['stunned']
            self.switch_turns()

        embed = self.create_battle_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def end_battle(self, interaction: discord.Interaction, winner_id: str):
        """End the battle."""
        loser_id = self.get_opponent_id(winner_id)
        
        # Update stats and rewards
        arena_data = PVP_ARENAS[self.arena]
        entry_fee = arena_data["entry_fee"]
        winner_reward = entry_fee * arena_data["winner_multiplier"]

        winner_data = self.get_user_data(winner_id)
        loser_data = self.get_user_data(loser_id)

        # Award winner
        winner_data['coins'] = winner_data.get('coins', 0) + winner_reward
        winner_stats = winner_data.get('stats', {})
        winner_stats['pvp_wins'] = winner_stats.get('pvp_wins', 0) + 1
        winner_data['stats'] = winner_stats

        # Update loser
        loser_data['coins'] = max(0, loser_data.get('coins', 0) - entry_fee)
        loser_stats = loser_data.get('stats', {})
        loser_stats['pvp_losses'] = loser_stats.get('pvp_losses', 0) + 1
        loser_data['stats'] = loser_stats

        # Save data
        update_user_rpg_data(winner_id, winner_data)
        update_user_rpg_data(loser_id, loser_data)

        # Create victory embed
        embed = discord.Embed(
            title="🏆 PvP Battle Complete!",
            description=f"**Winner:** <@{winner_id}>\n"
                       f"**Arena:** {arena_data['name']}\n"
                       f"**Turns:** {self.turn_count}\n"
                       f"**Reward:** {format_number(winner_reward)} coins",
            color=COLORS['success']
        )

        # Show final battle log
        if self.battle_log:
            recent_log = self.battle_log[-5:]  # Last 5 actions
            embed.add_field(
                name="⚔️ Final Battle Log",
                value="\n".join(recent_log),
                inline=False
            )

        # Clear all buttons and create a new view with no buttons
        self.clear_items()
        self.stop()  # Stop the view to prevent further interactions

        await interaction.response.edit_message(embed=embed, view=None)

    def create_battle_embed(self) -> discord.Embed:
        """Create the battle status embed."""
        embed = discord.Embed(
            title=f"⚔️ PvP Battle - {PVP_ARENAS[self.arena]['name']}",
            description=f"**Turn {self.turn_count}** - <@{self.current_turn}>'s turn",
            color=COLORS['warning']
        )

        # Challenger stats
        challenger_hp = self.challenger_data['hp']
        challenger_max_hp = self.challenger_data['max_hp']
        challenger_hp_bar = create_progress_bar((challenger_hp / challenger_max_hp) * 100)
        challenger_energy_bar = create_progress_bar(self.challenger_energy)
        
        embed.add_field(
            name=f"⚔️ Challenger <@{self.challenger_id}>",
            value=f"❤️ HP: {challenger_hp}/{challenger_max_hp}\n{challenger_hp_bar}\n"
                  f"⚡ Energy: {self.challenger_energy}/100\n{challenger_energy_bar}",
            inline=True
        )

        # Target stats
        target_hp = self.target_data['hp']
        target_max_hp = self.target_data['max_hp']
        target_hp_bar = create_progress_bar((target_hp / target_max_hp) * 100)
        target_energy_bar = create_progress_bar(self.target_energy)
        
        embed.add_field(
            name=f"🛡️ Defender <@{self.target_id}>",
            value=f"❤️ HP: {target_hp}/{target_max_hp}\n{target_hp_bar}\n"
                  f"⚡ Energy: {self.target_energy}/100\n{target_energy_bar}",
            inline=True
        )

        # Battle log
        if self.battle_log:
            recent_log = self.battle_log[-3:]  # Last 3 actions
            embed.add_field(
                name="📜 Recent Actions",
                value="\n".join(recent_log),
                inline=False
            )

        # Active buffs
        buffs_text = ""
        if self.challenger_buffs:
            buffs_text += f"<@{self.challenger_id}>: {', '.join(self.challenger_buffs.keys())}\n"
        if self.target_buffs:
            buffs_text += f"<@{self.target_id}>: {', '.join(self.target_buffs.keys())}\n"
        
        if buffs_text:
            embed.add_field(
                name="✨ Active Effects",
                value=buffs_text,
                inline=False
            )

        embed.set_footer(text=f"⚡ Energy costs: Attack(20) | Defend(15) | Special(40)")
        return embed

    async def start_pvp_battle(self, interaction):
        """Start the actual PvP battle."""
        self.challenger_data = get_user_rpg_data(self.challenger_id)
        self.target_data = get_user_rpg_data(self.target_id)

        if not self.challenger_data or not self.target_data:
            await interaction.response.send_message("❌ Could not retrieve player data!", ephemeral=True)
            return

        # Initialize battle state
        self.battle_started = True
        self.current_turn = self.challenger_id
        self.turn_count = 1
        self.battle_log = []
        self.challenger_buffs = {}
        self.target_buffs = {}
        self.challenger_energy = 100
        self.target_energy = 100

        # Make copies of data to avoid modifying original
        self.challenger_data = self.challenger_data.copy()
        self.target_data = self.target_data.copy()

        # Clear all existing buttons and add only battle buttons
        self.clear_items()
        
        # Add battle-specific buttons
        attack_btn = discord.ui.Button(label="⚔️ Attack", style=discord.ButtonStyle.danger, custom_id="attack")
        attack_btn.callback = self.attack_button
        self.add_item(attack_btn)
        
        defend_btn = discord.ui.Button(label="🛡️ Defend", style=discord.ButtonStyle.secondary, custom_id="defend")
        defend_btn.callback = self.defend_button
        self.add_item(defend_btn)
        
        special_btn = discord.ui.Button(label="⚡ Special Attack", style=discord.ButtonStyle.primary, custom_id="special")
        special_btn.callback = self.special_attack_button
        self.add_item(special_btn)
        
        item_btn = discord.ui.Button(label="🧪 Use Item", style=discord.ButtonStyle.success, custom_id="use_item")
        item_btn.callback = self.use_item_button
        self.add_item(item_btn)

        # Create initial battle embed
        embed = self.create_battle_embed()
        embed.add_field(
            name="🎯 Battle Instructions",
            value="**Energy System:**\n"
                  "• Attack: 20 energy\n"
                  "• Defend: 15 energy (+50% defense)\n"
                  "• Special: 40 energy (2x damage + stun)\n"
                  "• Item: No energy cost\n\n"
                  "Energy regenerates +25 per turn!",
            inline=False
        )

        await interaction.response.edit_message(embed=embed, view=self)

class TradeView(discord.ui.View):
    """Trading system view."""

    def __init__(self, trader1_id: str, trader2_id: str):
        super().__init__(timeout=600)
        self.trader1_id = trader1_id
        self.trader2_id = trader2_id
        self.trader1_items = []
        self.trader2_items = []
        self.trader1_coins = 0
        self.trader2_coins = 0
        self.trader1_ready = False
        self.trader2_ready = False

    @discord.ui.button(label="💎 Add Items", style=discord.ButtonStyle.primary)
    async def add_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add items to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        await interaction.response.send_message("📝 Please type the item name you want to add to the trade:", ephemeral=True)

    @discord.ui.button(label="💰 Add Coins", style=discord.ButtonStyle.secondary)
    async def add_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add coins to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

```python
        await interaction.response.send_message("💰 Please type the amount of coins you want to add:", ephemeral=True)

    @discord.ui.button(label="✅ Ready", style=discord.ButtonStyle.success)
    async def ready_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mark as ready for trade."""
        user_id = str(interaction.user.id)

        if user_id == self.trader1_id:
            self.trader1_ready = True
        elif user_id == self.trader2_id:
            self.trader2_ready = True
        else:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        if self.trader1_ready and self.trader2_ready:
            await self.execute_trade(interaction)
        else:
            await interaction.response.send_message("✅ You are ready! Waiting for the other trader...", ephemeral=True)

    @discord.ui.button(label="❌ Cancel Trade", style=discord.ButtonStyle.danger)
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the trade."""
        embed = discord.Embed(
            title="❌ Trade Cancelled",
            description="The trade has been cancelled.",
            color=COLORS['error']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    async def execute_trade(self, interaction):
        """Execute the trade between players."""
        trader1_data = get_user_rpg_data(self.trader1_id)
        trader2_data = get_user_rpg_data(self.trader2_id)

        if not trader1_data or not trader2_data:
            await interaction.response.send_message("❌ Could not retrieve trader data!", ephemeral=True)
            return

        # Execute the trade
        # This is a simplified version - in practice you'd want more validation

        embed = discord.Embed(
            title="✅ Trade Completed!",
            description="The trade has been successfully completed!",
            color=COLORS['success']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

class BattleView(discord.ui.View):
    """Interactive battle view."""

    def __init__(self, user_id: str, enemy_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.enemy_data = enemy_data

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the enemy."""
        await self.process_battle_action(interaction, "attack")

    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.secondary)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against enemy attack."""
        await self.process_battle_action(interaction, "defend")

    @discord.ui.button(label="🧪 Use Item", style=discord.ButtonStyle.success)
    async def item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item."""
        await self.process_battle_action(interaction, "item")

    async def process_battle_action(self, interaction: discord.Interaction, action: str):
        """Process battle action."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            player_hp = player_data.get('hp', 100)
            player_attack = player_data.get('attack', 10)
            player_defense = player_data.get('defense', 5)

            enemy_hp = self.enemy_data.get('hp', 50)
            enemy_attack = self.enemy_data.get('attack', 8)

            battle_result = ""

            if action == "attack":
                # Player attacks
                damage = calculate_battle_damage(player_attack, 0)
                enemy_hp -= damage
                battle_result += f"You dealt {damage} damage to {self.enemy_data['name']}!\n"

                # Enemy attacks back if still alive
                if enemy_hp > 0:
                    enemy_damage = calculate_battle_damage(enemy_attack, player_defense)
                    player_hp -= enemy_damage
                    battle_result += f"{self.enemy_data['name']} dealt {enemy_damage} damage to you!\n"

            elif action == "defend":
                # Reduced damage when defending
                enemy_damage = calculate_battle_damage(enemy_attack, player_defense * 2)
                player_hp -= enemy_damage
                battle_result += f"You defended! {self.enemy_data['name']} dealt {enemy_damage} damage!\n"

            # Check battle outcome
            if enemy_hp <= 0:
                # Victory
                coins_reward = random.randint(50, 150)
                xp_reward = random.randint(20, 50)

                player_data['coins'] = player_data.get('coins', 0) + coins_reward
                player_data['xp'] = player_data.get('xp', 0) + xp_reward

                stats = player_data.get('stats', {})
                stats['battles_won'] = stats.get('battles_won', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="🎉 Victory!",
                    description=f"{battle_result}\n**You defeated {self.enemy_data['name']}!**\n\n"
                                f"**Rewards:**\n"
                                f"Coins: {format_number(coins_reward)}\n"
                                f"XP: {xp_reward}",
                    color=COLORS['success']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            elif player_hp <= 0:
                # Defeat
                player_data['hp'] = 0
                stats = player_data.get('stats', {})
                stats['battles_lost'] = stats.get('battles_lost', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="💀 Defeat!",
                    description=f"{battle_result}\n**You were defeated by {self.enemy_data['name']}!**\n\n"
                                f"You need to heal before your next battle.",
                    color=COLORS['error']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            else:
                # Battle continues
                self.enemy_data['hp'] = enemy_hp
                player_data['hp'] = player_hp

                embed = discord.Embed(
                    title=f"⚔️ Battle vs {self.enemy_data['name']}",
                    description=f"{battle_result}\n\n"
                                f"**Your HP:** {player_hp}/{player_data.get('max_hp', 100)}\n"
                                f"**{self.enemy_data['name']} HP:** {enemy_hp}/{self.enemy_data.get('max_hp', enemy_hp)}",
                    color=COLORS['warning']
                )

            # Update player data
            update_user_rpg_data(self.user_id, player_data)

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Battle error: {e}")
            await interaction.response.send_message("❌ Battle error! Please try again.", ephemeral=True)

class ProgressiveShopView(discord.ui.View):
    """Shop organized by player progression."""

    def __init__(self, user_id: str):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.current_category = "beginner"
        self.current_page = 0
        self.selected_item = None
        self.update_shop_display()

    def update_shop_display(self):
        """Update shop based on player level and progression."""
        self.clear_items()

        player_data = get_user_rpg_data(self.user_id)
        level = player_data.get('level', 1) if player_data else 1
        player_class = player_data.get('player_class') if player_data else None

        # Category options based on level
        category_options = [
            discord.SelectOption(
                label="Beginner Gear",
                value="beginner",
                description="Level 1+ • Basic weapons and armor",
                emoji="🗡️",
                default=self.current_category == "beginner"
            )
        ]

        if level >= 5:
            category_options.append(discord.SelectOption(
                label="Combat Supplies",
                value="combat",
                description="Level 5+ • Potions and consumables",
                emoji="🧪",
                default=self.current_category == "combat"
            ))

        if level >= 10:
            category_options.append(discord.SelectOption(
                label="Advanced Gear",
                value="advanced",
                description="Level 10+ • Better weapons and armor",
                emoji="⚔️",
                default=self.current_category == "advanced"
            ))

        if player_class and level >= 15:
            category_options.append(discord.SelectOption(
                label="Class Weapons",
                value="class_specific",
                description=f"Level 15+ • {player_class.title()} weapons",
                emoji="🌟",
                default=self.current_category == "class_specific"
            ))

        if level >= 25:
            category_options.append(discord.SelectOption(
                label="Rare Items",
                value="rare",
                description="Level 25+ • Lootboxes and rare gear",
                emoji="💎",
                default=self.current_category == "rare"
            ))

        if level >= 40:
            category_options.append(discord.SelectOption(
                label="Legendary",
                value="legendary",
                description="Level 40+ • Legendary equipment",
                emoji="🏆",
                default=self.current_category == "legendary"
            ))

        category_select = discord.ui.Select(
            placeholder="📂 Choose equipment category...",
            options=category_options,
            custom_id="category_select"
        )
        category_select.callback = self.category_callback
        self.add_item(category_select)

        # Get items for current category
        items = self.get_category_items()

        if items:
            item_options = []
            for item_id, item_data in list(items.items())[:25]:
                rarity = item_data.get('rarity', 'common')
                emoji = self.get_rarity_emoji(rarity)
                price = item_data.get('price', 0)

                item_options.append(discord.SelectOption(
                    label=item_data.get('name', 'Unknown Item')[:100],
                    value=item_id,
                    description=f"{format_number(price)} coins | {rarity.title()}"[:100],
                    emoji=emoji
                ))

            if item_options:
                item_select = discord.ui.Select(
                    placeholder=f"🛍️ Select an item to view details...",
                    options=item_options,
                    custom_id="item_select"
                )
                item_select.callback = self.item_callback
                self.add_item(item_select)

        # Purchase button
        if self.selected_item:
            purchase_button = discord.ui.Button(
                label="💰 Purchase Item",
                style=discord.ButtonStyle.success,
                custom_id="purchase"
            )
            purchase_button.callback = self.purchase_callback
            self.add_item(purchase_button)

    def get_category_items(self) -> Dict[str, Any]:
        """Get items based on category and player level."""
        from utils.constants import SHOP_ITEMS

        player_data = get_user_rpg_data(self.user_id)
        level = player_data.get('level', 1) if player_data else 1
        player_class = player_data.get('player_class') if player_data else None

        category_items = {}

        for item_id, item_data in SHOP_ITEMS.items():
            item_level_req = item_data.get('level_requirement', 1)

            # Skip items above player level
            if level < item_level_req:
                continue

            # Category filtering
            if self.current_category == "beginner" and item_level_req <= 5:
                if item_data.get('category') in ['weapons', 'armor'] and item_data.get('rarity') in ['common', 'uncommon']:
                    category_items[item_id] = item_data

            elif self.current_category == "combat" and level >= 5:
                if item_data.get('category') == 'consumables':
                    category_items[item_id] = item_data

            elif self.current_category == "advanced" and level >= 10:
                if item_data.get('category') in ['weapons', 'armor'] and item_data.get('rarity') in ['rare', 'epic']:
                    category_items[item_id] = item_data

            elif self.current_category == "class_specific" and player_class and level >= 15:
                if item_data.get('class_req') == player_class or item_data.get('class_req') == 'any':
                    if item_data.get('rarity') in ['epic', 'legendary']:
                        category_items[item_id] = item_data

            elif self.current_category == "rare" and level >= 25:
                if item_data.get('rarity') in ['legendary', 'mythic'] or item_data.get('name') == 'Lootbox':
                    category_items[item_id] = item_data

            elif self.current_category == "legendary" and level >= 40:
                if item_data.get('rarity') in ['mythic', 'divine', 'omnipotent']:
                    category_items[item_id] = item_data

        return category_items

    def get_rarity_emoji(self, rarity):
        """Get emoji for rarity."""
        emojis = {
            "common": "⚪",
            "uncommon": "🟢", 
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟠",
            "mythic": "🔴",
            "divine": "🟡",
            "omnipotent": "💖"
        }
        return emojis.get(rarity, "⚪")

    async def category_callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_category = interaction.data['values'][0]
        self.selected_item = None
        self.update_shop_display()

        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        """Handle item selection."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.selected_item = interaction.data['values'][0]
        self.update_shop_display()

        embed = self.create_item_detail_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def purchase_callback(self, interaction: discord.Interaction):
        """Handle item purchase."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        await self.process_purchase(interaction)

    def create_shop_embed(self) -> discord.Embed:
        """Create the shop embed."""
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0
        level = player_data.get('level', 1) if player_data else 1

        embed = discord.Embed(
            title="🏪 Progressive Equipment Shop",
            description=f"*Gear tailored to your adventure level!*\n\n"
                       f"💰 **Your Coins:** {format_number(coins)}\n"
                       f"📊 **Your Level:** {level}",
            color=COLORS['warning']
        )

        category_info = {
            "beginner": {"emoji": "🗡️", "desc": "Basic gear for new adventurers"},
            "combat": {"emoji": "🧪", "desc": "Potions and supplies for battles"},
            "advanced": {"emoji": "⚔️", "desc": "Superior weapons and armor"},
            "class_specific": {"emoji": "🌟", "desc": "Specialized class equipment"},
            "rare": {"emoji": "💎", "desc": "Rare items and lootboxes"},
            "legendary": {"emoji": "🏆", "desc": "Legendary and mythic equipment"}
        }

        current_info = category_info.get(self.current_category, {"emoji": "📦", "desc": "Various items"})
        embed.add_field(
            name=f"{current_info['emoji']} Current Category: {self.current_category.title()}",
            value=current_info['desc'],
            inline=False
        )

        items = self.get_category_items()
        if items:
            items_text = ""
            for i, (item_id, item_data) in enumerate(list(items.items())[:10], 1):
                rarity = item_data.get('rarity', 'common')
                emoji = self.get_rarity_emoji(rarity)
                name = item_data.get('name', 'Unknown')
                price = item_data.get('price', 0)
                level_req = item_data.get('level_requirement', 1)

                items_text += f"`{i:2d}.` {emoji} **{name}** (Lv.{level_req}) - {format_number(price)} coins\n"

            embed.add_field(
                name="📋 Available Items",
                value=items_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Available Items",
                value="No items available in this category for your level.",
                inline=False
            )

        embed.set_footer(text="💡 Select an item to view detailed information!")
        return embed

    def create_item_detail_embed(self) -> discord.Embed:
        """Create detailed item view."""
        from utils.constants import SHOP_ITEMS

        if not self.selected_item or self.selected_item not in SHOP_ITEMS:
            return self.create_shop_embed()

        item_data = SHOP_ITEMS[self.selected_item]
        rarity = item_data.get('rarity', 'common')
        color = RARITY_COLORS.get(rarity, COLORS['primary'])
        emoji = self.get_rarity_emoji(rarity)

        embed = discord.Embed(
            title=f"{emoji} {item_data.get('name', 'Unknown Item')}",
            description=item_data.get('description', 'A mysterious item from the shop.'),
            color=color
        )

        # Stats
        stats_text = ""
        if item_data.get('attack'):
            stats_text += f"⚔️ **Attack:** +{item_data['attack']}\n"
        if item_data.get('defense'):
            stats_text += f"🛡️ **Defense:** +{item_data['defense']}\n"
        if item_data.get('hp'):
            stats_text += f"❤️ **Health:** +{item_data['hp']}\n"

        if stats_text:
            embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        # Requirements and info
        price = item_data.get('price', 0)
        level_req = item_data.get('level_requirement', 1)
        class_req = item_data.get('class_req', 'Any')

        embed.add_field(
            name="📋 Requirements",
            value=f"**Level:** {level_req}\n"
                  f"**Class:** {class_req.title()}\n"
                  f"**Price:** {format_number(price)} coins",
            inline=True
        )

        # Player status
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0
        level = player_data.get('level', 1) if player_data else 1

        can_afford = coins >= price
        level_ok = level >= level_req

        status_text = ""
        status_text += "✅ Can afford" if can_afford else f"❌ Need {format_number(price - coins)} more coins"
        status_text += f"\n{'✅' if level_ok else '❌'} Level requirement"

        embed.add_field(
            name="💳 Purchase Status",
            value=status_text,
            inline=False
        )

        return embed

    async def process_purchase(self, interaction: discord.Interaction):
        """Process item purchase."""
        from utils.constants import SHOP_ITEMS

        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            if self.selected_item not in SHOP_ITEMS:
                await interaction.response.send_message("❌ Invalid item selected!", ephemeral=True)
                return

            item_data = SHOP_ITEMS[self.selected_item]
            price = item_data.get('price', 0)
            level_req = item_data.get('level_requirement', 1)
            coins = player_data.get('coins', 0)
            level = player_data.get('level', 1)

            # Check requirements
            if level < level_req:
                await interaction.response.send_message(
                    f"❌ **Level requirement not met!**\n"
                    f"Required: Level {level_req} | Your Level: {level}",
                    ephemeral=True
                )
                return

            if coins < price:
                await interaction.response.send_message(
                    f"❌ **Insufficient funds!**\n"
                    f"Price: {format_number(price)} | Your coins: {format_number(coins)}",
                    ephemeral=True
                )
                return

            # Process purchase
            player_data['coins'] = coins - price
            inventory = player_data.get('inventory', [])
            inventory.append(item_data['name'])
            player_data['inventory'] = inventory

            update_user_rpg_data(self.user_id, player_data)

            embed = discord.Embed(
                title="🎉 Purchase Successful!",
                description=f"You bought **{item_data['name']}** for {format_number(price)} coins!",
                color=COLORS['success']
            )

            self.selected_item = None
            self.update_shop_display()

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Purchase error: {e}")
            await interaction.response.send_message("❌ Purchase failed! Please try again.", ephemeral=True)

class EnhancedAdventureView(discord.ui.View):
    """Adventure system with level-gated locations."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Choose your adventure location...",
        options=[
            discord.SelectOption(
                label="Training Grounds",
                value="training",
                description="Level 1+ • Safe area for beginners",
                emoji="🏃"
            ),
            discord.SelectOption(
                label="Forest",
                value="forest",
                description="Level 3+ • Peaceful woods with small creatures",
                emoji="🌲"
            ),
            discord.SelectOption(
                label="Mountains",
                value="mountains", 
                description="Level 8+ • Dangerous peaks with better rewards",
                emoji="⛰️"
            ),
            discord.SelectOption(
                label="Dungeon Entrance",
                value="dungeon",
                description="Level 15+ • Dark chambers with rare treasures",
                emoji="🏰"
            ),
            discord.SelectOption(
                label="Dragon Lair",
                value="dragon_lair",
                description="Level 25+ • Extremely dangerous but epic rewards",
                emoji="🐉"
            )
        ]
    )
    async def adventure_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Start an adventure with level checking."""
        location = select.values[0]

        player_data = get_user_rpg_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
            return

        level = player_data.get('level', 1)

        # Level requirements for locations
        requirements = {
            'training': 1,
            'forest': 3,
            'mountains': 8,
            'dungeon': 15,
            'dragon_lair': 25
        }

        required_level = requirements.get(location, 1)
        if level < required_level:
            await interaction.response.send_message(
                f"❌ **{location.title()}** requires Level {required_level}! You are Level {level}.\n"
                f"💡 Try lower level areas first to gain experience!",
                ephemeral=True
            )
            return

        # Disable the select while processing
        select.disabled = True
        await interaction.response.edit_message(view=self)

        await self.process_adventure(interaction, location)

    async def process_adventure(self, interaction: discord.Interaction, location: str):
        """Process adventure with location-specific rewards."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            level = player_data.get('level', 1)

            # Location-specific rewards
            location_data = {
                'training': {
                    'coins': (10, 30),
                    'xp': (5, 15),
                    'items': ['Training Sword', 'Health Potion'],
                    'description': 'You practice your combat skills in safety.'
                },
                'forest': {
                    'coins': (30, 70),
                    'xp': (15, 35),
                    'items': ['Iron Sword', 'Leather Armor', 'Health Potion'],
                    'description': 'You venture through peaceful woodlands.'
                },
                'mountains': {
                    'coins': (60, 120),
                    'xp': (30, 60),
                    'items': ['Steel Sword', 'Chain Mail', 'Mana Potion'],
                    'description': 'You brave the treacherous mountain paths.'
                },
                'dungeon': {
                    'coins': (100, 200),
                    'xp': (50, 100),
                    'items': ['Mystic Blade', 'Plate Armor', 'Lucky Charm'],
                    'description': 'You explore dark underground chambers.'
                },
                'dragon_lair': {
                    'coins': (200, 500),
                    'xp': (100, 250),
                    'items': ['Dragon Slayer', 'Dragon Scale Armor', 'Phoenix Feather'],
                    'description': 'You dare to enter the legendary dragon\'s domain.'
                }
            }

            adventure_info = location_data.get(location, location_data['training'])

            # Calculate rewards
            base_coins = random.randint(*adventure_info['coins'])
            base_xp = random.randint(*adventure_info['xp'])

            # Level-based multiplier
            level_multiplier = 1 + (level - 1) * 0.1

            enhanced_rewards = generate_loot_with_luck(self.user_id, {
                'coins': int(base_coins * level_multiplier),
                'xp': int(base_xp * level_multiplier)
            })

            coins_earned = enhanced_rewards['coins']
            xp_earned = enhanced_rewards['xp']

            # Item rewards
            items_found = []
            if roll_with_luck(self.user_id, 0.4):  # 40% chance
                items_found = [random.choice(adventure_info['items'])]

            # Update player data
            player_data['coins'] = player_data.get('coins', 0) + coins_earned
            player_data['xp'] = player_data.get('xp', 0) + xp_earned
            player_data['adventure_count'] = player_data.get('adventure_count', 0) + 1

            if items_found:
                inventory = player_data.get('inventory', [])
                inventory.extend(items_found)
                player_data['inventory'] = inventory

            # Check for level up
            level_up_msg = level_up_player(player_data)

            update_user_rpg_data(self.user_id, player_data)

            # Create result embed
            embed = discord.Embed(
                title=f"🗺️ Adventure Complete - {location.title()}",
                description=adventure_info['description'],
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Rewards",
                value=f"**Coins:** {format_number(coins_earned)}\n"
                      f"**XP:** {xp_earned}",
                inline=True
            )

            if items_found:
                embed.add_field(
                    name="📦 Items Found",
                    value="\n".join([f"• {item}" for item in items_found]),
                    inline=True
                )

            if level_up_msg:
                embed.add_field(
                    name="📊 Level Up!",
                    value=level_up_msg,
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Adventure error: {e}")
            await interaction.followup.send("❌ Adventure failed! Please try again.", ephemeral=True)

class RPGGamesCog(commands.Cog):
    """Progressive RPG system with meaningful advancement."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start', help='Begin your RPG adventure')
    async def start_command(self, ctx):
        """Start RPG adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if get_user_rpg_data(user_id):
            await ctx.send("❌ You've already started your adventure! Use `$profile` to see your progress.")
            return

        if create_user_profile(user_id):
            embed = create_embed(
                "🎉 Welcome to Your Epic Adventure!",
                f"**{ctx.author.mention}, your journey begins now!**\n\n"
                f"🌟 **Starting Stats:**\n"
                f"• Level: 1 | HP: 100 | Attack: 10 | Defense: 5\n"
                f"• Coins: 100 | Mana: 50\n\n"
                f"📋 **Next Steps:**\n"
                f"1️⃣ Use `$adventure` to explore and gain XP\n"
                f"2️⃣ Reach Level 3 to unlock new areas\n"
                f"3️⃣ Use `$shop` to buy better equipment\n"
                f"4️⃣ At Level 5, choose your class with `$class`\n\n"
                f"💡 Use `$help rpg` for a complete guide!",
                COLORS['success']
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to start your adventure. Please try again.")

    @commands.command(name='class', help='Choose your character class (Level 5 required)')
    async def class_command(self, ctx, class_name: str = None):
        """Choose character class with level requirement."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ Start your adventure first with `$start`!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        # Check level requirement
        can_choose, error_msg = check_level_requirement(player_data, 5, "Class Selection")
        if not can_choose:
            await ctx.send(f"{error_msg}\n💡 Use `$adventure` to gain more experience!")
            return

        from utils.constants import PLAYER_CLASSES

        if not class_name:
            embed = discord.Embed(
                title="🎭 Choose Your Class",
                description="**Select your path at Level 5!**\n"
                           "Each class has unique abilities and playstyles.",
                color=COLORS['primary']
            )

            for class_key, class_data in PLAYER_CLASSES.items():
                if class_data.get('hidden'):
                    continue

                stats = class_data['base_stats']
                embed.add_field(
                    name=f"{class_data['name']} ({class_key})",
                    value=f"{class_data['description']}\n"
                          f"HP: {stats['hp']} | ATK: {stats['attack']} | DEF: {stats['defense']}",
                    inline=False
                )

            embed.set_footer(text="Use $class <name> to choose! (warrior, mage, rogue, archer, healer)")
            await ctx.send(embed=embed)
            return

        class_name = class_name.lower()
        if class_name not in PLAYER_CLASSES or PLAYER_CLASSES[class_name].get('hidden'):
            await ctx.send(f"❌ Invalid class! Use `$class` to see available options.")
            return

        if player_data.get('player_class'):
            await ctx.send("❌ You already chose a class! Classes cannot be changed.")
            return

        # Assign class
        class_data = PLAYER_CLASSES[class_name]
        player_data['player_class'] = class_name

        # Update stats
        base_stats = class_data['base_stats']
        player_data['max_hp'] = base_stats['hp']
        player_data['hp'] = base_stats['hp']
        player_data['attack'] = base_stats['attack']
        player_data['defense'] = base_stats['defense']
        player_data['max_mana'] = base_stats['mana']
        player_data['mana'] = base_stats['mana']

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"🎭 Class Selected: {class_data['name']}",
            f"**{class_data['description']}**\n\n"
            f"📊 **Your New Stats:**\n"
            f"HP: {base_stats['hp']} | Attack: {base_stats['attack']}\n"
            f"Defense: {base_stats['defense']} | Mana: {base_stats['mana']}\n\n"
            f"🌟 **Unlocked:** Use `$skills` to see your abilities!",
            COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name='skills', help='View your class abilities')
    async def skills_command(self, ctx):
        """View class skills and progression."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Start your adventure first!")
            return

        can_use, error_msg = check_class_requirement(player_data, "Skills")
        if not can_use:
            await ctx.send(f"{error_msg}\n💡 Reach Level 5 to choose a class!")
            return

        player_class = player_data['player_class']
        level = player_data.get('level', 1)

        from utils.constants import PLAYER_CLASSES
        class_data = PLAYER_CLASSES[player_class]

        embed = discord.Embed(
            title=f"⚡ {class_data['name']} Skills",
            description=f"Your abilities as a {class_data['name']}:",
            color=COLORS['primary']
        )

        abilities = get_player_abilities(player_data)
        for ability in abilities:
            status = "🔓" if ability['unlocked'] else "🔒"
            skill_data = ability['data']

            if ability['unlocked']:
                value = f"Mana Cost: {skill_data['mana_cost']}\n"
                value += f"Cooldown: {skill_data['cooldown']}s\n"
                value += f"Effect: {self._format_skill_effect(skill_data)}"
            else:
                value = f"🔒 **Unlocks at Level {ability['required_level']}**\n"
                value += f"Current Level: {level}"

            embed.add_field(
                name=f"{status} {ability['name'].replace('_', ' ').title()}",
                value=value,
                inline=True
            )

        await ctx.send(embed=embed)

    def _format_skill_effect(self, skill_data):
        """Format skill effect for display."""
        effects = []
        if 'damage' in skill_data:
            effects.append(f"Damage: {skill_data['damage']}")
        if 'heal' in skill_data:
            effects.append(f"Heal: {skill_data['heal']}")
        if 'defense_boost' in skill_data:
            effects.append(f"+{skill_data['defense_boost']} Defense")
        if 'attack_boost' in skill_data:
            effects.append(f"+{skill_data['attack_boost']} Attack")
        return ", ".join(effects) if effects else "Special Effect"

    @commands.command(name='adventure', help='Explore the world to gain experience and items')
    @commands.cooldown(1, RPG_CONSTANTS['adventure_cooldown'], commands.BucketType.user)
    async def adventure_command(self, ctx):
        """Go on progressive adventures."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ Start your adventure first with `$start`!")
            return

        view = EnhancedAdventureView(user_id)
        embed = create_embed(
            "🗺️ Choose Your Adventure",
            "**Where will your journey take you?**\n\n"
            "🌟 Higher level areas give better rewards!\n"
            "⚠️ But they also require more experience to access.\n\n"
            "💡 Start with Training Grounds if you're new!",
            COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='shop', help='Browse equipment and items')
    async def shop_command(self, ctx):
        """Browse the progressive shop."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ Start your adventure first with `$start`!")
            return

        view = ProgressiveShopView(user_id)
        embed = view.create_shop_embed()
        await ctx.send(embed=embed, view=view)

    @commands.command(name='pvp', help='Challenge another player (Level 5 required)')
    async def pvp_command(self, ctx, member: discord.Member, arena: str = "Training Ground"):
        """PvP with level requirements."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Start your adventure first!")
            return

        can_pvp, error_msg = check_level_requirement(player_data, 5, "PvP Combat")
        if not can_pvp:
            await ctx.send(f"{error_msg}\n💡 Gain more experience through adventures!")
            return

        # Continue with existing PvP logic...
        await ctx.send(f"⚔️ PvP system activated! Challenge {member.mention} to battle!")

    @commands.command(name='profession', help='Learn crafting skills (Level 10 required)')
    async def profession_command(self, ctx, profession_name: str = None):
        """Choose profession with level gate."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Start your adventure first!")
            return

        can_craft, error_msg = check_level_requirement(player_data, 10, "Professions")
        if not can_craft:
            await ctx.send(f"{error_msg}\n💡 Keep adventuring to unlock crafting!")
            return

        # Continue with profession logic...
        await ctx.send("🔨 Profession system unlocked!")

    @commands.command(name='profile', help='View your character profile and progression')
    async def profile_command(self, ctx, member: Optional[discord.Member] = None):
        """Enhanced profile with progression info."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve profile data.")
            return

        level = player_data.get('level', 1)
        xp = player_data.get('xp', 0)
        max_xp = player_data.get('max_xp', 100)
        hp = player_data.get('hp', 100)
        max_hp = player_data.get('max_hp', 100)
        coins = player_data.get('coins', 0)
        player_class = player_data.get('player_class', 'Classless')

        embed = discord.Embed(
            title=f"📊 {target.display_name}'s Adventure Profile",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        # Basic stats
        xp_percent = (xp / max_xp) * 100 if max_xp > 0 else 0
        hp_percent = (hp / max_hp) * 100 if max_hp > 0 else 0

        embed.add_field(
            name="📈 Level & Progress",
            value=f"**Level:** {level}\n"
                  f"**Class:** {player_class.title()}\n"
                  f"**XP:** {xp:,}/{max_xp:,}\n"
                  f"{create_progress_bar(xp_percent)}",
            inline=True
        )

        embed.add_field(
            name="💪 Combat Stats",
            value=f"❤️ **HP:** {hp}/{max_hp}\n"
                  f"⚔️ **Attack:** {player_data.get('attack', 10)}\n"
                  f"🛡️ **Defense:** {player_data.get('defense', 5)}\n"
                  f"💙 **Mana:** {player_data.get('mana', 50)}/{player_data.get('max_mana', 50)}",
            inline=True
        )

        embed.add_field(
            name="💰 Resources",
            value=f"**Coins:** {format_number(coins)}\n"
                  f"**Adventures:** {player_data.get('adventure_count', 0)}\n"
                  f"**Battles Won:** {player_data.get('stats', {}).get('battles_won', 0)}",
            inline=True
        )

        # Feature availability
        features = []
        if level >= 5:
            features.append("✅ Class Selection")
            features.append("✅ PvP Combat")
        else:
            features.append("🔒 Class Selection (Level 5)")
            features.append("🔒 PvP Combat (Level 5)")

        if level >= 10:
            features.append("✅ Professions")
        else:
            features.append("🔒 Professions (Level 10)")

        if level >= 15:
            features.append("✅ Dungeons")
        else:
            features.append("🔒 Dungeons (Level 15)")

        embed.add_field(
            name="🎯 Available Features",
            value="\n".join(features),
            inline=False
        )

        embed.set_footer(text="Use $adventure to gain experience and unlock new features!")
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(RPGGamesCog(bot))