"""
Enhanced Constants for the Epic RPG Bot with Progressive System
"""
from typing import Dict, Any, List

# RPG System Constants
RPG_CONSTANTS = {
    # Cooldowns (in seconds)
    'work_cooldown': 3600,      # 1 hour
    'daily_cooldown': 86400,    # 24 hours
    'adventure_cooldown': 900,   # 15 minutes (reduced for better progression)
    'battle_cooldown': 300,     # 5 minutes
    'dungeon_cooldown': 7200,   # 2 hours
    'craft_cooldown': 600,      # 10 minutes
    'gather_cooldown': 900,     # 15 minutes
    'trade_cooldown': 1800,     # 30 minutes
    'quest_cooldown': 3600,     # 1 hour

    # Costs
    'heal_cost': 50,            # Cost to heal
    'revive_cost': 100,         # Cost to revive
    'guild_creation_cost': 5000, # Cost to create guild
    'profession_unlock_cost': 1000, # Cost to unlock profession

    # Level system
    'base_xp': 100,             # XP needed for level 2
    'xp_multiplier': 1.5,       # XP multiplier per level
    'max_level': 100,           # Maximum player level
    'prestige_level': 50,       # Level required for prestige

    # Battle system
    'critical_chance': 0.1,     # 10% critical hit chance
    'critical_multiplier': 2.0,  # 2x damage on critical
    'max_party_size': 4,        # Maximum party members

    # Feature unlock levels
    'class_unlock_level': 5,
    'pvp_unlock_level': 5,
    'profession_unlock_level': 10,
    'dungeon_unlock_level': 15,
    'faction_unlock_level': 20,
    'lootbox_unlock_level': 25,
    'auction_unlock_level': 30,
    # Luck system
    'luck_decay': 0.95,         # Luck decay per day
    'max_luck': 1000,           # Maximum luck points

    # Economy
    'max_inventory_size': 50,   # Maximum inventory slots
    'auction_tax': 0.05,        # 5% auction house tax
    'trade_fee': 100,           # Cost to initiate trade
}

# Player Classes with level-based skill unlocks
PLAYER_CLASSES = {
    'warrior': {
        'name': 'Cheese Guardian',
        'description': 'Tank warrior with high defense and protective abilities',
        'base_stats': {'hp': 120, 'attack': 15, 'defense': 12, 'mana': 50},
        'skills': {
            'shield_bash': {
                'damage': 20, 'mana_cost': 15, 'cooldown': 300, 'level_requirement': 5,
                'description': 'Bash enemies with your shield'
            },
            'taunt': {
                'aggro': True, 'mana_cost': 10, 'cooldown': 180, 'level_requirement': 8,
                'description': 'Force enemies to target you'
            },
            'berserker_rage': {
                'attack_boost': 25, 'mana_cost': 30, 'cooldown': 600, 'level_requirement': 15,
                'description': 'Increase attack power temporarily'
            }
        }
    },
    'mage': {
        'name': 'Kwami Sorcerer',
        'description': 'Master of magical arts with powerful spells',
        'base_stats': {'hp': 80, 'attack': 25, 'defense': 5, 'mana': 100},
        'skills': {
            'magic_missile': {
                'damage': 30, 'mana_cost': 20, 'cooldown': 300, 'level_requirement': 5,
                'description': 'Launch magical projectiles'
            },
            'heal': {
                'heal': 40, 'mana_cost': 25, 'cooldown': 240, 'level_requirement': 10,
                'description': 'Restore health with magic'
            },
            'fireball': {
                'damage': 50, 'mana_cost': 40, 'cooldown': 480, 'level_requirement': 15,
                'description': 'Cast devastating fire magic'
            }
        }
    },
    'rogue': {
        'name': 'Shadow Cat',
        'description': 'Stealthy assassin with high damage and critical hits',
        'base_stats': {'hp': 90, 'attack': 22, 'defense': 8, 'mana': 70},
        'skills': {
            'backstab': {
                'damage': 35, 'crit_chance': 0.5, 'mana_cost': 20, 'cooldown': 300, 'level_requirement': 5,
                'description': 'Critical strike from behind'
            },
            'stealth': {
                'invisible': True, 'mana_cost': 25, 'cooldown': 420, 'level_requirement': 12,
                'description': 'Become invisible temporarily'
            },
            'poison_blade': {
                'damage': 25, 'poison': True, 'mana_cost': 30, 'cooldown': 360, 'level_requirement': 18,
                'description': 'Apply poison to weapons'
            }
        }
    },
    'archer': {
        'name': 'Cheese Hunter',
        'description': 'Ranged specialist with precision and mobility',
        'base_stats': {'hp': 95, 'attack': 20, 'defense': 7, 'mana': 60},
        'skills': {
            'aimed_shot': {
                'damage': 40, 'accuracy': 0.95, 'mana_cost': 18, 'cooldown': 300, 'level_requirement': 5,
                'description': 'Carefully aimed shot with high accuracy'
            },
            'multi_shot': {
                'hits': 3, 'damage': 15, 'mana_cost': 30, 'cooldown': 480, 'level_requirement': 12,
                'description': 'Fire multiple arrows'
            },
            'explosive_arrow': {
                'damage': 60, 'area_damage': True, 'mana_cost': 45, 'cooldown': 600, 'level_requirement': 20,
                'description': 'Arrow that explodes on impact'
            }
        }
    },
    'healer': {
        'name': 'Tikki Disciple',
        'description': 'Support specialist focused on healing and buffs',
        'base_stats': {'hp': 85, 'attack': 12, 'defense': 10, 'mana': 120},
        'skills': {
            'heal': {
                'heal': 50, 'mana_cost': 20, 'cooldown': 180, 'level_requirement': 5,
                'description': 'Restore ally health'
            },
            'group_heal': {
                'heal': 30, 'targets': 'all', 'mana_cost': 40, 'cooldown': 360, 'level_requirement': 15,
                'description': 'Heal all party members'
            },
            'divine_protection': {
                'shield': True, 'mana_cost': 35, 'cooldown': 480, 'level_requirement': 20,
                'description': 'Grant magical protection'
            }
        }
    },
    'chrono_weave': {
        'name': 'Chrono Weave',
        'description': 'Master of time manipulation and temporal magic',
        'base_stats': {'hp': 100, 'attack': 25, 'defense': 15, 'mana': 150},
        'skills': {
            'time_reversal': {'revert_turns': 5, 'mana_cost': 80, 'cooldown': 259200},
            'temporal_surge': {'crit_boost': 20, 'xp_boost': 10, 'mana_cost': 40, 'cooldown': 900},
            'chrono_immunity': {'debuff_resist': 100, 'mana_cost': 60, 'cooldown': 1200}
        },
        'unlock_conditions': {
            'time_rift_dragon_defeat': {'level_cap': 30, 'boss_level': 80},
            'chrono_whispers_quest': {'event_required': 'time_rift'},
            'ancient_relics': ['relic_of_past', 'relic_of_future', 'relic_of_present']
        },
        'hidden': True
    }
}

