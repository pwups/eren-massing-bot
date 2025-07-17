import discord
from discord.ext import commands
from keep_alive import keep_alive
from discord import app_commands
from discord import Interaction
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="e?", intents=intents)

# IDs
CATEGORY_ID = 1372050909332373624
TARGET_CHANNEL_ID_NOTIFICATION = 1371876364457873509
TARGET_CHANNEL_ID_DONE = 1371876390856818718
TARGET_CHANNEL_ID_TICKET = 1371876418019135518
REQUIRED_ROLE_ID = 1372051652952981636

# Colors
DARK_GRAY = discord.Color.from_str("#20202A")
BLUE = discord.Color.from_str("#455F5B")

# ----- Lose Modal -----
class BreathingModal(discord.ui.Modal, title="₊　˙ㅤinfo"):
    server_ad = discord.ui.TextInput(
        label="ㅤ❀ ㅤ ⊹˚ㅤserverㅤad",
        placeholder="ㅤ.ㅤno spoiler walls",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )
    invite_link = discord.ui.TextInput(
        label="ㅤ❀ ㅤ ⊹˚ㅤinviteㅤlink",
        placeholder="ㅤ.ㅤNO vanities",
        style=discord.TextStyle.short,
        required=True,
        max_length=200,
    )
    type_info = discord.ui.TextInput(
        label="ㅤ❀ ㅤ ⊹˚ㅤpaidㅤtype",
        placeholder="ㅤ.ㅤpoint or invite?",
        style=discord.TextStyle.short,
        required=True,
        max_length=100,
    )

    def __init__(self, original_message):
        super().__init__()
        self.original_message = original_message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        thread = await self.original_message.create_thread(name="⁺  .  ♡  ⁺  .")
        embed = discord.Embed(description=f"```{self.server_ad.value}```", color=DARK_GRAY)
        await thread.send(content=self.server_ad.value, embed=embed)
        await thread.send(self.invite_link.value)
        await thread.send(f"# <:reply001:1372053721256693834> {self.type_info.value}")
        await interaction.followup.send(
            "_ _\n\n\n                  **wait   for   approval** <a:eren3:1372039132888694896>\n                   *do  not  ping  anyone.*\n\n\n_ _",
        )

class ClickButton(discord.ui.View):
    def __init__(self, original_message=None):
        super().__init__(timeout=None)
        self.original_message = original_message

    @discord.ui.button(label="ㅤclickㅤ⠀‿︵⠀⠀ㅤ⟡ㅤ", style=discord.ButtonStyle.secondary)
    async def click_me_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.original_message is None:
            self.original_message = await interaction.channel.fetch_message(interaction.message.id)
        await interaction.response.send_modal(BreathingModal(self.original_message))

# ----- Notification Modal -----
class NotificationModal(discord.ui.Modal, title="₊　˙ㅤmassed"):
    notification = discord.ui.TextInput(
        label="ㅤ❀ ㅤ ⊹˚ㅤnotification",
        placeholder="ㅤ.ㅤping / dm",
        required=True,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        current_channel = interaction.channel
        target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID_NOTIFICATION)
        if target_channel:
            await target_channel.send(
                f"_ _\n　　　　　⋅.˳˳.⋅ॱ˙　 　 ✿　 　 {user.mention}\n　　　　　**ovn**　　₊　　<a:002_yellowwatch:1374302432003096656>　　⣓\n　　　　　—　　{current_channel.mention}　　⊹\n_ _"
            )
        try:
            await current_channel.edit(name=f"ovn﹕{user.name}—{self.notification.value}")
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to edit the channel name.", ephemeral=True)
            return

        await interaction.followup.send(
            "_ \n\n _ ⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀[*queued*](https://discord.com/channels/1371507740362543155/1371876364457873509)⠀♡\n"
            "_ _  ⠀  ⠀ ⠀⠀⠀⠀ ⠀⠀⠀⠀ *check  pings  &  dms.*\n\n_ _",
            ephemeral=False
        )

class ClickMeView(discord.ui.View):
    @discord.ui.button(label="ㅤㅤshingekiㅤnoㅤkyojinㅤㅤ", style=discord.ButtonStyle.secondary)
    async def click_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NotificationModal())

