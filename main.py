from keep_alive import keep_alive
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Dictionnaire pour stocker les temps de service des utilisateurs
time_tracking = {}

# Intents nécessaires pour le bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Préfixe du bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Appel de la fonction keep_alive pour démarrer le serveur Flask
keep_alive()

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        # Entrée dans un salon vocal
        time_tracking[member.id] = time_tracking.get(member.id, {'start': None, 'total': 0})
        time_tracking[member.id]['start'] = datetime.now()

    if before.channel is not None and after.channel is None:
        # Sortie du salon vocal
        if member.id in time_tracking and time_tracking[member.id]['start']:
            elapsed_time = datetime.now() - time_tracking[member.id]['start']
            time_tracking[member.id]['total'] += elapsed_time.total_seconds()
            time_tracking[member.id]['start'] = None

            total = int(time_tracking[member.id]['total'])
            hours = total // 3600
            minutes = (total % 3600) // 60
            seconds = total % 60
            print(f"{member.name} a passé {hours}h {minutes}m {seconds}s en service.")

@bot.command()
async def time(ctx):
    await ctx.message.delete()  # Supprime le message de commande

    user_id = ctx.author.id
    if user_id in time_tracking:
        total = int(time_tracking[user_id]['total'])
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        await ctx.send(f'{ctx.author.name}, tu as {hours}h {minutes}m {seconds}s de service. Le commandant va être fier de toi (ou pas).')
    else:
        await ctx.send(f'{ctx.author.name}, tu as pas encore pris ton service? Fais gaffe tu va te faire virer :) .')

@bot.command()
async def resetall(ctx):
    if any(role.name == "Chef" for role in ctx.author.roles):
        global time_tracking
        time_tracking = {}
        await ctx.send("Les temps de service de tous les agents ont été réinitialisés.")
    else:
        await ctx.send("Désolé, cette commande est réservée aux boss. Retourne bosser.")

@bot.command()
async def alltime(ctx):
    if any(role.name == "Chef" for role in ctx.author.roles):
        if not time_tracking:
            await ctx.send("Les agents sont des flemmars.")
            return

        leaderboard_message = "Temps de service de tous les agents :\n"
        for user_id, data in time_tracking.items():
            try:
                member = await ctx.guild.fetch_member(user_id)
                total = int(data['total'])
                hours = total // 3600
                minutes = (total % 3600) // 60
                seconds = total % 60
                leaderboard_message += f"{member.name} : {hours}h {minutes}m {seconds}s\n"
            except:
                continue

        await ctx.send(leaderboard_message)
    else:
        await ctx.send("Désolé, cette commande est réservée aux boss. Retourne bosser.")

# Lancer le bot
bot.run(TOKEN)