# Professions System
PROFESSIONS = {
    'blacksmith': {
        'name': 'Miraculous Forger',
        'description': 'Crafts weapons and armor infused with kwami power',
        'max_level': 50,
        'recipes': ['iron_sword', 'steel_armor', 'miraculous_blade'],
        'gathering_spots': ['forge', 'mining_cave', 'scrapyard']
    },
    'alchemist': {
        'name': 'Potion Master',
        'description': 'Brews magical potions and elixirs',
        'max_level': 50,
        'recipes': ['health_potion', 'mana_elixir', 'cheese_brew'],
        'gathering_spots': ['herb_garden', 'crystal_cave', 'ancient_lab']
    },
    'enchanter': {
        'name': 'Kwami Enchanter',
        'description': 'Imbues items with magical properties',
        'max_level': 50,
        'recipes': ['fire_enchant', 'luck_charm', 'plagg_blessing'],
        'gathering_spots': ['magic_circle', 'kwami_shrine', 'moonstone_altar']
    }
}

# Crafting Recipes
CRAFTING_RECIPES = {
    'cheese_sword': {
        'profession': 'blacksmith',
        'level_required': 5,
        'materials': {'iron_ore': 3, 'aged_cheese': 2, 'kwami_essence': 1},
        'result': {'name': 'Cheese Sword', 'type': 'weapon', 'attack': 25, 'special': 'cheese_power'},
        'success_rate': 0.8
    },
    'camembert_armor': {
        'profession': 'blacksmith',
        'level_required': 10,
        'materials': {'steel_ingot': 5, 'camembert_wheel': 3, 'plagg_whisker': 1},
        'result': {'name': 'Camembert Armor', 'type': 'armor', 'defense': 30, 'special': 'cheese_resistance'},
        'success_rate': 0.7
    },
    'kwami_potion': {
        'profession': 'alchemist',
        'level_required': 8,
        'materials': {'crystal_water': 2, 'moonflower': 3, 'kwami_tear': 1},
        'result': {'name': 'Kwami Potion', 'type': 'consumable', 'heal': 100, 'special': 'mana_restore'},
        'success_rate': 0.75
    }
}

# Gathering Materials
GATHERING_MATERIALS = {
    'iron_ore': {'locations': ['mining_cave', 'mountain_pass'], 'rarity': 'common', 'base_chance': 0.6},
    'aged_cheese': {'locations': ['cheese_cellar', 'plagg_shrine'], 'rarity': 'uncommon', 'base_chance': 0.3},
    'kwami_essence': {'locations': ['kwami_shrine', 'miraculous_garden'], 'rarity': 'rare', 'base_chance': 0.1},
    'moonflower': {'locations': ['enchanted_forest', 'moonstone_altar'], 'rarity': 'uncommon', 'base_chance': 0.4},
    'plagg_whisker': {'locations': ['plagg_shrine'], 'rarity': 'legendary', 'base_chance': 0.05}
}

# Factions
FACTIONS = {
    'miraculous_order': {
        'name': 'Order of the Miraculous',
        'description': 'Protectors of the Miraculous and defenders of Paris',
        'alignment': 'good',
        'perks': ['healing_boost', 'teamwork_bonus', 'protection_aura'],
        'enemies': ['butterfly_syndicate']
    },
    'butterfly_syndicate': {
        'name': 'Butterfly Syndicate',
        'description': 'Those who seek power through dark miraculous',
        'alignment': 'evil',
        'perks': ['damage_boost', 'fear_aura', 'corruption_resistance'],
        'enemies': ['miraculous_order']
    },
    'cheese_guild': {
        'name': 'Ancient Cheese Guild',
        'description': 'Devoted followers of Plagg and cheese worship',
        'alignment': 'neutral',
        'perks': ['luck_boost', 'cheese_affinity', 'plagg_blessing'],
        'enemies': []
    }
}

