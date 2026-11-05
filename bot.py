import discord
from discord.ext import commands
import random
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

reputacja = {}
ostatni_rep = {}
aktywne_historie = {}

LOSOWE_POCZATKI = [
    "Dawno, dawno temu w odległej krainie...",
    "Nagle w środku nocy rozległ się dziwny hałas za oknem...",
    "Kosmonauta powoli otworzył właz nieznanej planety i...",
    "Kot sąsiada nagle zaczął mówić ludzkim głosem i powiedział...",
    "W starej, zakurzonej skrzyni na strychu znaleźli mapę, która..."
]

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name} (ID: {bot.user.id})")
    print("Bot Bloomist jest gotowy do działania!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = message.channel.id

    if channel_id in aktywne_historie:
        dane = aktywne_historie[channel_id]
        dane["zdania"].append(message.content)

        if len(dane["zdania"]) % 5 == 0:
            pelna_historia = " ".join(dane["zdania"])
            await message.channel.send(f"📖 *Aktualny stan opowieści:**\n*{pelna_historia}")

    await bot.process_commands(message)

@bot.command(name="vczesc")
async def vczesc(ctx):
    await ctx.send(f"Cześć {ctx.author.mention}! Bloomist bot działa poprawnie! 🌸")

@bot.command(name="vkwiat")
async def vkwiat(ctx):
    await ctx.send(f"🌸 {ctx.author.mention}, oto bukiet świeżych kwiatów specjalnie dla Ciebie! Miłego dnia! 🌷🌼")

@bot.command(name="vkpn")
async def vkpn(ctx, wybor: str):
    wybor = wybor.lower()
    opcje = ["kamien", "papier", "nozyce"]
    if wybor not in opcje:
        await ctx.send("Wybierz: kamien, papier lub nozyce!")
        return
    
    bot_wybor = random.choice(opcje)
    if wybor == bot_wybor:
        await ctx.send(f"Remis! Oboje wybraliście {bot_wybor}.")
    elif (wybor == "kamien" and bot_wybor == "nozyce") or \
         (wybor == "papier" and bot_wybor == "kamien") or \
         (wybor == "nozyce" and bot_wybor == "papier"):
        await ctx.send(f"Wygrałeś! Bot wybrał {bot_wybor}. 🎉")
    else:
        await ctx.send(f"Przegrałeś! Bot wybrał {bot_wybor}. 😈")

@bot.command(name="v8ball")
async def v8ball(ctx, *, pytanie):
    odpowiedzi = [
        "Zdecydowanie tak! 🌸",
        "Moim zdaniem... tak!",
        "Zapytaj ponownie później 🔮",
        "Nie liczyłbym na to...",
        "Gwiazdy mówią: zdecydowanie NIE! ❌"
    ]
    await ctx.send(f"❓ *Pytanie:* {pytanie}\n🔮 *Odpowiedź:* {random.choice(odpowiedzi)}")

@bot.command(name="vrep")
async def vrep(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Oznacz użytkownika, któremu chcesz dać reputację, np. !vrep @Nazwa!")
        return

    dawca = ctx.author
    
    if member.id == dawca.id:
        await ctx.send("❌ Nie możesz dać punktu reputacji samemu sobie! Nice try 😉")
        return

    if member.bot:
        await ctx.send("🤖 Nie możesz dawać reputacji botom!")
        return

    aktualny_czas = time.time()
    czas_cooldownu = 14400 
    
    if dawca.id in ostatni_rep:
        minelo = aktualny_czas - ostatni_rep[dawca.id]
        if minelo < czas_cooldownu:
            pozostalo_sekund = int(czas_cooldownu - minelo)
            godziny = pozostalo_sekund // 3600
            minuty = (pozostalo_sekund % 3600) // 60
            await ctx.send(f"⏳ Musisz poczekać jeszcze *{godziny} godz. i {minuty} min.* zanim znowu komuś dasz reputację!")
            return

    ostatni_rep[dawca.id] = aktualny_czas

    if member.id not in reputacja:
        reputacja[member.id] = 0
    reputacja[member.id] += 1

    await ctx.send(f"⭐ *{dawca.name}* przyznał punkt reputacji dla *{member.name}*! Aktualny stan: {reputacja[member.id]} pkt 🌟")

@bot.command(name="vpunkty")
async def vpunkty(ctx, member: discord.Member = None):
    cel = member if member else ctx.author
    punkty_uzytkownika = reputacja.get(cel.id, 0)
    await ctx.send(f"📊 Użytkownik *{cel.name}* ma na koncie *{punkty_uzytkownika}* punktów reputacji.")

@bot.command(name="vtop")
async def vtop(ctx):
    if not reputacja:
        await ctx.send("📊 Tabela reputacji jest jeszcze pusta! Nikt nikomu nie przyznał punktu.")
        return

    posortowani = sorted(reputacja.items(), key=lambda item: item[1], reverse=True)
    
    tekst = "🏆 **Ranking Reputacji (Top 5):**\n\n"
    medale = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for i, (user_id, punkty) in enumerate(posortowani[:5]):
        user = ctx.guild.get_member(user_id)
        nazwa = user.name if user else f"Użytkownik ID: {user_id}"
        medal = medale[i] if i < len(medale) else "▫️"
        tekst += f"{medal} *{nazwa}* – `{punkty} pkt`\n"

    await ctx.send(tekst)

@bot.command(name="vstory")
async def vstory(ctx):
    poczatek = random.choice(LOSOWE_POCZATKI)
    aktywne_historie[ctx.channel.id] = {
        "zdania": [poczatek]
    }
    await ctx.send(f"📖 *Rozpoczynamy nową historię na tym kanale!**\n\n*{poczatek}*\n\n*(Piszcie kolejne zdania na czacie!)")

@bot.command(name="vhelp")
async def vhelp(ctx):
    tekst = (
        "📜 **Lista komend bota Bloomist:**\n\n"
        "!vczesc - Witka z botem! 🌸\n"
        "!vkwiat - Wysyła piękny bukiet dla Ciebie 🌷\n"
        "!vkpn <kamien/papier/nozyce> - Gra w kamień, papier, nożyce ✂️\n"
        "!v8ball <pytanie> - Zadaj pytanie, a bot odpowiada wróżbą 🔮\n"
        "!vrep @użytkownik - Daje punkt reputacji innej osobie (co 4 godz.) ⭐\n"
        "!vpunkty [@użytkownik] - Sprawdza stan punktów reputacji 📊\n"
        "!vtop - Wyświetla ranking najlepszych użytkowników 🏆\n"
        "!vstory - Startuje/resetuje wspólne pisanie historii na kanale 📖\n"
        "!vhelp - Wyświetla tę listę komend ❓"
    )
    await ctx.send(tekst)

bot.run("MTU2NzQ2MDU4MzcxMDY1ODU3MA.GjY8ah.sgaHbRCRBoKLmCz-tewL5OiGWhVIKDg7EPhVDQ")