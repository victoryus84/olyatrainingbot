# Load .env
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN_OLYA = os.getenv('BOTTOKEN')

import asyncio
import logging
import message_texts as texts
import constants as constants

from telegram import ( 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,                  
    Update )
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Define a dictionary to store user-specific data, including the selected language
user_dict = {}
univ_courses = []
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Stages
CHOOSING = range(1) 
LANGUAGE, UNIVERSITY, COURSE = range(3)

current_language = None

# markup_languages= ReplyKeyboardMarkup(message_texts.LANGUAGES, one_time_keyboard=True)
# markup_universities = ReplyKeyboardMarkup(message_texts.UNIVERSITIES, one_time_keyboard=True)
# markup_courses = ReplyKeyboardMarkup(message_texts.COURSES, one_time_keyboard=True)

async def help_command(update: Update, context):
    await update.message.reply_text(texts.HELP_MESSAGE[0])

async def start_command(update: Update, context):
    user_data = context.user_data
    user_data.clear()
    await update.message.reply_text(texts.BEGIN_MESSAGES[0], reply_markup=language_keyboard())
    return CHOOSING

async def language_choise(update: Update, context):
    user_data = context.user_data
    user_data['language'] = update.callback_query.data
    await update.callback_query.message.edit_text(f"Language selected: {user_data['language']}")
    await update.callback_query.message.reply_text(texts.UNIVERSITIES_MESSAGES[user_data['language']], reply_markup=university_keyboard())
    return CHOOSING

async def university_choise(update: Update, context):
    user_data = context.user_data
    user_data['university'] = update.callback_query.data
    univ_courses = get_courses_for_university(user_data['university'])
    # print(f"univ_courses: {univ_courses}")
    await update.callback_query.message.edit_text(f"University selected: {user_data['university']}")
    await update.callback_query.message.reply_text(texts.UNIVERSITIES_MESSAGES[user_data['language']], reply_markup=course_keyboard(univ_courses))
    return CHOOSING

async def course_choise(update: Update, context):
    user_data = context.user_data
    user_data['course'] = update.callback_query.data
    await update.callback_query.message.edit_text(f"Course selected: {user_data['course']}")
    await update.callback_query.message.reply_text("Thank you for using our bot!")
    return CHOOSING

# Funcția care returnează cursurile unei universități
def get_courses_for_university(university_name):
    return constants.COURSES.get(university_name, [])

def language_keyboard():
    keyboard = [InlineKeyboardButton(lang, callback_data=lang) for lang in constants.LANGUAGES]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

def university_keyboard():
    keyboard = [InlineKeyboardButton(university, callback_data=university) for university in constants.UNIVERSITIES]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols=3))

def course_keyboard(univ_courses):
    # print(f"univ_courses-course_keyboard: {univ_courses}")
    keyboard = [InlineKeyboardButton(course, callback_data=course) for course in univ_courses]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols=1))

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def main():
    application = Application.builder().token(TOKEN_OLYA).build()

    application.add_handler(CommandHandler("help", help_command))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            CHOOSING: [
                CallbackQueryHandler(language_choise, pattern=f"({'|'.join(constants.LANGUAGES)})$"),
                CallbackQueryHandler(university_choise, pattern=f"({'|'.join(constants.UNIVERSITIES)})$"),
                CallbackQueryHandler(course_choise, pattern=f"({'|'.join(univ_courses)})$"),
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conversation_handler)
    
    # print(f"language selected: {user_data['language']}")
    # print(f"university selected: {user_data['university']}")
    # print(f"course selected: {user_data['course']}")
          
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()