# Quest Types
QUEST_TYPES = {
    'kill': {
        'name': 'Elimination',
        'description': 'Defeat specific monsters',
        'rewards': {'xp': (100, 300), 'coins': (200, 500), 'items': ['weapon', 'armor']}
    },
    'collection': {
        'name': 'Gathering',
        'description': 'Collect specific materials',
        'rewards': {'xp': (50, 150), 'coins': (100, 300), 'items': ['material', 'tool']}
    },
    'exploration': {
        'name': 'Discovery',
        'description': 'Explore new locations',
        'rewards': {'xp': (150, 400), 'coins': (300, 700), 'items': ['map', 'compass']}
    },
    'delivery': {
        'name': 'Courier',
        'description': 'Transport items between NPCs',
        'rewards': {'xp': (75, 200), 'coins': (150, 400), 'items': ['consumable']}
    },
    'story': {
        'name': 'Epic Tale',
        'description': 'Multi-part story quests with choices',
        'rewards': {'xp': (500, 1000), 'coins': (1000, 2500), 'items': ['legendary', 'unique']}
    }
}

# World Events
WORLD_EVENTS = {
    'cheese_storm': {
        'name': 'The Great Cheese Storm',
        'description': 'Plagg has gone wild! Cheese rains from the sky!',
        'duration': 3600,  # 1 hour
        'effects': {'loot_multiplier': 2.0, 'cheese_drop_chance': 0.8},
        'rewards': {'cheese_crown': 1, 'golden_camembert': 5}
    },
    'kwami_invasion': {
        'name': 'Rogue Kwami Invasion',
        'description': 'Wild kwamis have appeared across all locations!',
        'duration': 7200,  # 2 hours
        'effects': {'rare_encounter_chance': 0.5, 'xp_multiplier': 1.5},
        'rewards': {'kwami_fragment': 10, 'miraculous_shard': 3}
    },
    'camembert_colossus': {
        'name': 'Rise of the Camembert Colossus',
        'description': 'A giant cheese monster threatens all! Form parties to defeat it!',
        'duration': 10800,  # 3 hours
        'effects': {'global_boss': True, 'min_players': 10},
        'rewards': {'legendary_cheese_armor': 1, 'colossus_medal': 1}
    }
}

# Shop Items with level requirements and progressive pricing
SHOP_ITEMS = {
    # Beginner Gear (Level 1-5)
    "weapon_001": {
        "id": "weapon_001",
        "name": "Training Sword",
        "attack": 3,
        "defense": 1,
        "price": 50,
        "level_requirement": 1,
        "rarity": "common",
        "category": "weapons",
        "description": "A practice sword for beginners"
    },
    "weapon_002": {
        "id": "weapon_002",
        "name": "Iron Sword",
        "attack": 8,
        "defense": 2,
        "price": 150,
        "level_requirement": 3,
        "rarity": "common",
        "category": "weapons",
        "description": "A basic iron sword"
    },
    "armor_001": {
        "id": "armor_001",
        "name": "Cloth Armor",
        "defense": 4,
        "price": 80,
        "level_requirement": 1,
        "rarity": "common",
        "category": "armor",
        "description": "Simple cloth protection"
    },
    "armor_002": {
        "id": "armor_002",
        "name": "Leather Armor",
        "defense": 8,
        "price": 200,
        "level_requirement": 3,
        "rarity": "common",
        "category": "armor",
        "description": "Basic leather protection"
    },

    # Combat Supplies (Level 5+)
    "item_001": {
        "id": "item_001",
        "name": "Health Potion",
        "effect": "heal_50",
        "price": 30,
        "level_requirement": 1,
        "rarity": "common",
        "category": "consumables",
        "description": "Restores 50 HP"
    },
    "item_002": {
        "id": "item_002",
        "name": "Mana Potion",
        "effect": "mana_50",
        "price": 40,
        "level_requirement": 5,
        "rarity": "common",
        "category": "consumables",
        "description": "Restores 50 MP"
    },
    "item_003": {
        "id": "item_003",
        "name": "Energy Drink",
        "effect": "restore_energy",
        "price": 100,
        "level_requirement": 5,
        "rarity": "uncommon",
        "category": "consumables",
        "description": "Restores battle energy"
    },

    # Advanced Gear (Level 10+)
    "weapon_003": {
        "id": "weapon_003",
        "name": "Steel Sword",
        "attack": 15,
        "defense": 3,
        "price": 500,
        "level_requirement": 10,
        "rarity": "uncommon",
        "category": "weapons",
        "description": "A well-forged steel blade"
    },
    "weapon_004": {
        "id": "weapon_004",
        "name": "Enchanted Blade",
        "attack": 22,
        "defense": 5,
        "price": 1200,
        "level_requirement": 15,
        "rarity": "rare",
        "category": "weapons",
        "description": "A blade infused with magic"
    },
    "armor_003": {
        "id": "armor_003",
        "name": "Chain Mail",
        "defense": 15,
        "price": 600,
        "level_requirement": 10,
        "rarity": "uncommon",
        "category": "armor",
        "description": "Interlocked metal rings"
    },
    "armor_004": {
        "id": "armor_004",
        "name": "Plate Armor",
        "defense": 25,
        "price": 1500,
        "level_requirement": 15,
        "rarity": "rare",
        "category": "armor",
        "description": "Heavy protective plates"
    },

    # Class-Specific Gear (Level 15+)
    "weapon_005": {
        "id": "weapon_005",
        "name": "Guardian's Shield",
        "attack": 18,
        "defense": 20,
        "price": 2000,
        "level_requirement": 15,
        "class_req": "warrior",
        "rarity": "epic",
        "category": "weapons",
        "description": "A warrior's protective weapon"
    },
    "weapon_006": {
        "id": "weapon_006",
        "name": "Sorcerer's Staff",
        "attack": 30,
        "mana_boost": 30,
        "price": 2200,
        "level_requirement": 15,
        "class_req": "mage",
        "rarity": "epic",
        "category": "weapons",
        "description": "Amplifies magical power"
    },
    "weapon_007": {
        "id": "weapon_007",
        "name": "Shadow Daggers",
        "attack": 35,
        "crit_chance": 15,
        "price": 2500,
        "level_requirement": 15,
        "class_req": "rogue",
        "rarity": "epic",
        "category": "weapons",
        "description": "Twin blades for assassins"
    },

    # Rare Items (Level 25+)
    "item_007": {
        "id": "item_007",
        "name": "Lootbox",
        "effect": "random_reward",
        "price": 1000,
        "level_requirement": 25,
        "rarity": "rare",
        "category": "consumables",
        "description": "Contains random rewards"
    },
    "item_008": {
        "id": "item_008",
        "name": "Lucky Charm",
        "effect": "luck_boost",
        "price": 800,
        "level_requirement": 20,
        "rarity": "rare",
        "category": "consumables",
        "description": "Increases luck temporarily"
    },

    # Legendary Items (Level 40+)
    "weapon_008": {
        "id": "weapon_008",
        "name": "Dragon Slayer",
        "attack": 50,
        "defense": 15,
        "price": 10000,
        "level_requirement": 40,
        "rarity": "legendary",
        "category": "weapons",
        "description": "Forged to slay dragons"
    },
    "armor_005": {
        "id": "armor_005",
        "name": "Celestial Robes",
        "defense": 40,
        "mana_boost": 50,
        "price": 12000,
        "level_requirement": 40,
        "rarity": "legendary",
        "category": "armor",
        "description": "Blessed by celestial beings"
    },
    "weapon_006": {
        "id": "weapon_006",
        "name": "The Last Echo",
        "attack": 50,
        "defense": 25,
        "price": 15000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "Great Axe that echoes with the power of fallen heroes",
        "effect": "+25% XP gain, +30% boss damage"
    },
    "weapon_007": {
        "id": "weapon_007",
        "name": "Chrono Weave",
        "attack": 45,
        "defense": 20,
        "price": 12000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "A weapon that weaves through time itself",
        "effect": "Time manipulation abilities"
    },
    "weapon_008": {
        "id": "weapon_008",
        "name": "The Paradox Core",
        "attack": 60,
        "defense": 30,
        "price": 25000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "Crystal Staff containing the essence of paradox",
        "effect": "Reality manipulation powers"
    },
    "armor_005": {
        "id": "armor_005",
        "name": "Celestial Robes",
        "defense": 25,
        "price": 4000,
        "rarity": "legendary",
        "category": "armor",
        "description": "Robes blessed by celestial beings"
    },
    "item_007": {
        "id": "item_007",
        "name": "Lootbox",
        "effect": "random_reward",
        "price": 1000,
        "rarity": "rare",
        "category": "consumables",
        "description": "Contains random rewards including rare items"
    }
}

