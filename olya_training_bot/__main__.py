# Load .env
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN_OLYA = os.getenv('BOTTOKEN')

import asyncio
import logging
import message_texts as message_texts

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Define a dictionary to store user-specific data, including the selected language
user_dict = {}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

LANGUAGE, UNIVERSITY, COURS = range(3)

current_language = None

# markup_languages= ReplyKeyboardMarkup(message_texts.LANGUAGES, one_time_keyboard=True)
# markup_universities = ReplyKeyboardMarkup(message_texts.UNIVERSITIES, one_time_keyboard=True)
# markup_courses = ReplyKeyboardMarkup(message_texts.COURSES, one_time_keyboard=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    print(f"DEBUG: Current def: help_command")
    
    user_id = update.effective_user.id
    await update.message.reply_text(message_texts.HELP_MESSAGE[0])



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f"DEBUG: Current def: help_command")
    """Start the conversation and ask user for input."""
    # await update.message.reply_text(
    #     message_texts.BEGIN_MESSAGES[0],
    #     reply_markup=markup_languages,
    # )
        
    # return CHOOSING
    await update.message.reply_text(
        message_texts.BEGIN_MESSAGES[0],
        reply_markup=ReplyKeyboardMarkup(
            message_texts.LANGUAGES, one_time_keyboard=True, input_field_placeholder="EN or RO?"
        ),
    )

    return LANGUAGE

async def language_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: language_choise")
    
    user_data = context.user_data
    selected_language = update.message.text

    # Verificați și setați limba selectată
    # print(f"DEBUG: Utilizatorul a selectat: {selected_language}")
    if selected_language == "English 🇬🇧":
        user_data["selected_language"] = "en"  # Salvați o abreviere pentru limba engleză
    elif selected_language == "Romanian 🇷🇴":
        user_data["selected_language"] = "ro"  # Salvați o abreviere pentru limba română
    else:
        await update.message.reply_text("Selectați o limbă din opțiunile disponibile.")
        return LANGUAGE  # Reveniți la alegerea limbii

    
    await update.message.reply_text("Language succes selected!", 
        reply_markup=ReplyKeyboardRemove())
    
    return UNIVERSITY

# UNIVERSITIES = [
#     ["ARU", "GBS", "ELS", "CCOS"],
#     ["QA", "LCCA","LCCM", "UKCBC"],
#     ["LSC"],
#     ["cancel"],
# ]

async def universities_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: universities_start")
    selected_language = context.user_data.get["selected_language"]
     # return CHOOSING
    buttons = [university[0] for university in message_texts.UNIVERSITIES]
    print(f"DEBUG: Current buttons: {buttons}")
    await update.message.reply_text(
        message_texts.BEGIN_MESSAGES[0],
        reply_markup=ReplyKeyboardMarkup(
            buttons, one_time_keyboard=True),
    )
        
    return UNIVERSITY

async def universities_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: universities_choise")
        
    user_data = context.user_data
    selected_university = user_data.get("selected_university", "ARU")   
    if selected_university != "Cancel":
        user_data["selected_university"] = selected_university
        await update.message.reply_text("Select a university:")
    else:
        await update.message.reply_text("Select a university:")
        return UNIVERSITY

    await update.message.reply_text("University succes selected!", reply_markup=ReplyKeyboardRemove())
    
    return UNIVERSITY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
    
def main() -> None:
    
    
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN_OLYA).build()
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    # Add the /help command handler
        
    application.add_handler(CommandHandler("help", help_command))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command),
                    ],
        states={
            LANGUAGE: [MessageHandler(filters.Regex("^(English 🇬🇧|Romanian 🇷🇴)$"), language_choise)],
            UNIVERSITY: [CommandHandler("univ", universities_start), MessageHandler(filters.Regex("^(ARU)$"), universities_choise)],
            # TYPING_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice)],
            # TYPING_REPLY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),received_information,)],
            
            # COURSES_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),courses_choise,)],
        },
        fallbacks= [
                [MessageHandler(filters.Regex("^Done$"), cancel)]
        ]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()