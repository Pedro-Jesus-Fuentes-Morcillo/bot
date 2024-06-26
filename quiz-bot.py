import json
import asyncio
import logging
import random
import add_pic
#from asyncio import Queue

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Updater,
    Application,
    BaseHandler,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)

# Configuración del logging
logging.basicConfig(filename="/tmp/quiz-bot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TOTAL_VOTER_COUNT = 5

# Token de tu bot
TOKEN_FILE = "TOKEN.txt"
INTERVAL = 2700 # secconds
MSG_DELETE_TIME = 90
#INTERVAL = 4

# Cargar preguntas desde el archivo JSON
with open('nuevas.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Almacenar las preguntas y las respuestas correctas temporalmente
current_question = {}

def get_bot_token():
    """Get token from file"""
    with open(TOKEN_FILE, "r", encoding="utf-8") as file:
        token = file.read().strip()  # Get token and delete spaces
    return token

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "Enviando cuestionarios cada "+ str(int(INTERVAL/60))+ " minutos"
    )
    context.application.job_queue.run_once(quiz, when = 0, data = INTERVAL, chat_id = chat_id, name="quiz")
    context.application.job_queue.run_repeating(quiz, interval=INTERVAL, first=0, 
                                    data = INTERVAL, chat_id = chat_id, name="quiz")
    #context.application.job_queue.run_repeating(quiz, interval=10, first=0, context=chat_id, name="quiz")

async def stop_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop quiz generation"""
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id, "Se ha detenido el envio de encuestas. Ya no keleis ma? :(")
    await stop_jobs(update, context, "quiz")


async def test(update: Update, context: CallbackContext) -> None:
    """Execute individual quiz test"""
    chat_id = update.effective_chat.id
    context.application.job_queue.run_once(quiz, when = 0, data = INTERVAL, chat_id = chat_id, name="quiz")
    #context.application.job_queue.run_repeating(quiz, interval=2, first=0, chat_id = chat_id, name="quiz")

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Change the interval at which questionnaires are sent """
    global INTERVAL
    chat_id = update.effective_chat.id
    mins = context.args[0]
    if not mins.isdigit():
        await update.message.reply_text(
        "El campo dado "+ str(mins)+ " debe ser un numero entero en minutos"
        )
    else:
        INTERVAL=int(mins)*60
        await update.message.reply_text(
            "Las encuestas se enviarán cada "+ str(int(INTERVAL/60))+ " minutos"
        )
        # Stop quiz jobs in current chat
        await stop_jobs(update, context, "quiz")
        context.application.job_queue.run_repeating(quiz, interval=INTERVAL, first=0,
                                        data = INTERVAL, chat_id = chat_id, name="quiz")

async def stop_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE, job_name) -> None:
    """Stop quiz jobs in current chat"""
    jobs_list = [ job for job in context.application.job_queue.jobs() ]
    chat_id = update.effective_chat.id
    for job in jobs_list:
        print(str(job.chat_id)+" name "+job.name+" name var "+job_name)
        if str(job.chat_id) == str(chat_id) and job.name == str(job_name):
            job.schedule_removal()

async def delete_msg(context: ContextTypes.DEFAULT_TYPE) -> None:
    "Delete message with chat and msg id"
    data = context.job.data
    chat_id = data["chat_id"]
    msg_id= data["msg_id"]
    context = data["context"]
    await context.bot.delete_message(chat_id, msg_id)

