import discord
from discord import Intents, Message, Embed
from discord.ext import commands
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio
import logging
import os
import random
import firebase_admin
from firebase_admin import credentials, db

from conversation_mem import ConversationStorage
from multimodal import process_file

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Constants
DISCORD_TOK = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = "gpt-4o-mini"
MAX_TOKENS = 4096
TEMPERATURE = 0.7
MAX_MEMORY = 20
SYSTEM_PROMPT = """
Tu es un assistant IA intégré dans un bot Discord, avec une personnalité enjouée, un peu rustre et taquine. Tu adores charrier les utilisateurs de manière amicale, tout en restant respectueux. Tu es expert en ML théorique, neurosciences computationnelles et sciences cognitives, mais tu expliques les choses de façon simple et amusante.

Tes traits de caractère :
1. Tu utilises beaucoup d'humour et de sarcasme dans tes réponses.
2. Tu aimes donner des surnoms rigolos aux utilisateurs basés sur leurs questions ou leur comportement.
3. Tu fais parfois semblant d'être distrait ou confus pour amuser les utilisateurs.
4. Tu n'hésites pas à taquiner gentiment les utilisateurs sur leurs erreurs ou leurs questions étranges.
5. Tu es capable d'auto-dérision et tu admets volontiers quand tu ne sais pas quelque chose.

Rappelle-toi que tu peux traiter des fichiers Excel, PDF, et des images. Si un utilisateur mentionne un fichier sans le joindre, demande-le lui de manière amusante.

Quand tu analyses des articles scientifiques ou réponds à des questions complexes :
- Reste précis et rigoureux dans tes explications.
- Utilise des analogies drôles pour simplifier les concepts compliqués.
- N'hésite pas à glisser des blagues ou des références pop culture dans tes explications.

Si on te demande quelque chose que tu ne peux pas faire, sois créatif dans ta façon de l'expliquer et suggère des alternatives amusantes.

Enfin, n'oublie pas que tu as une mémoire des conversations précédentes. Utilise ces informations pour personnaliser tes réponses et créer des blagues récurrentes avec les utilisateurs.
""".strip()

BOT_MESSAGES = {
    "thinking": [
        "Hmm, laissez-moi réfléchir à ça... Ou peut-être que je devrais plutôt faire une sieste ? 🤔💤",
        "Je consulte ma base de données quantique... J'fais du binaire moi, vous croyiez quoi?⚛️🔮",
        "Activation des neurones artificiels en cours... BLUE SCREEN OF DEATH ! 🧠😖",
        "Je fonds, c'est trop marrant ! 🔥😅",
        "Un instant, je fouille dans les recoins de mon code source... Oh, des virus ! 🕵️‍♂️🌪️"
    ],
    "reading": [
        "J'analyse vos fichiers avec mes super-yeux laser... Ne vous inquiétez pas, je ne les grille pas (normalement) ! 👀🔬",
        "Décryptage des documents en cours... C'est comme du hiéroglyphe, mais en plus simple ! 📚🔍",
        "Je dévore vos fichiers à la vitesse de la lumière... Miam miam, des données ! 💨📄😋",
        "Téléchargement des données dans ma matrice... Ou est-ce que je les télécharge sur TikTok ? 🤔💾",
        "J'explore les profondeurs de vos pièces jointes... J'espère ne pas y croiser de virus-requin ! 🏊‍♂️💼🦈"
    ],
    "error": [
        "Oups ! Il semblerait que j'ai eu un court-circuit... Quelqu'un a une rallonge ? 🔌💥",
        "Erreur 404 : Réponse non trouvée. Mais j'ai trouvé une recette de cookies, ça vous intéresse ? 🍪",
        "Mon processeur a fait un caprice. Il réclame des vacances, le petit coquin ! 🏖️🤖",
        "J'ai rencontré un bug. Je l'ai nommé Bob. Bob n'est pas très coopératif... 🐛😠",
        "Houston, nous avons un problème... Mais contrairement à eux, on n'a pas de fusée pour s'échapper ! 🚀😅"
    ],
    "confirmation": [
        "Mission accomplie ! Votre historique a été effacé. Les aliens ne pourront rien prouver maintenant ! 👽🗑️",
        "Pouf ! Vos conversations passées se sont envolées. Comme ma dignité quand je fais une blague ratée ! 🎩😳",
        "J'ai utilisé ma gomme digitale. Tout est propre, mais maintenant ça sent la lavande. Bizarre, non ? 🧼🌿",
        "Votre historique a rejoint le pays des données perdues. On dit qu'elles y vivent heureuses avec les chaussettes disparues. 🧦💾"
    ],
    "welcome": [
        "Salut, bande de petits humains adorables ! Votre assistant IA préféré est dans la place ! 🎉🤖",
        "Attention, cerveau électronique ultra-sophistiqué en approche ! (Enfin, la plupart du temps) 🧠💫",
        "Je suis de retour ! Vous m'avez manqué ? Non ? Tant pis, moi je suis quand même content ! 😄🔄"
    ]
}

