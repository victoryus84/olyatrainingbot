import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()
bot = telebot.TeleBot(os.getenv('BOTTOKEN'))

# Define the welcome message for both English and Romanian
WELCOME_MESSAGES = {
    'en': (
        "🌟Welcome to Olya Training – Your Gateway to UK Universities! 🇬🇧🌟\n"
        "Are you gearing up for university interviews and entrance exams in the UK? Look no further! "
        "Olya Training is here to guide you. Our tailored programs boost your skills and confidence, "
        "ensuring you shine in every aspect of the admissions process.\n"
        "Let’s kickstart your journey to success! Ready to ace those interviews and exams? Let's begin! 📚🎓🚀\n"
        "🌟Bine ați venit la Olya Training – Poarta ta către universitățile din Marea Britanie! 🇬🇧🌟\n"
        "Ești pregătit pentru interviurile și examenele de admitere la universitățile din Marea Britanie? Nu căuta mai departe! "
        "Olya Training este aici pentru a te ghida. Programele noastre personalizate îți dezvoltă abilitățile și încrederea, "
        "asigurându-te că te remarci în fiecare aspect al procesului de admitere.\n"
        "Hai să începem călătoria ta spre succes! Ești pregătit să strălucești la acele interviuri și examene? 📚🎓🚀"
    ),
    'ro': (
        "🌟Bine ați venit la Olya Training – Poarta ta către universitățile din Marea Britanie! 🇷🇴🌟\n"
        "Ești pregătit pentru interviurile și examenele de admitere la universitățile din Marea Britanie? Nu căuta mai departe! "
        "Olya Training este aici pentru a te ghida. Programele noastre personalizate îți dezvoltă abilitățile și încrederea, "
        "asigurându-te că te remarci în fiecare aspect al procesului de admitere.\n"
        "Hai să începem călătoria ta spre succes! Ești pregătit să strălucești la acele interviuri și examene? 📚🎓🚀"
    )
}

# Define the welcome message for both English and Romanian
BEGIN_MESSAGES = {
    'en': (
        "If you press the ""English"" button, the training will follow only in English 👇\n"
        "Dacă apesi butonul ""Romanian"" va urma pregătirea în limba Engleza cu traducere în Română 👇"
    ),
    'ro': (
       "If you press the ""English"" button, the training will follow only in English 👇\n"
        "Dacă apesi butonul ""Romanian"" va urma pregătirea în limba Engleza cu traducere în Română 👇"
    )
}

# Define the welcome message for both English and Romanian
STEP2_MESSAGES = {
    'en': (
        "Very important! Why is it absolutely necessary to know general information about the university you have applied to during the interview?" 
        "🎓Understanding general information about the university you're applying to is crucial for your success. It goes beyond just passing an" 
        "interview or an entrance exam – it's about finding the perfect match between your aspirations and the university's values, culture, and opportunities."
        "By grasping this foundational knowledge, you not only show your genuine interest but also demonstrate that you're making an informed decision about" 
        "your education. Knowing about the university's history, unique programs, faculty, and campus life equips you to tailor your answers effectively during" 
        "interviews. It showcases your enthusiasm and proves that you're ready to contribute meaningfully to the university community."
        "In essence, understanding the university you're applying to is the key to presenting yourself as a candidate who not only meets the academic criteria" 
        "but also aligns perfectly with the ethos of the institution. It's about making a compelling case for why you belong there and how you can make a significant" 
        "impact during your academic journey"
    ),
    'ro': (
         "Very important! Why is it absolutely necessary to know general information about the university you have applied to during the interview?" 
        "🎓Understanding general information about the university you're applying to is crucial for your success. It goes beyond just passing an" 
        "interview or an entrance exam – it's about finding the perfect match between your aspirations and the university's values, culture, and opportunities."
        "By grasping this foundational knowledge, you not only show your genuine interest but also demonstrate that you're making an informed decision about" 
        "your education. Knowing about the university's history, unique programs, faculty, and campus life equips you to tailor your answers effectively during" 
        "interviews. It showcases your enthusiasm and proves that you're ready to contribute meaningfully to the university community."
        "In essence, understanding the university you're applying to is the key to presenting yourself as a candidate who not only meets the academic criteria" 
        "but also aligns perfectly with the ethos of the institution. It's about making a compelling case for why you belong there and how you can make a significant" 
        "impact during your academic journey"
        "🎓 A înțelege informații generale despre universitatea la care aplici este crucial pentru succesul tău. Aceasta depășește doar trecerea unui interviu" 
        "sau a unui examen de admitere - este vorba despre găsirea potrivirii perfecte între aspirațiile tale și valorile, cultura și oportunitățile universității."
        "Prin înțelegerea acestei cunoștințe de bază, nu doar arăți un interes sincer, ci și demonstrezi că iei o decizie informată despre educația ta." 
        "Cunoașterea istoriei universității, a programelor unice, a corpului profesoral și a vieții de campus te ajută să îți ajustezi răspunsurile în mod" 
        "eficient în timpul interviurilor. Aceasta evidențiază entuziasmul tău și dovedește că ești pregătit să contribui semnificativ la comunitatea universitară."
        "În esență, înțelegerea universității la care aplici este cheia pentru a te prezenta ca un candidat care nu doar îndeplinește criteriile academice," 
        "ci se potrivește perfect cu etica instituției. Este vorba despre a face un argument convingător privind de ce aparții acolo și cum poți avea un impact" 
        "semnificativ în timpul călătoriei tale academice."

    )
}