async def quiz(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a predefined poll"""
    job = context.job
    chat_id=job.chat_id
    #chat_id = update.effective_chat.id

    question = random.choice(questions)  # Selecciona una pregunta aleatoria
    options = question['options']
    correct_option = question['correct_option']
    question_text = question['question']

    # Mezclar las opciones
    options_with_indices = list(enumerate(options))
    random.shuffle(options_with_indices)

    # Guardar la pregunta y la respuesta correcta en la posición aleatorizada
    current_question[chat_id] = {
        'question': question['question'],
        'correct_option': next(idx for idx, option in options_with_indices if option == options[correct_option])
    }

    msg = await context.bot.send_poll(
        chat_id, question_text, options, 
        type=Poll.QUIZ, correct_option_id=correct_option, is_anonymous=False
    )

    text = await context.bot.send_message(chat_id, "Esta seguro que Enmaporro y Paporro no la aciertan")
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        msg.poll.id: {"chat_id": chat_id, "message_id": msg.message_id}
    }

    # Delete quiz
    context.application.job_queue.run_once(delete_msg, INTERVAL,
                               data={'chat_id': msg.chat_id, 
                                     'msg_id': msg.message_id, 
                                     'context': context},
                               name="delete-quiz")

    # Delete rest of msgs
    context.application.job_queue.run_once(delete_msg, INTERVAL,
                               data={'chat_id': text.chat_id,
                                     'msg_id': text.message_id,
                                     'context': context},
                               name="delete-msg")

    #context.bot_data.update(payload)

async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])

def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start quiz when the bot is added to a group"""
    chat_id = update.message.chat_id
    context.application.job_queue.run_repeating(quiz, interval=INTERVAL, first=0, 
                                    data = INTERVAL, chat_id = chat_id, name="quiz")
    update.message.reply_text('¡Gracias por añadirme al grupo! Enviaré preguntas de cultura general cada '+INTERVAL/60+' minutos.')
    context.application.job_queue.run_once(quiz, when = 0, data = INTERVAL, chat_id = chat_id, name="quiz")

async def pic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get msg with photos"""
    reply = None
    reply_list = []
    msg = update.message
    photo_id = None
    photo_file = None
    orig_file = './imgs/edits/orig.jpg'
    png_file = './imgs/edits/barba.png'
    if msg.photo:
        if msg.caption.lower().find('es pablo') != -1:
            photo_id=msg.photo[-1].file_id
            photo_file= await context.bot.get_file(photo_id)
            await photo_file.download_to_drive(orig_file)
            add_pic.add_pic(orig_file, png_file)
            reply = await context.bot.send_photo(msg.chat_id,
                                    photo=open("./imgs/edits/result.jpg", "rb"),
                                    caption="Es increíble como es literalmente Pablo",
                                    reply_to_message_id=msg.message_id)
            reply_list.append(reply)

    if reply_list:
        for reply in reply_list:
            context.application.job_queue.run_once(delete_msg, MSG_DELETE_TIME,
                                data={'chat_id': reply.chat_id,
                                        'msg_id': reply.message_id,
                                        'context': context},
                                name="delete-msg")
    
async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Read all msg and search pito word"""
    pito_word = "pito"
    gay_word = "gay"
    guapo_word = "guapo"
    reply = None
    reply_list = []
    msg = update.message    
    msg_lower = msg.text.lower()
    if msg_lower.find(pito_word) != -1:
        reply = await context.bot.send_photo(msg.chat_id,
                                    photo=open("./imgs/pito.jpg", "rb"),
                                    caption="Mmm no se antojen...",
                                    reply_to_message_id=msg.message_id)
        reply_list.append(reply)
    if msg_lower.find(guapo_word) != -1:
        reply = await context.bot.send_photo(msg.chat_id,
                                    photo=open("./imgs/guapo.jpg", "rb"),
                                    caption="Mmm no se antojen...",
                                    reply_to_message_id=msg.message_id)
        reply_list.append(reply)
    if msg_lower.find(gay_word) != -1:
        reply = await context.bot.send_voice(msg.chat_id,
                                             voice=open("./voice/gay.mp3", "rb"),
                                             reply_to_message_id=msg.message_id)
        reply_list.append(reply)

    #if reply is not None:
    if reply_list:
        for reply in reply_list:
            context.application.job_queue.run_once(delete_msg, MSG_DELETE_TIME,
                                data={'chat_id': reply.chat_id,
                                        'msg_id': reply.message_id,
                                        'context': context},
                                name="delete-msg")

async def resume_quiz_after_restart(application: Application) -> None:
    """Resume quizes after bot restart"""
    chat_id = "-1001915500416"
    # reply = await application.bot.send_message(chat_id,
    #                                 text="Bot restarted...")
    application.job_queue.run_repeating(quiz, interval=INTERVAL, first=0,
                                    data = INTERVAL, chat_id = chat_id, name="quiz")

async def post_init(application: Application) -> None:
    """Execute after bot startup"""
    commands = [("start", "Bot starts to send quizs"),
                ("stop_quiz", "Stop quizs sendings"),
                ("set_interval", "Give a numer of mins between quizs")]
    await application.bot.set_my_commands(commands)
    await resume_quiz_after_restart(application)

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    token = get_bot_token()
    application = Application.builder().token(token).post_init(post_init).build()

    #application.add_handler(MessageHandler(filters.StatusUpdate._NewChatMembers, add_group))
    application.add_handler(CommandHandler("start", start_quiz))
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("stop_quiz", stop_quiz))
    application.add_handler(CommandHandler("set_interval", set_interval, has_args=True))
    application.add_handler(MessageHandler(filters.TEXT, msg_handler, block=False))
    application.add_handler(MessageHandler(filters.PHOTO, pic_handler, block=False))
    #application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(PollHandler(receive_quiz_answer))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