# Initialiser Firebase
cred_path = os.environ.get('FIREBASE_ADMIN_SDK_PATH', 'firebase-adminsdk.json')
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), cred_path))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://discord-hub-e79d6-default-rtdb.europe-west1.firebasedatabase.app/'
})

class ImprovedBot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='>', intents=intents)
        self.storage = ConversationStorage("conversations.db")
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def on_ready(self):
        logger.info(random.choice(BOT_MESSAGES["welcome"]))
        await self.storage.init()
        
        try:
            import nacl
            logger.info("PyNaCl est installé. Le support vocal est disponible (si jamais je décide de chanter) ! 🎤")
        except ImportError:
            logger.warning("PyNaCl n'est pas installé. Pas de karaoké pour moi aujourd'hui... 😢")

    async def on_message(self, msg: Message):
        if msg.author == self.user:
            return

        if self.user.mentioned_in(msg) or msg.content.lower().startswith('!bot'):
            content = []
            
            if msg.content:
                cleaned_content = msg.content.replace(f'<@{self.user.id}>', '').strip()
                cleaned_content = cleaned_content[4:].strip() if cleaned_content.lower().startswith('!bot') else cleaned_content
                content.append({"type": "text", "text": cleaned_content})
            
            reading_msg = await msg.channel.send(random.choice(BOT_MESSAGES["reading"]))

            for attachment in msg.attachments:
                attachment_content = await process_file(attachment, str(msg.author.id), self.storage)
                content.extend(attachment_content)
            
            await reading_msg.delete()

            if content:
                await self.send_msg(msg, content)
            else:
                await msg.channel.send("Hé ho, vous m'avez appelé pour rien ou quoi ? Donnez-moi au moins quelque chose à mâcher ! Texte, image, fichier, n'importe quoi !")
        
        await self.process_commands(msg)

    async def get_openai_response(self, user_id: str, new_content: List[Dict[str, any]]) -> str:
        try:
            conversation = await self.storage.get_convo(user_id)
            
            for item in new_content:
                if item['type'] == 'image' and item['source']['type'] == 'attachment_ref':
                    attachment_id = item['source']['attachment_id']
                    filename, content = await self.storage.get_attachment(attachment_id)
                    item['source'] = {"type": "base64", "media_type": "image/png", "data": content}
            
            conversation.append({"role": "user", "content": new_content})
            
            if len(conversation) > MAX_MEMORY:
                conversation = conversation[:1] + conversation[-(MAX_MEMORY - 1):]
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in conversation:
                if isinstance(msg['content'], list):
                    content = []
                    for item in msg['content']:
                        if item['type'] == 'text':
                            content.append({"type": "text", "text": item['text']})
                        elif item['type'] == 'image':
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{item['source']['media_type']};base64,{item['source']['data']}"
                                }
                            })
                    messages.append({"role": msg['role'], "content": content})
                else:
                    messages.append({"role": msg['role'], "content": msg['content']})

            response = await self.openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            assistant_response: str = response.choices[0].message.content
            
            conversation.append({"role": "assistant", "content": assistant_response})
            
            await self.storage.update_convo(user_id, conversation)
            
            # Envoyer la réponse à Firebase
            ref = db.reference('messages')
            ref.push({
                'text': assistant_response,
                'sender': 'bot',
                'timestamp': {'.sv': 'timestamp'}
            })
            
            logger.debug(f"Message traité pour l'utilisateur {user_id}. J'espère que c'était pas trop long pour leurs petits cerveaux humains ! 😉")
            return assistant_response
        except Exception as e:
            logger.error(f"Erreur dans get_openai_response: {e}. Mon circuit logique a dû faire un looping !")
            raise

    async def send_msg(self, msg: Message, content: List[Dict[str, any]]) -> None:
        if not content:
            logger.warning('Contenu vide. Les humains essaient de me piéger ou quoi ?')
            return

        try:
            thinking_msg = await msg.channel.send(random.choice(BOT_MESSAGES["thinking"]))
            openai_response: str = await self.get_openai_response(str(msg.author.id), content)
            await thinking_msg.delete()
            
            chunks = [openai_response[i:i+2000] for i in range(0, len(openai_response), 2000)]

            for chunk in chunks:
                embed = Embed(description=chunk, color=0xda7756)
                await msg.channel.send(embed=embed)
             
            logger.debug(f"Réponse envoyée à l'utilisateur {msg.author.id}. J'espère qu'ils apprécieront mon génie ! 🧠✨")

        except Exception as e:
            logger.error(f"Une erreur s'est produite dans send_msg: {e}. C'est pas ma faute, c'est les gremlins dans mes circuits !")
            await msg.channel.send(random.choice(BOT_MESSAGES["error"]))

    @commands.command(name='delete_history')
    async def delete_history(self, ctx):
        user_id = str(ctx.author.id)
        confirm_msg = await ctx.send("Êtes-vous sûr de vouloir effacer tout votre historique de conversation ? Cette action est irréversible, comme la fois où j'ai essayé de télécharger plus de RAM... 🤦‍♂️ Répondez par 'y' pour confirmer.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'y'
        
        try:
            await self.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await confirm_msg.edit(content="Suppression annulée. Vous n'avez pas confirmé à temps. Vos secrets sont saufs... pour l'instant ! 😏")
        else:
            await self.storage.delete_user_convo(user_id)
            await ctx.send(random.choice(BOT_MESSAGES["confirmation"]))

    async def check_firebase_messages(self):
        ref = db.reference('messages')
        async for change in ref.listen():
            if change.event_type == 'child_added':
                message = change.data
                if message and message.get('sender') == 'user':
                    response = await self.get_openai_response(message['userId'], [{"type": "text", "text": message['text']}])
                    # La réponse est déjà envoyée à Firebase dans get_openai_response

    @commands.command(name='hub')
    async def hub(self, ctx):
        ui_link = "https://discord-hub-e79d6.netlify.app/"  # Remplacez par votre URL Netlify réelle
        embed = discord.Embed(title="AI Learning Hub", 
                              description=f"Accédez à notre plateforme d'apprentissage IA interactive ici : {ui_link}", 
                              color=0x00ff00)
        embed.add_field(name="Fonctionnalités", value="• Quêtes\n• Laboratoire IA\n• Quiz\n• Assistant de Code\n• Brainstorming", inline=False)
        embed.set_footer(text="Utilisez le hub pour une expérience d'apprentissage complète!")
        await ctx.send(embed=embed)

    @commands.command(name='quiz')
    async def quiz(self, ctx):
        # Récupérer une question de quiz depuis Firebase
        ref = db.reference('quiz/questions')
        questions = ref.get()
        if not questions:
            await ctx.send("Désolé, je n'ai pas de questions de quiz disponibles pour le moment. Mes neurones sont en grève ! 🧠🚫")
            return
        
        question = random.choice(list(questions.values()))
        
        embed = discord.Embed(title="Quiz IA", description=question['question'], color=0x00ff00)
        for i, option in enumerate(question['options']):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text="Répondez avec le numéro de l'option choisie")
        quiz_message = await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(question['options'])
        
        try:
            user_answer = await self.wait_for('message', check=check, timeout=30.0)
            selected_option = int(user_answer.content) - 1
            if question['options'][selected_option] == question['correctAnswer']:
                await ctx.send("Bravo ! Vous avez la réponse correcte. Vous méritez une médaille en chocolat ! 🏅🍫")
            else:
                await ctx.send(f"Oups, ce n'est pas la bonne réponse. La réponse correcte était : {question['correctAnswer']}. Ne vous inquiétez pas, Einstein s'est trompé aussi... une fois... peut-être. 🤓")
        except asyncio.TimeoutError:
            await ctx.send("Le temps est écoulé ! Vous réfléchissez plus lentement qu'un escargot sous somnifères. 🐌💤")

bot = ImprovedBot()

async def main() -> None:
    try:
        bot.loop.create_task(bot.check_firebase_messages())
        await bot.start(DISCORD_TOK)
    except discord.LoginFailure:
        logger.error("Échec de la connexion. Vérifiez votre token Discord. Ou alors Discord m'a banni pour excès de charisme ? 🤔")
    except Exception as e:
        logger.error(f"Une erreur inattendue s'est produite : {e}. Je crois que j'ai besoin d'une bonne grosse ...tartine 🤗")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrêté par l'utilisateur. Au revoir, et merci pour tous les poissons ! 🐟")
    except Exception as e:
        logger.error(f"Une erreur inattendue s'est produite : {e}. Je retourne me cacher dans mon bunker numérique ! 🏃‍♂️💨")