# ----- Ticket Close Button -----
class RegretButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="ㅤ(っ- ‸ – ς)ㅤ",
        style=discord.ButtonStyle.danger
    )
    async def regret_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "_ _\n\n    <:bird:1372061833204207648>  result  has  been  **sent**  ♡\n     ₊   click button to close ticket\n\n_ _",
            view=CloseTicketView()  # 👈 close button included here
        )
        
# ----- Slash Commands -----
@bot.tree.command(name="freedom", description="：　start massing")
async def freedom(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    user = interaction.user
    category = discord.utils.get(guild.categories, id=CATEGORY_ID)
    if not category:
        await interaction.followup.send("Category not found.")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
    }

    channel = await guild.create_text_channel(name=f"w﹕{user.name}", category=category, overwrites=overwrites)

    embed = discord.Embed(
        description="<:z_invisibleemt:1372062781603446807>\n<:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807>♡︎ㅤㅤ**chapter**ㅤㅤ⧦⧦ㅤㅤ🕊️ㅤㅤ*#139.*\n-# _ _<:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807>૮꒰ “◜ .◝ ꒱აㅤㅤToward  The  Tree  On  That  Hill\n<:z_invisibleemt:1372062781603446807>",
        color=DARK_GRAY
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1372031090923012116/1395331666121326652/Untitled242_20250717170922.png?ex=687a0f61&is=6878bde1&hm=1494db19e186314eaf9f0684ca5537bdf47bc7fdfac648a42b77ad26c57543b6&")

    view = ClickButton(None)
    message = await channel.send(embed=embed, view=view)
    view.original_message = message

    await interaction.followup.send(
        f"_ \n\n\n _　　　　<:eren4:1372394683501776967>          ⁺     ⊹\n_ _　　　　{channel.mention}\n\n\n_ _"
    )

@bot.tree.command(name="dreams", description="：　finished")
async def dreams(interaction: discord.Interaction):
    embed = discord.Embed()
    embed.set_image(url="https://tenor.com/view/eren-why-are-you-crying-gif-17830961909432728889")
    await interaction.response.send_message(
        content="_ _\n-# _ _　　　　　✧ ‿︵ 　~~    　~~ 　**戦わなければ勝てない。**\n_ _",
        embed=embed,
        view=ClickMeView()
    )

@bot.tree.command(name="done", description="miel only")
@app_commands.describe(sep="sep time", user="who", link="invite link", edit="ticket channel")
@app_commands.checks.has_role(REQUIRED_ROLE_ID)
async def done(interaction: discord.Interaction, sep: str, user: discord.User, link: str, edit: discord.TextChannel = None):
    await interaction.response.defer(ephemeral=True)
    target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID_DONE)
    if not target_channel:
        await interaction.followup.send("Target channel not found.")
        return

    await target_channel.send(f"_ _\n\n                          ₊ ⊹      *{sep}* <a:erendedicate:1372038697553231892> {user.mention}\n\n_ _ [⠀]( {link} )")
    await target_channel.send("_ _\n\n\n-# _ _  <a:waves:1372065708250370139>  (｡˘﹏˘｡)っ  **wait  awhile  to  count  invites**         ***!***\n\n\n_ _")

    if edit:
        try:
            await edit.edit(name="w4s")
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to rename that channel.")
            return

    await interaction.followup.send("Done!")

@bot.tree.command(name="dm", description="miel only")
@app_commands.describe(user="who's going to be DMed")
@app_commands.checks.has_role(REQUIRED_ROLE_ID)
async def dm(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=True)
    try:
        await user.send(
            f"_ \n\n\n\n\n _        sep  over.   ﹙   <:erenplush:1372066291250364478>   ﹚   {user.mention}   ✿\n-# _ _         check invites    .    ◟⠀run **/right** in ticket\n\n\n\n\n_ _"
        )
        await interaction.followup.send("User has been DMed.")
    except discord.Forbidden:
        await interaction.followup.send("I couldn't DM that user. They might have DMs off.")