# Define the help message
HELP_MESSAGE = (
    "Olya Training Bot that provides information and language selection.\n\n"
    "Available commands:\n"
    "/start - Start the bot and choose your language.\n"
    "/help - Display this help message."
)

# Define the languages
LANGUAGES = {
    'en': "English",
    'ro': "Romanian",
}
LANGUAGES_ICONS = {
    'en': "🇬🇧",
    'ro': "🇷🇴",
}

# Define a dictionary to store user-specific data, including the selected language
user_dict = {}
selected_languages = {}

# /help command handler
@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.chat.id, HELP_MESSAGE)

# Start command handler
@bot.message_handler(commands=["start", "help"])
def start_message(message):
    if message.text == '/start':
        user_language = get_user_language(message.chat.id)
        markup = create_language_markup()
        bot.send_message(message.chat.id, WELCOME_MESSAGES[user_language])
        bot.send_message(message.chat.id, BEGIN_MESSAGES[user_language], reply_markup=markup)
        # Set the next step for language selection
        bot.register_next_step_handler(message, handle_language_selection)


@bot.message_handler(commands=["next"])
def next_command_handler(message):
    send_step2_message(message)
    
@bot.message_handler(func=lambda message: message.text == '/next')
def send_step2_message(message):
    user_language = get_user_language(message.chat.id)
    bot.send_message(message.chat.id, STEP2_MESSAGES[user_language])
        
def handle_language_selection(message):
    user_language = get_language_code(message.text)
    set_user_language(message.chat.id, user_language)
    bot.send_message(message.chat.id, f"You have chosen {message.text}. Let's begin! (type /next)")
    bot.register_next_step_handler(message, send_step2_message)
                
@bot.message_handler(func=lambda message: message.text)
def handle_user_input(message):
    user_language = get_user_language(message.chat.id)
    if user_language == 'en':
        bot.send_message(message.chat.id, "Try /start or /help")
    else:
        bot.send_message(message.chat.id, "Încercați /start sau /help") 
    
def create_language_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for lang_code, lang_name in LANGUAGES.items():
        markup.add(KeyboardButton(f"{lang_name} {LANGUAGES_ICONS[lang_code]}"))
    return markup

def get_user_language(user_id):
    return selected_languages.get(user_id, 'en')

def set_user_language(user_id, language):
    selected_languages[user_id] = language

def get_language_code(language_name):
    for code, name in LANGUAGES.items():
        if name == language_name:
            return code

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.polling(non_stop=True)