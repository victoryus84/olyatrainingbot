# Load .env
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN_OLYA = os.getenv('BOTTOKEN')

import asyncio
import logging
import message_texts

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

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
 
LANGUAGE_CHOISE = []

# Define the languages
LANGUAGES = [
    ["English 🇬🇧", "Romanian 🇷🇴"]
]
LANGUAGES_ICONS = {
    'en': "🇬🇧",
    'ro': "🇷🇴",
}

UNIVERSITIES = [
    ["ARU", "GBS"],
    ["ELS", "CCOS"],
    ["QA", "LCCA"],
    ["LCCM", "UKCBC"],
    ["LSC"],
    ["Done"],
]

COURSES = [
    ["BSc (Hons) International Business Management with Foundation Year", "Test_1", "Test2"],
    ["Done"],
]

current_language = None

markup_languages= ReplyKeyboardMarkup(LANGUAGES, one_time_keyboard=True)
markup_universities = ReplyKeyboardMarkup(UNIVERSITIES, one_time_keyboard=True)
markup_courses = ReplyKeyboardMarkup(COURSES, one_time_keyboard=False)
    
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        message_texts.BEGIN_MESSAGES[0],
        reply_markup=markup_languages,
    )
        
    return CHOOSING

async def start_universities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    user_data = context.user_data
    selected_language = user_data["selected_language"]
    
    await update.message.reply_text(
        message_texts.UNIV_MESSAGES[selected_language],
        reply_markup=markup_universities,
    )
        
    return CHOOSING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(message_texts.HELP_MESSAGE[0])

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    print(f"DEBUG: Utilizatorul a selectat: {text}")
    await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

    return TYPING_REPLY

async def language_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        return CHOOSING  # Reveniți la alegerea limbii

    await update.message.reply_text("Language succes selected!", reply_markup=ReplyKeyboardRemove())

    return CHOOSING

# async def universities_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     user_data = context.user_data
#     selected_language = user_data["selected_language"]
    
#     await update.message.reply_text(
#         message_texts.UNIV_MESSAGES[selected_language],
#         reply_markup=markup_universities,
#     )

#     return CHOOSING

async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN_OLYA).build()
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    # Add the /help command handler
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list_keys", list_user_data_keys))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                     CommandHandler("univ", start_universities)],
        states={
            CHOOSING: [MessageHandler(filters.Regex("^(Age|Favourite colour|Number of siblings)$"), regular_choice),
                       MessageHandler(filters.Regex("^Something else...$"), custom_choice),
                       MessageHandler(filters.Regex("English 🇬🇧") ^ filters.Regex("Romanian 🇷🇴"), language_choise),
                       ],
            TYPING_CHOICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice)],
            TYPING_REPLY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),received_information,)],
        },
        fallbacks= [
                [MessageHandler(filters.Regex("^Done$"), done)]
        ]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())