
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Dict, Any
import logging

from config import COLORS, get_server_config, is_module_enabled
from utils.helpers import create_embed

logger = logging.getLogger(__name__)

class HelpView(discord.ui.View):
    """Progressive help system organized by player advancement."""

    def __init__(self, bot, user: discord.Member):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.current_category = "getting_started"

    @discord.ui.select(
        placeholder="Select help category...",
        options=[
            discord.SelectOption(label="🚀 Getting Started", value="getting_started", emoji="🚀"),
            discord.SelectOption(label="⚔️ Combat & Classes", value="combat", emoji="⚔️"),
            discord.SelectOption(label="🛒 Equipment & Shop", value="equipment", emoji="🛒"),
            discord.SelectOption(label="🏰 Advanced Features", value="advanced", emoji="🏰"),
            discord.SelectOption(label="🤖 AI Chatbot", value="ai", emoji="🤖"),
            discord.SelectOption(label="🛡️ Moderation", value="moderation", emoji="🛡️")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Change help category."""
        if interaction.user != self.user:
            await interaction.response.send_message("This help menu is not for you!", ephemeral=True)
            return

        self.current_category = select.values[0]
        embed = self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_help_embed(self) -> discord.Embed:
        """Create organized help embed."""
        embed = discord.Embed(
            title=f"📚 Plagg's Adventure Guide",
            color=COLORS['primary']
        )

        if self.current_category == "getting_started":
            embed.description = "🌟 **New to the adventure? Start here!**"
            
            embed.add_field(
                name="🎯 First Steps",
                value="1️⃣ **`/start`** - Begin your RPG adventure\n"
                      "2️⃣ **`$adventure`** - Explore Training Grounds\n"
                      "3️⃣ **`$profile`** - Check your progress\n"
                      "4️⃣ **`$shop`** - Buy basic equipment",
                inline=False
            )
            
            embed.add_field(
                name="📈 Early Progression (Levels 1-5)",
                value="• **Goal:** Reach Level 5 to choose your class\n"
                      "• **How:** Use `$adventure` repeatedly\n"
                      "• **Where:** Start with Training Grounds\n"
                      "• **Buy:** Basic weapons from Beginner Gear shop\n"
                      "• **Tip:** Each adventure gives XP and coins!",
                inline=False
            )
            
            embed.add_field(
                name="🎭 Choose Your Path (Level 5)",
                value="**`$class`** - Select your class:\n"
                      "• **Warrior** (Tank) - High HP and defense\n"
                      "• **Mage** (Magic) - Powerful spells and mana\n"
                      "• **Rogue** (Stealth) - High damage and crits\n"
                      "• **Archer** (Ranged) - Balanced ranged combat\n"
                      "• **Healer** (Support) - Healing and buffs",
                inline=False
            )

        elif self.current_category == "combat":
            embed.description = "⚔️ **Master combat and class abilities!**"
            
            embed.add_field(
                name="🎯 Class System",
                value="**`$class`** - Choose your class (Level 5 required)\n"
                      "**`$skills`** - View your abilities\n"
                      "**`$battle`** - Fight monsters for practice\n\n"
                      "**Class Unlocks:**\n"
                      "🔓 Level 5: Class selection\n"
                      "🔓 Level 10: Advanced skills\n"
                      "🔓 Level 20: Master abilities",
                inline=False
            )
            
            embed.add_field(
                name="⚔️ Combat Features",
                value="**`$pvp <user>`** - Challenge players (Level 5+)\n"
                      "**`$battle`** - Fight AI monsters\n"
                      "**`$heal`** - Restore HP for 50 coins\n\n"
                      "**PvP Unlocks:**\n"
                      "🔓 Level 5: Basic PvP\n"
                      "🔓 Level 15: Advanced arenas\n"
                      "🔓 Level 25: Championship battles",
                inline=False
            )

        elif self.current_category == "equipment":
            embed.description = "🛒 **Gear up for your adventures!**"
            
            embed.add_field(
                name="🏪 Progressive Shop",
                value="**`$shop`** - Browse equipment by level\n"
                      "**`$buy <item>`** - Purchase specific items\n"
                      "**`$inventory`** - View your items\n"
                      "**`$equip <item>`** - Equip weapons/armor\n"
                      "**`$use <item>`** - Use consumables",
                inline=False
            )
            
            embed.add_field(
                name="📊 Shop Categories",
                value="**🗡️ Beginner Gear** (Level 1+) - Basic equipment\n"
                      "**🧪 Combat Supplies** (Level 5+) - Potions\n"
                      "**⚔️ Advanced Gear** (Level 10+) - Better equipment\n"
                      "**🌟 Class Weapons** (Level 15+) - Specialized gear\n"
                      "**💎 Rare Items** (Level 25+) - Lootboxes & rares\n"
                      "**🏆 Legendary** (Level 40+) - Epic equipment",
                inline=False
            )
            
            embed.add_field(
                name="💰 Economy Commands",
                value="**`$work`** - Earn coins through jobs\n"
                      "**`$daily`** - Claim daily rewards\n"
                      "**`$pay <user> <amount>`** - Transfer coins\n"
                      "**`$balance`** - Check your coins",
                inline=False
            )

        elif self.current_category == "advanced":
            embed.description = "🏰 **Unlock endgame content and features!**"
            
            embed.add_field(
                name="🔓 Feature Unlocks by Level",
                value="**Level 10:** 🔨 Professions & Crafting\n"
                      "**Level 15:** 🏰 Dungeons & Raids\n"
                      "**Level 20:** 🏛️ Factions & Guilds\n"
                      "**Level 25:** 🎁 Lootboxes & Rare Items\n"
                      "**Level 30:** 🏛️ Auction House Trading\n"
                      "**Level 40:** 🌟 Legendary Equipment",
                inline=False
            )
            
            embed.add_field(
                name="🔨 Crafting System",
                value="**`$profession`** - Choose crafting skill (Level 10+)\n"
                      "**`$craft <recipe>`** - Create items\n"
                      "**`$gather <location>`** - Collect materials\n"
                      "**`$materials`** - View crafting resources",
                inline=False
            )
            
            embed.add_field(
                name="🏰 Endgame Content",
                value="**`$dungeon`** - Multi-floor exploration (Level 15+)\n"
                      "**`$faction <name>`** - Join organizations (Level 20+)\n"
                      "**`$lootbox`** - Open for rare rewards (Level 25+)\n"
                      "**`$auction`** - Player trading (Level 30+)",
                inline=False
            )

        elif self.current_category == "ai":
            embed.description = "🤖 **Chat with Plagg, the AI companion!**"
            
            embed.add_field(
                name="💬 AI Features",
                value="• **Just mention me!** - @Plagg to start chatting\n"
                      "• **`/chat <message>`** - Direct AI conversation\n"
                      "• **`/clear_chat`** - Reset conversation history\n"
                      "• **Memory:** I remember our previous chats!\n"
                      "• **Personality:** Sarcastic and fun responses",
                inline=False
            )
            
            embed.add_field(
                name="🧀 Plagg's Personality",
                value="I'm the Kwami of Destruction with a love for cheese!\n"
                      "• Sarcastic and playful responses\n"
                      "• Cheese-related jokes and references\n"
                      "• Helpful but with attitude\n"
                      "• Remembers context from our chats",
                inline=False
            )

        elif self.current_category == "moderation":
            embed.description = "🛡️ **Server management tools (Moderators only)**"
            
            embed.add_field(
                name="⚒️ Basic Moderation",
                value="**`/kick <user>`** - Remove user from server\n"
                      "**`/ban <user>`** - Permanently ban user\n"
                      "**`/warn <user>`** - Issue warning\n"
                      "**`/timeout <user>`** - Temporary mute\n"
                      "**`/purge <amount>`** - Delete messages",
                inline=False
            )
            
            embed.add_field(
                name="📊 Moderation Info",
                value="**`/warnings <user>`** - View user warnings\n"
                      "**`/clear_warns <user>`** - Clear warnings\n"
                      "**`/modlogs`** - View moderation history\n"
                      "**`/config`** - Server configuration",
                inline=False
            )

        # Add progression tips at bottom
        if self.current_category in ["getting_started", "combat", "equipment"]:
            embed.add_field(
                name="💡 Quick Tips",
                value="• Use `$profile` to track your progression\n"
                      "• Higher level areas give better rewards\n"
                      "• Equipment from shop scales with your level\n"
                      "• Each feature unlocks at specific levels",
                inline=False
            )

        embed.set_footer(text="🧀 Made by Plagg | Use the dropdown to explore different topics!")
        return embed

class HelpCog(commands.Cog):
    """User-friendly help system."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', help='Show organized help information')
    async def help_command(self, ctx, category: Optional[str] = None):
        """Show help information."""
        view = HelpView(self.bot, ctx.author)
        
        if category:
            valid_categories = ["getting_started", "combat", "equipment", "advanced", "ai", "moderation"]
            if category.lower() in valid_categories:
                view.current_category = category.lower()
        
        embed = view.create_help_embed()
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Show organized help information")
    @app_commands.describe(category="Specific category to view (optional)")
    async def help_slash(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Show help information (slash command)."""
        view = HelpView(self.bot, interaction.user)

        if category:
            valid_categories = ["getting_started", "combat", "equipment", "advanced", "ai", "moderation"]
            if category.lower() in valid_categories:
                view.current_category = category.lower()

        embed = view.create_help_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="quickstart", description="Quick guide for new players")
    async def quickstart_slash(self, interaction: discord.Interaction):
        """Quick start guide for new players."""
        embed = discord.Embed(
            title="🚀 Quick Start Guide",
            description="**Get started in 4 easy steps!**",
            color=COLORS['success']
        )

        embed.add_field(
            name="Step 1: Start Your Adventure",
            value="Use **`/start`** to create your character",
            inline=False
        )

        embed.add_field(
            name="Step 2: Explore",
            value="Use **`$adventure`** to gain XP and coins\nStart with Training Grounds!",
            inline=False
        )

        embed.add_field(
            name="Step 3: Get Gear",
            value="Use **`$shop`** to buy better equipment\nCheck Beginner Gear first!",
            inline=False
        )

        embed.add_field(
            name="Step 4: Choose Class",
            value="At Level 5, use **`$class`** to specialize\nPick Warrior, Mage, Rogue, Archer, or Healer!",
            inline=False
        )

        embed.add_field(
            name="💡 Next Steps",
            value="• Keep adventuring to unlock new areas\n"
                  "• Use `$profile` to track progress\n"
                  "• Try `$pvp` at Level 5 for player combat\n"
                  "• Unlock crafting at Level 10!",
            inline=False
        )

        embed.set_footer(text="🧀 Need more help? Use /help for detailed guides!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Show bot information")
    async def info_slash(self, interaction: discord.Interaction):
        """Show bot information."""
        embed = discord.Embed(
            title="🧀 Plagg - Your Adventure Companion",
            description="**Progressive RPG system with AI chatbot features!**",
            color=COLORS['primary']
        )

        embed.add_field(
            name="🎮 Progressive RPG",
            value="• **6 Classes** with unique abilities\n"
                  "• **Level-based progression** system\n"
                  "• **30+ weapons** and equipment\n"
                  "• **Meaningful advancement** with unlocks\n"
                  "• **Balanced gameplay** requiring strategy",
            inline=True
        )

        embed.add_field(
            name="🤖 AI Chatbot",
            value="• **Smart conversations** with context\n"
                  "• **Plagg's personality** - sarcastic & fun\n"
                  "• **Memory system** remembers chats\n"
                  "• **Google Gemini** powered responses\n"
                  "• **Just mention me** to start chatting!",
            inline=True
        )

        embed.add_field(
            name="📈 Server Stats",
            value=f"• **Guilds:** {len(self.bot.guilds)}\n"
                  f"• **Users:** {len(self.bot.users)}\n"
                  f"• **Commands:** {len(self.bot.commands)}\n"
                  f"• **Latency:** {round(self.bot.latency * 1000, 2)}ms",
            inline=True
        )

        embed.add_field(
            name="🌟 Key Features",
            value="✅ Progressive level-gated content\n"
                  "✅ Meaningful equipment upgrades\n"
                  "✅ Strategic combat system\n"
                  "✅ Crafting and professions\n"
                  "✅ PvP and dungeon systems\n"
                  "✅ AI conversation companion",
            inline=False
        )

        embed.set_footer(text="🧀 Made with cheese and code | Use /quickstart to begin!")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(HelpCog(bot))
