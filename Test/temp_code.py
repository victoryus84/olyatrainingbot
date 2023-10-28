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

LANGUAGE, UNIVERSITY,COURS = range(3)

current_language = None

markup_languages= ReplyKeyboardMarkup(message_texts.LANGUAGES, one_time_keyboard=True)
markup_universities = ReplyKeyboardMarkup(message_texts.UNIVERSITIES, one_time_keyboard=True)
markup_courses = ReplyKeyboardMarkup(message_texts.COURSES, one_time_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
   
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    print(f"DEBUG: Current def: help_command")
    
    user_id = update.effective_user.id
    await update.message.reply_text(message_texts.HELP_MESSAGE[0])

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: regular_choice")
      
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    print(f"DEBUG: Utilizatorul a selectat: {text}")
    await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

    return TYPING_REPLY

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
    
    return LANGUAGE
# UNIVERSITIES = [
#     ["ARU", "GBS"],
#     ["ELS", "CCOS"],
#     ["QA", "LCCA"],
#     ["LCCM", "UKCBC"],
#     ["LSC"],
#     ["Done"],
# ]

async def universities_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: universities_choise")
    
    user_data = context.user_data
    selected_university = user_data.get("selected_university", "ARU")   
    if selected_university != "Done":
        user_data["selected_university"] = selected_university
    else:
        universities = message_texts.UNIVERSITIES_MESSAGES[user_data.get("selected_language")]
        # Construiți o listă de butoane pentru universități din mesajele dvs.
        buttons = [university[0] for university in universities]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
        await update.message.reply_text("Select a university:", reply_markup=reply_markup)
        return CHOOSING

    await update.message.reply_text("University succes selected!", reply_markup=ReplyKeyboardRemove())
    
    return CHOOSING

# COURSES = [
#     ["BSc (Hons) International Business Management with Foundation Year", "Test_1", "Test2"],
#     ["Done"],
# ]

async def courses_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_data = context.user_data
    user_state = user_data.get('state', COURSES_CHOICE)

    if user_state == COURSES_CHOICE:
        # Ați ajuns în funcția cursurilor
        user_data['selected_course'] = update.message.text
        await update.message.reply_text("Course successfully selected!")
        # Setăm starea următoare sau orice logică doriți
    else:
        await update.message.reply_text("Select a course please!")

    return user_data['state']


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: custom_choice")
    
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: received_information")
    
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)}You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup_languages,
    )

    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    print(f"DEBUG: Current def: done")
    
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END

def facts_to_str(user_data: dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def list_user_data_keys(update, context) -> None:
    # Accesează dicționarul user_data
    user_data = context.user_data
    # Obține o listă cu toate cheile din user_data
    keys = list(user_data.keys())
    # Răspunde cu lista de chei
    await update.message.reply_text(f"Data user keys: {keys}")
    
def main() -> None:
    
    
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN_OLYA).build()
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    # Add the /help command handler
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list_keys", list_user_data_keys))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start_command", start_command),
                    ],
        
        states={
            LANGUAGE: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), language_choise)],
            # UNIVERSITIES_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),universities_choise,)],
            # TYPING_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice)],
            # TYPING_REPLY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),received_information,)],
            
            # COURSES_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),courses_choise,)],
        },
        fallbacks= [
                [MessageHandler(filters.Regex("^Done$"), done)]
        ]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()