# Rarity System
RARITY_COLORS = {
    "common": 0x9E9E9E,      # Gray
    "uncommon": 0x4CAF50,    # Green
    "rare": 0x2196F3,        # Blue
    "epic": 0x9C27B0,        # Purple
    "legendary": 0xFF9800,   # Orange
    "mythic": 0xF44336,      # Red
    "divine": 0xFFD700,      # Gold
    "omnipotent": 0xFF1493   # Deep Pink
}

RARITY_WEIGHTS = {
    "common": 0.50,      # 50%
    "uncommon": 0.25,    # 25%
    "rare": 0.15,        # 15%
    "epic": 0.07,        # 7%
    "legendary": 0.025,  # 2.5%
    "mythic": 0.004,     # 0.4%
    "divine": 0.001,     # 0.1%
    "omnipotent": 0.0001 # 0.01%
}

# Luck Levels
LUCK_LEVELS = {
    'cursed': {'min': -1000, 'max': -100, 'emoji': '💀', 'bonus_percent': -25},
    'unlucky': {'min': -99, 'max': -1, 'emoji': '😰', 'bonus_percent': -10},
    'normal': {'min': 0, 'max': 99, 'emoji': '😐', 'bonus_percent': 0},
    'lucky': {'min': 100, 'max': 499, 'emoji': '😊', 'bonus_percent': 15},
    'blessed': {'min': 500, 'max': 999, 'emoji': '✨', 'bonus_percent': 30},
    'divine': {'min': 1000, 'max': 9999, 'emoji': '🌟', 'bonus_percent': 50}
}

# Weapons organized by class and rarity
WEAPONS = {
    # Warrior Weapons
    "Iron Petal": {
        "attack": 12,
        "defense": 4,
        "rarity": "common",
        "class_req": "warrior",
        "level_requirement": 5
    },
    "Guardian's Might": {
        "attack": 25,
        "defense": 15,
        "rarity": "epic",
        "class_req": "warrior",
        "level_requirement": 20
    },

    # Mage Weapons
    "Apprentice Wand": {
        "attack": 15,
        "mana_boost": 20,
        "rarity": "common",
        "class_req": "mage",
        "level_requirement": 5
    },
    "Archmage Staff": {
        "attack": 35,
        "mana_boost": 50,
        "rarity": "legendary",
        "class_req": "mage",
        "level_requirement": 30
    },
    "The Last Echo": {
        "attack": 50,
        "defense": 10,
        "rarity": "mythic",
        "class_req": "any",
        "special": "legendary_bonus",
        "xp_gain": 25,
        "boss_damage": 30,
        "unlock_condition": "paradox_realm_boss"
    },
    "The Paradox Core": {
        "attack": 40,
        "defense": 8,
        "rarity": "mythic",
        "class_req": "any",
        "special": "randomized_boost",
        "random_stat_chance": 50,
        "random_stat_boost": 15,
        "unlock_condition": "paradox_chamber"
    },

    # Add more weapons as needed...
}

