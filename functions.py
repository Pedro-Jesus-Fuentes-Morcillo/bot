import unidecode
import os

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    Message,
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

from constants import (
    BASE_DIR, DATA_DIR,
    MEDIA_DIR, CACHE_FILE_PATH,
    VIDEO_DIR, IMAGE_DIR,
    GIF_DIR, VOICE_DIR,
    EDITS_DIR
)

from FileIDCache import FileIDCache

file_id_cache = FileIDCache()

def basic_str(input_str: str) -> str:
    msg_lower = input_str.lower()
    return unidecode.unidecode(msg_lower)

async def download_photo(context: ContextTypes.DEFAULT_TYPE, photo_id: str) -> None:
    downloaded_path = os.path.join(EDITS_DIR, 'orig.jpg')
    print(downloaded_path)
    photo_file= await context.bot.get_file(photo_id)
    await photo_file.download_to_drive(downloaded_path)

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE, video_filename: str, caption = '', use_cache = False) -> Message:
    chat_id = update.message.chat_id
    video_path = os.path.join(VIDEO_DIR, video_filename)  # Construir la ruta completa del archivo de video
    video_key = os.path.basename(video_path)  # Obtener el nombre del archivo como clave

    # Verificar si el file ID ya está en la caché
    file_id = file_id_cache.get_file_id(video_key)
    if file_id and use_cache:
        sent_message = await context.bot.send_video(chat_id,
                               video=file_id,
                               caption=caption,
                               reply_to_message_id=update.message.message_id)
    else:
        # Subir el video y obtener el file ID
        with open(video_path, 'rb') as video_file:
            sent_message = await context.bot.send_video(chat_id,
                                                  video=video_file,
                                                  caption=caption,
                                                  reply_to_message_id=update.message.message_id)
        
        # Guardar el file ID en la caché
        if use_cache:
            file_id_cache.set_file_id(video_key, sent_message.video.file_id)
    
    return sent_message

async def send_pic(update: Update, context: ContextTypes.DEFAULT_TYPE, image_filename: str, caption = '', use_cache = False) -> Message:
    chat_id = update.message.chat_id
    image_path = os.path.join(IMAGE_DIR, image_filename)  # Construir la ruta completa del archivo de imagen
    print(image_path)
    image_key = os.path.basename(image_path)  # Obtener el nombre del archivo como clave

    # Verificar si el file ID ya está en la caché
    file_id = file_id_cache.get_file_id(image_key)
    if file_id and use_cache:
        sent_message = await context.bot.send_photo(chat_id,
                               photo=file_id,
                               caption=caption,
                               reply_to_message_id=update.message.message_id)
    else:
        # Subir la imagen y obtener el file ID
        with open(image_path, 'rb') as image_file:
            sent_message = await context.bot.send_photo(chat_id,
                                                  photo=image_file,
                                                  caption=caption,
                                                  reply_to_message_id=update.message.message_id)
        
        # Guardar el file ID en la caché
        if use_cache:
            file_id_cache.set_file_id(image_key, sent_message.photo[-1].file_id)
        
    return sent_message

async def send_voice(update: Update, context: ContextTypes.DEFAULT_TYPE, voice_filename: str, caption = '', use_cache = False) -> Message:
    chat_id = update.message.chat_id
    voice_path = os.path.join(VOICE_DIR, voice_filename)  # Construir la ruta completa del archivo de imagen
    voice_key = os.path.basename(voice_path)  # Obtener el nombre del archivo como clave

    # Verificar si el file ID ya está en la caché
    file_id = file_id_cache.get_file_id(voice_key)
    if file_id and use_cache:
        sent_message = await context.bot.send_voice(chat_id,
                               voice=file_id,
                               caption=caption,
                               reply_to_message_id=update.message.message_id)
    else:
        # Subir la imagen y obtener el file ID
        with open(voice_path, 'rb') as voice_file:
            sent_message = await context.bot.send_voice(chat_id,
                                                  voice=voice_file,
                                                  caption=caption,
                                                  reply_to_message_id=update.message.message_id)
        
        # Guardar el file ID en la caché
        if use_cache:
            file_id_cache.set_file_id(voice_key, sent_message.voice.file_id)
        
    return sent_message

async def send_animation(update: Update, context: ContextTypes.DEFAULT_TYPE, animation_filename: str, caption = '', use_cache = False) -> Message:
    chat_id = update.message.chat_id
    animation_path = os.path.join(GIF_DIR, animation_filename)  # Construir la ruta completa del archivo de imagen
    animation_key = os.path.basename(animation_path)  # Obtener el nombre del archivo como clave

    # Verificar si el file ID ya está en la caché
    file_id = file_id_cache.get_file_id(animation_key)
    if file_id and use_cache:
        sent_message = await context.bot.send_animation(chat_id,
                               animation=file_id,
                               caption=caption,
                               reply_to_message_id=update.message.message_id)
    else:
        # Subir la imagen y obtener el file ID
        with open(animation_path, 'rb') as voice_file:
            sent_message = await context.bot.send_animation(chat_id,
                                                  animation=voice_file,
                                                  caption=caption,
                                                  reply_to_message_id=update.message.message_id)
        
        # Guardar el file ID en la caché
        if use_cache:
            file_id_cache.set_file_id(animation_key, sent_message.animation.file_id)
        
    return sent_message