@bot.tree.command(name="close", description="miel only")
@app_commands.describe(user="The user to notify", reason="Reason for closing the ticket")
async def close(interaction: discord.Interaction, user: discord.User, reason: str):
    if interaction.user.id != 1252888975635382368:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
        return

    # Respond immediately to avoid "Unknown interaction" error
    await interaction.response.send_message("Closing ticket...", ephemeral=True)

    try:
        await user.send(f"> **ticket closed** ***!!***\n> **reason:** {reason} <:wheart:1372066563020292129>")
    except discord.Forbidden:
        await interaction.followup.send("Could not DM the user. They might have DMs disabled.", ephemeral=True)
        return

    # Delete the channel after a short delay to ensure messages are sent
    await interaction.channel.delete()

# ----- Regret Command and Close Ticket View -----
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", style=discord.ButtonStyle.danger, emoji="<a:b_heartwings2:1373848451644919932>", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # Acknowledge the click immediately
        await interaction.channel.delete()

@bot.tree.command(
    name="right",
    description="：　invites gained"
)
@app_commands.describe(
    invites=". invites gained",
    portals=". other portals that posted",
    type=". server type you massed",
    link=". server invite link"
)
async def regret(
    interaction: discord.Interaction,
    invites: int,
    portals: str,
    type: str,
    link: str
):
    
    await interaction.response.defer(ephemeral=True)

    user = interaction.user
    guild = interaction.guild

    review_channel = guild.get_channel(TARGET_CHANNEL_ID_TICKET)
    if review_channel is None:
        await interaction.followup.send("Review channel not found.")
        return

    content = f"_ _\n                                **__{invites}__    invites**    ༚ි༉༷\n[⠀]({link})"

    embed = discord.Embed(description=f"(+{portals}p)‎ ‎‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎‎‎‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎‎ ‎‎ ‎ ‎ ‎ ‎੭‎ ‎‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎‎‎‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎‎ ‎‎ ‎ ‎ ‎ {type}")
    embed.set_image(url="https://media.discordapp.net/attachments/1371835441010966558/1372065624615948288/IMG_3853.jpg?ex=68256b30&is=682419b0&hm=890f7df72dbf040bd6f78ef03d743bf13e391d4cffc92b1af6939658bde65dde&=&format=webp")
    embed.set_footer(
        text=f"{user.name}‎ㅤㅤㅤ‎✧ㅤㅤㅤthankq for massing",
        icon_url=user.avatar.url if user.avatar else discord.Embed.Empty
    )

    await review_channel.send(content=content, embed=embed)

    await interaction.followup.send(
        "_ _\n\n    <a:eren_bird2:1372068208705802373>  result  has  been  **sent**  ♡\n     ₊   click button to close ticket\n\n_ _",
        view=CloseTicketView()
    )

@bot.command(name="a")
async def approve(ctx):
    await ctx.send("_ _\n<:z_invisibleemt:1372062781603446807>尊敬        ꒰৯        **checkpoints  required**\n-# _ _ ✦　　`24h`  to  post　　═╬　　`1d`  max  ext.　　<:key:1374088453788139580>\n_ _ [⠀](https://discord.gg/4sYuPUsG )")

@bot.command(name="d")
async def sep_over(ctx):
    await ctx.send("_ _\n\n\n\n　　　　　　♡　　₊　　*sep  over.*\n　　　　　　run　**` /right `**  ৎ\n\n\n\n_ _")

    try:
        await ctx.channel.edit(name="done")
    except discord.Forbidden:
        await ctx.send("I don't have permission to rename the channel.", delete_after=5)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", delete_after=5)

@bot.tree.command(name="cruel", description="：　checkpoint")
async def cruel(interaction: discord.Interaction):
    await interaction.response.defer()  # Immediately tell Discord you're working

    await interaction.followup.send(
        f"_ _\n<:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:eren:1373952750261374997>⁺<:z_invisibleemt:1372062781603446807> *but  i  __still__  **love**  you.*\n-# _ _<:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807><:z_invisibleemt:1372062781603446807>~~   ~~ **Akuma No Ko.**<:z_invisibleemt:1372062781603446807> **Ai Higuchi**\n_ _ [⠀](https://open.spotify.com/track/5cRKj1kynNFqiliT2ndZ3y?si=555b2e85b1734e89 )"
    )

# ----- Events -----
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)
    activity = discord.Streaming(
        name="the rumbling ♬",
        url="https://www.twitch.tv/sexcmiel"
    )
    await bot.change_presence(status=discord.Status.idle, activity=activity)

keep_alive()
bot.run(TOKEN)