# Armor with level requirements
ARMOR = {
    "Leather Vest": {
        "defense": 8,
        "rarity": "common",
        "level_requirement": 1
    },
    "Iron Chestplate": {
        "defense": 18,
        "rarity": "uncommon",
        "level_requirement": 8
    },
    "Dragon Scale Armor": {
        "defense": 40,
        "rarity": "legendary",
        "level_requirement": 35
    },
    "Leather Vest": {
        "defense": 8,
        "rarity": "common",
        "class_req": "any"
    },
    "Iron Chestplate": {
        "defense": 15,
        "rarity": "uncommon",
        "class_req": "warrior"
    },
    "Mage Robes": {
        "defense": 5,
        "mana_boost": 20,
        "rarity": "uncommon",
        "class_req": "mage"
    },
    "Shadow Cloak": {
        "defense": 10,
        "stealth_bonus": 15,
        "rarity": "rare",
        "class_req": "rogue"
    },
    "Ranger's Coat": {
        "defense": 12,
        "range_bonus": 10,
        "rarity": "rare",
        "class_req": "archer"
    },
    "Holy Vestments": {
        "defense": 8,
        "healing_bonus": 25,
        "rarity": "epic",
        "class_req": "healer"
    },
    "Temporal Armor": {
        "defense": 20,
        "time_resistance": 50,
        "rarity": "legendary",
        "class_req": "chrono_weave"
    }
}

# Omnipotent Items (existing)
OMNIPOTENT_ITEM = {
    "Reality Stone": {
        "rarity": "omnipotent",
        "special": "wish_any_item",
        "description": "Can grant any item except World Ender",
        "level_requirement": 50
    },
    "Reality Stone": {
        "rarity": "omnipotent",
        "special": "wish_any_item",
        "description": "Can grant any item except World Ender"
    }
}

# Adventure locations with level gates
ADVENTURE_LOCATIONS = {
    'training': {
        'name': 'Training Grounds',
        'level_requirement': 1,
        'description': 'Safe practice area for beginners',
        'rewards': {'coins': (10, 30), 'xp': (5, 15)}
    },
    'forest': {
        'name': 'Peaceful Forest',
        'level_requirement': 3,
        'description': 'Woods with small creatures',
        'rewards': {'coins': (30, 70), 'xp': (15, 35)}
    },
    'mountains': {
        'name': 'Dangerous Mountains',
        'level_requirement': 8,
        'description': 'Treacherous peaks',
        'rewards': {'coins': (60, 120), 'xp': (30, 60)}
    },
    'dungeon': {
        'name': 'Ancient Dungeon',
        'level_requirement': 15,
        'description': 'Dark underground chambers',
        'rewards': {'coins': (100, 200), 'xp': (50, 100)}
    },
    'dragon_lair': {
        'name': 'Dragon Lair',
        'level_requirement': 25,
        'description': 'Legendary dragon domain',
        'rewards': {'coins': (200, 500), 'xp': (100, 250)}
    },
    'paris_streets': {
        'name': 'Streets of Paris',
        'description': 'The familiar streets where miraculous holders patrol',
        'level_range': (1, 10),
        'monsters': ['akuma_victim', 'sentimonster'],
        'resources': ['city_materials', 'tourist_coins']
    },
    'cheese_dimension': {
        'name': 'Plagg\'s Cheese Dimension',
        'description': 'A realm made entirely of different cheeses',
        'level_range': (15, 30),
        'monsters': ['cheese_golem', 'cheddar_spirit'],
        'resources': ['aged_cheese', 'mystical_dairy']
    },
    'kwami_realm': {
        'name': 'The Kwami Realm',
        'description': 'The mystical home dimension of all kwamis',
        'level_range': (25, 50),
        'monsters': ['rogue_kwami', 'guardian_spirit'],
        'resources': ['kwami_essence', 'miraculous_energy']
    }
}

