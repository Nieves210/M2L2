import discord
from discord.ext import commands
from config import token
from collections import defaultdict
from logic import quiz_questions 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_responses = {}
user_points = {}


class QuizView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None) 
        self.user_id = user_id 

        question_index = user_responses.get(user_id, 0)
        question = quiz_questions[question_index]

        for i, option in enumerate(question.options):
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary, custom_id=f"{user_id}_{i}")
            button.callback = self.button_callback  # Butona tıklanınca çalışacak fonksiyon
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if user_id != self.user_id:
            await interaction.response.send_message("Bu soruya yalnızca komutu yazan kişi cevap verebilir.", ephemeral=True)
            return

        question_index = user_responses.get(user_id, 0)
        question = quiz_questions[question_index]

        selected_option = int(interaction.data["custom_id"].split("_")[1])

        if selected_option == question._Question__answer_id:
            user_points[user_id] = user_points.get(user_id, 0) + 1
            await interaction.response.send_message("Doğru cevap!", ephemeral=True)
        else:
            await interaction.response.send_message("Yanlış cevap!", ephemeral=True)

        user_responses[user_id] += 1

        if user_responses[user_id] >= len(quiz_questions):
            await interaction.followup.send(f"Test tamamlandı! Toplam puanınız: {user_points.get(user_id, 0)}")
        else:
            question_index = user_responses[user_id]
            question = quiz_questions[question_index]

            await interaction.followup.send(f"**Soru:** {question.text}", view=QuizView(user_id))

@bot.command()
async def start(ctx):
    user_id = ctx.author.id

    if user_id in user_responses:
        await ctx.send("Zaten bir test başlattınız!")
        return

    user_responses[user_id] = 0
    user_points[user_id] = 0
    await ctx.send("Test başlıyor! İlk soru:", view=QuizView(user_id))

bot.run(token)