# PvP Arenas with level requirements
PVP_ARENAS = {
    'training_ground': {
        'name': 'Training Ground',
        'description': 'Safe practice arena for beginners',
        'entry_fee': 0,
        'level_requirement': 5,
        'winner_multiplier': 1.2,
        'special_effects': []
    },
    'colosseum': {
        'name': 'Colosseum',
        'description': 'Classic gladiator arena',
        'entry_fee': 100,
        'level_requirement': 10,
        'winner_multiplier': 1.8,
        'special_effects': ['crowd_boost']
    },
    'dragon_pit': {
        'name': 'Dragon Pit',
        'description': 'Dangerous arena with fire hazards',
        'entry_fee': 500,
        'level_requirement': 20,
        'winner_multiplier': 2.5,
        'special_effects': ['fire_damage', 'dragon_roar']
    },
    'cheese_pit': {
        'name': 'The Cheese Pit',
        'description': 'Battle in a pit filled with molten cheese',
        'entry_fee': 100,
        'winner_multiplier': 1.8,
        'special_effects': ['cheese_slick', 'heat_damage'],
        'map_effects': {
            'cheese_slick': 'Random chance to slip and lose turn',
            'heat_damage': 'Gradual HP loss over time'
        }
    },
    'miraculous_arena': {
        'name': 'Miraculous Colosseum',
        'description': 'The grand arena where heroes prove their worth',
        'entry_fee': 500,
        'winner_multiplier': 2.5,
        'special_effects': ['power_boost', 'audience_buff'],
        'map_effects': {
            'power_boost': 'All attacks deal 25% more damage',
            'audience_buff': 'Gain energy faster from crowd cheers'
        }
    },
    'kwami_realm': {
        'name': 'Kwami Dimension',
        'description': 'Fight in the ethereal realm of the kwamis',
        'entry_fee': 1000,
        'winner_multiplier': 3.0,
        'special_effects': ['gravity_shift', 'magic_amplification'],
        'map_effects': {
            'gravity_shift': 'Movement abilities have different effects',
            'magic_amplification': 'Special attacks cost less energy'
        }
    },
    'shadow_realm': {
        'name': 'Shadow Realm',
        'description': 'A dark dimension where only the strongest survive',
        'entry_fee': 2000,
        'winner_multiplier': 4.0,
        'special_effects': ['shadow_clones', 'darkness_boost'],
        'map_effects': {
            'shadow_clones': 'Attacks may hit shadow copies',
            'darkness_boost': 'Stealth attacks more effective'
        }
    }
}

def get_all_shop_items():
    """Get all shop items organized by level"""
    return SHOP_ITEMS

def get_items_by_level(min_level: int, max_level: int = 999):
    """Get items available for a level range"""
    return {
        item_id: item_data
        for item_id, item_data in SHOP_ITEMS.items()
        if min_level <= item_data.get('level_requirement', 1) <= max_level
    }

def get_items_by_rarity(rarity_filter):
    """Get items by rarity"""
    if isinstance(rarity_filter, str):
        rarity_filter = [rarity_filter]

    return {
        item_id: item_data
        for item_id, item_data in SHOP_ITEMS.items()
        if item_data.get("rarity") in rarity_filter
    }

# Daily Rewards
DAILY_REWARDS = {
    'base': 100,
    'level_multiplier': 10,
    'streak_bonus': 25,
    'max_streak': 7
}

# Status Effects
STATUS_EFFECTS = {
    'blessed': {'duration': 1800, 'effects': {'luck_bonus': 100, 'xp_bonus': 1.2}},
    'cursed': {'duration': 1800, 'effects': {'luck_penalty': -50, 'damage_penalty': 0.8}},
    'cheese_power': {'duration': 600, 'effects': {'attack_bonus': 1.3, 'cheese_immunity': True}},
    'kwami_protection': {'duration': 900, 'effects': {'defense_bonus': 1.5, 'magic_resistance': 0.5}}
}

# World Locations with cheese theme
WORLD_LOCATIONS = {
    'paris_streets': {
        'name': 'Streets of Paris',
        'description': 'The familiar streets where miraculous holders patrol',
        'level_range': (1, 10),
        'monsters': ['akuma_victim', 'sentimonster'],
        'resources': ['city_materials', 'tourist_coins']
    },
    'cheese_dimension': {
        'name': 'Plagg\'s Cheese Dimension',
        'description': 'A realm made entirely of different cheeses',
        'level_range': (15, 30),
        'monsters': ['cheese_golem', 'cheddar_spirit'],
        'resources': ['aged_cheese', 'mystical_dairy']
    },
    'kwami_realm': {
        'name': 'The Kwami Realm',
        'description': 'The mystical home dimension of all kwamis',
        'level_range': (25, 50),
        'monsters': ['rogue_kwami', 'guardian_spirit'],
        'resources': ['kwami_essence', 'miraculous_energy']
    }
}

# Enhanced Battle System
BATTLE_MECHANICS = {
    'energy_system': {
        'max_energy': 100,
        'energy_regen': 25,
        'action_costs': {
            'attack': 20,
            'defend': 15,
            'special': 40,
            'item': 0
        }
    },
    'status_effects': {
        'stunned': {'duration': 1, 'effect': 'skip_turn'},
        'defense_boost': {'duration': 1, 'effect': 'reduce_damage_50'},
        'poison': {'duration': 3, 'effect': 'damage_over_time'},
        'regen': {'duration': 3, 'effect': 'heal_over_time'},
        'berserk': {'duration': 2, 'effect': 'double_damage'}
    },
    'critical_hit': {
        'base_chance': 0.15,
        'damage_multiplier': 1.5
    }
}

# New Monsters with Enhanced AI
ENHANCED_MONSTERS = {
    'Slime': {
        'hp': 60,
        'attack': 8,
        'defense': 3,
        'special_abilities': ['regeneration'],
        'ai_behavior': 'defensive',
        'rewards': {'coins': (20, 40), 'xp': (10, 20)}
    },
    'Goblin_Warrior': {
        'hp': 80,
        'attack': 12,
        'defense': 6,
        'special_abilities': ['weapon_throw', 'battle_cry'],
        'ai_behavior': 'aggressive',
        'rewards': {'coins': (30, 60), 'xp': (15, 30)}
    },
    'Shadow_Assassin': {
        'hp': 70,
        'attack': 18,
        'defense': 4,
        'special_abilities': ['stealth_attack', 'poison_blade'],
        'ai_behavior': 'tactical',
        'rewards': {'coins': (50, 90), 'xp': (25, 45)}
    },
    'Crystal_Golem': {
        'hp': 150,
        'attack': 15,
        'defense': 20,
        'special_abilities': ['crystal_spike', 'armor_repair'],
        'ai_behavior': 'tank',
        'rewards': {'coins': (80, 120), 'xp': (40, 60)}
    },
    'Fire_Elemental': {
        'hp': 90,
        'attack': 20,
        'defense': 8,
        'special_abilities': ['fire_blast', 'burn_aura'],
        'ai_behavior': 'elemental',
        'rewards': {'coins': (60, 100), 'xp': (30, 50)}
    }
}

# New Items and Equipment
ENHANCED_WEAPONS = {
    'Cheese_Blade': {
        'name': 'Blade of Aged Cheese',
        'attack': 25,
        'rarity': 'epic',
        'special': 'cheese_slice',
        'description': 'A sword forged from the finest aged cheese, sharp enough to cut through reality.',
        'price': 5000,
        'category': 'weapons'
    },
    'Miraculous_Staff': {
        'name': 'Staff of Miracles',
        'attack': 30,
        'rarity': 'legendary',
        'special': 'miracle_cast',
        'description': 'A staff imbued with the power of all kwamis.',
        'price': 10000,
        'category': 'weapons'
    },
    'Destruction_Gauntlets': {
        'name': 'Gauntlets of Destruction',
        'attack': 35,
        'rarity': 'mythic',
        'special': 'cataclysm',
        'description': 'Gloves that channel the power of destruction itself.',
        'price': 20000,
        'category': 'weapons'
    }
}

# New Consumables
ENHANCED_CONSUMABLES = {
    'Camembert_Deluxe': {
        'name': 'Deluxe Camembert',
        'effect': 'full_heal_and_buff',
        'description': 'Plaggs favorite cheese that fully heals and provides temporary buffs.',
        'price': 500,
        'category': 'consumables'
    },
    'Kwami_Energy_Drink': {
        'name': 'Kwami Energy Drink',
        'effect': 'restore_energy',
        'description': 'A magical drink that restores all energy.',
        'price': 300,
        'category': 'consumables'
    },
    'Lucky_Charm_Scroll': {
        'name': 'Lucky Charm Scroll',
        'effect': 'summon_lucky_charm',
        'description': 'Creates a random useful item for the current situation.',
        'price': 1000,
        'category': 'consumables'
    }
}

# Adventure Locations with Enhanced Mechanics
ENHANCED_LOCATIONS = {
    'cheese_caves': {
        'name': 'Ancient Cheese Caves',
        'description': 'Deep caves filled with ancient cheese deposits and dangerous creatures.',
        'difficulty': 'medium',
        'encounters': {
            'cheese_golem': 0.3,
            'cave_spider': 0.25,
            'treasure_chest': 0.2,
            'cheese_fountain': 0.15,
            'secret_passage': 0.1
        },
        'environmental_effects': ['low_light', 'cheese_aroma']
    },
    'kwami_dimension': {
        'name': 'Kwami Dimension',
        'description': 'A mystical realm where kwamis reside.',
        'difficulty': 'hard',
        'encounters': {
            'guardian_kwami': 0.2,
            'energy_crystal': 0.25,
            'dimensional_rift': 0.2,
            'ancient_relic': 0.15,
            'kwami_blessing': 0.2
        },
        'environmental_effects': ['magic_amplification', 'time_dilation']
    },
    'paris_rooftops': {
        'name': 'Paris Rooftops',
        'description': 'The rooftops of Paris where heroes patrol.',
        'difficulty': 'easy',
        'encounters': {
            'akuma_victim': 0.3,
            'police_chase': 0.2,
            'civilian_rescue': 0.25,
            'hidden_cache': 0.15,
            'view_point': 0.1
        },
        'environmental_effects': ['wind_boost', 'city_lights']
    }
}

# Guild System
GUILD_FEATURES = {
    'max_members': 20,
    'ranks': ['Member', 'Elite', 'Officer', 'Leader'],
    'benefits': {
        'exp_bonus': 0.1,
        'coin_bonus': 0.05,
        'guild_shop': True,
        'guild_battles': True
    },
    'upgrade_costs': {
        'exp_boost': 10000,
        'coin_boost': 15000,
        'member_slots': 5000,
        'guild_hall': 50000
    }
}

# Achievement System
ACHIEVEMENTS = {
    'first_steps': {
        'name': 'First Steps',
        'description': 'Complete your first adventure',
        'requirement': {'type': 'adventure_count', 'value': 1},
        'reward': {'coins': 100, 'xp': 50},
        'rarity': 'common'
    },
    'cheese_lover': {
        'name': 'Cheese Lover',
        'description': 'Consume 50 cheese-related items',
        'requirement': {'type': 'cheese_consumed', 'value': 50},
        'reward': {'coins': 1000, 'title': 'Cheese Connoisseur'},
        'rarity': 'uncommon'
    },
    'battle_master': {
        'name': 'Battle Master',
        'description': 'Win 100 battles',
        'requirement': {'type': 'battles_won', 'value': 100},
        'reward': {'coins': 5000, 'weapon': 'Champion_Sword'},
        'rarity': 'rare'
    },
    'kwami_chosen': {
        'name': 'Chosen by Kwami',
        'description': 'Reach level 50 with a miraculous equipped',
        'requirement': {'type': 'level_with_miraculous', 'value': 50},
        'reward': {'coins': 10000, 'title': 'Kwami Champion', 'special_ability': True},
        'rarity': 'legendary'
    }
}

# Enhanced PvP Arenas
PVP_ARENAS = {
    'cheese_pit': {
        'name': 'The Cheese Pit',
        'description': 'Battle in a pit filled with molten cheese',
        'entry_fee': 100,
        'winner_multiplier': 1.8,
        'special_effects': ['cheese_slick', 'heat_damage'],
        'map_effects': {
            'cheese_slick': 'Random chance to slip and lose turn',
            'heat_damage': 'Gradual HP loss over time'
        }
    },
    'miraculous_arena': {
        'name': 'Miraculous Colosseum',
        'description': 'The grand arena where heroes prove their worth',
        'entry_fee': 500,
        'winner_multiplier': 2.5,
        'special_effects': ['power_boost', 'audience_buff'],
        'map_effects': {
            'power_boost': 'All attacks deal 25% more damage',
            'audience_buff': 'Gain energy faster from crowd cheers'
        }
    },
    'kwami_realm': {
        'name': 'Kwami Dimension',
        'description': 'Fight in the ethereal realm of the kwamis',
        'entry_fee': 1000,
        'winner_multiplier': 3.0,
        'special_effects': ['gravity_shift', 'magic_amplification'],
        'map_effects': {
            'gravity_shift': 'Movement abilities have different effects',
            'magic_amplification': 'Special attacks cost less energy'
        }
    },
    'shadow_realm': {
        'name': 'Shadow Realm',
        'description': 'A dark dimension where only the strongest survive',
        'entry_fee': 2000,
        'winner_multiplier': 4.0,
        'special_effects': ['shadow_clones', 'darkness_boost'],
        'map_effects': {
            'shadow_clones': 'Attacks may hit shadow copies',
            'darkness_boost': 'Stealth attacks more effective'
        }
    }
}

# Daily Challenges
DAILY_CHALLENGES = {
    'monday': {
        'name': 'Monster Monday',
        'description': 'Defeat 5 monsters',
        'requirement': {'type': 'monsters_defeated', 'value': 5},
        'reward': {'coins': 500, 'xp': 200}
    },
    'tuesday': {
        'name': 'Treasure Tuesday',
        'description': 'Find 3 treasure chests',
        'requirement': {'type': 'treasures_found', 'value': 3},
        'reward': {'coins': 750, 'item': 'random_rare'}
    },
    'wednesday': {
        'name': 'Work Wednesday',
        'description': 'Complete 10 work sessions',
        'requirement': {'type': 'work_completed', 'value': 10},
        'reward': {'coins': 1000, 'luck_points': 100}
    },
    'thursday': {
        'name': 'Training Thursday',
        'description': 'Use 20 training points',
        'requirement': {'type': 'training_points_used', 'value': 20},
        'reward': {'stat_points': 5, 'xp': 300}
    },
    'friday': {
        'name': 'Fight Friday',
        'description': 'Win 3 PvP battles',
        'requirement': {'type': 'pvp_wins', 'value': 3},
        'reward': {'coins': 1500, 'title': 'Weekend Warrior'}
    },
    'saturday': {
        'name': 'Shopping Saturday',
        'description': 'Buy 5 items from the shop',
        'requirement': {'type': 'items_purchased', 'value': 5},
        'reward': {'coins': 800, 'shop_discount': 0.2}
    },
    'sunday': {
        'name': 'Social Sunday',
        'description': 'Help 3 other players',
        'requirement': {'type': 'players_helped', 'value': 3},
        'reward': {'coins': 600, 'friendship_points': 50}
    }
}

# Seasonal Events
SEASONAL_EVENTS = {
    'cheese_festival': {
        'name': 'Great Cheese Festival',
        'description': 'Plagg celebrates with a cheese extravaganza!',
        'duration': 7,  # days
        'bonuses': {
            'exp_multiplier': 2.0,
            'coin_multiplier': 1.5,
            'cheese_drop_rate': 3.0
        },
        'special_shop': ['Golden_Cheese', 'Cheese_Crown', 'Camembert_Armor'],
        'special_quests': ['cheese_collector', 'cheese_master', 'cheese_legend']
    },
    'miraculous_awakening': {
        'name': 'Miraculous Awakening',
        'description': 'The power of miracles grows stronger!',
        'duration': 10,  # days
        'bonuses': {
            'miraculous_power': 2.0,
            'special_ability_cooldown': 0.5,
            'rare_drop_rate': 2.0
        },
        'special_shop': ['Ladybug_Earrings', 'Cat_Ring', 'Turtle_Bracelet'],
        'special_quests': ['miracle_seeker', 'hero_training', 'kwami_bond']
    }
}

# Legacy System
LEGACY_MODIFIERS = {
    'blessed_by_cheese': {
        'name': 'Blessed by Cheese',
        'description': 'Plagg smiles upon you',
        'effects': {'xp_bonus': 0.1, 'luck_bonus': 50},
        'rarity': 'rare'
    },
    'descendant_of_heroes': {
        'name': 'Descendant of Heroes',
        'description': 'Hero blood flows through your veins',
        'effects': {'stat_bonus': 5, 'skill_cooldown_reduction': 0.1},
        'rarity': 'epic'
    },
    'kwami_chosen': {
        'name': 'Chosen by Kwami',
        'description': 'A kwami has chosen you as their champion',
        'effects': {'mana_bonus': 50, 'special_abilities': True},
        'rarity': 'legendary'
    },
    'destruction_master': {
        'name': 'Master of Destruction',
        'description': 'You have mastered the power of destruction',
        'effects': {'destruction_bonus': 0.5, 'cataclysm_power': True},
        'rarity': 'mythic'
    }
}