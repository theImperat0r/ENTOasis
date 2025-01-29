from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.ext import filters
from telegram.ext import CallbackContext
import asyncio, nest_asyncio
from telegram import KeyboardButton, ReplyKeyboardMarkup

TOKEN = '7793066582:AAFLTHOAz35bNxBxI0LKQVmzFFqew-R3QAw'
ADMIN_CHAT_ID = '2001599721'  

BOT_TOKEN = TOKEN
ADMIN_IDS = ['2001599721', '6280496611', '7834496052']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🌟Basic", callback_data="basic"),
            InlineKeyboardButton("🚀Standard", callback_data="standard"),
            InlineKeyboardButton("💎Premium", callback_data="premium"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *გამარჯობა!*\n"
        "კეთილი იყოს თქვენი მობრძანება! 🥳\n\n"
        "აირჩიეთ გამოწერის პაკეტი და გაიგეთ მეტი 👇:\n\n"
        "🌟 *Basic* — 40 ლარი/თვე\n"
        "- 2 გიდი\n"
        "- 6 სიმულაცია\n"
        "- 1 ყოველკვირეული კონსულტაცია\n\n"
        "🚀 *Standard* — 60 ლარი/თვე\n"
        "- 3 გიდი\n"
        "- 7 სიმულაცია\n"
        "- 2 ყოველკვირეული კონსულტაცია\n\n"
        "💎 *Premium* — 90 ლარი/თვე\n"
        "- 5 გიდი\n"
        "- 10 სიმულაცია\n"
        "- 3 ყოველკვირეული კონსულტაცია\n\n"
        "🛠️ გთხოვთ, აირჩიოთ თქვენი გამოწერის ტიპი ქვემოთ მოცემული ღილაკების საშუალებით! 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data["selected_plan"] = choice
    await query.edit_message_text(
        text=f"✅ თქვენ აირჩიეთ: *{choice.capitalize()}*\n\n"
        "📝 გთხოვთ, შეავსოთ ეს ფორმა, რათა გააგრძელოთ:\n\n"
        "[👉 გახსენით Google ფორმა](https://forms.gle/example)\n\n"
        "ფორმის შევსების შემდეგ დააჭირეთ ქვემოთ მოცემულ ღილაკს 👇",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ ფორმა შევავსე", callback_data="form_completed")]]
        ),
        parse_mode="Markdown",
    )

async def form_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[KeyboardButton("📞 კონტაქტის გაგზავნა", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text(
        text="📲 შესანიშნავია! ახლა, გთხოვთ, გააგზავნოთ თქვენი კონტაქტი ქვემოთ მოცემული ღილაკის საშუალებით 👇",
    )
    await query.message.reply_text("ველოდები თქვენს კონტაქტს!", reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    selected_plan = context.user_data.get("selected_plan", "არ აირჩია")

    context.user_data["user_info"] = (
        f"👤 *ახალი მომხმარებელი*\n"
        f"✅ აირჩია: *{selected_plan.capitalize()}*\n"
        f"სახელი: {contact.first_name}\n"
        f"გვარი: {contact.last_name or 'არ არის მითითებული'}\n"
        f"ტელეფონის ნომერი: {contact.phone_number}\n"
        f"ID: {update.effective_user.id}"
    )

    plan_prices = {"Basic": 30, "Standard": 60, "Premium": 90}
    price = plan_prices.get(selected_plan.capitalize(), 0)

    await update.message.reply_text(
        f"📸 შესანიშნავია! ახლა, გთხოვთ, გადაიხადოთ {price}₾.\n"
        f"🪙ანგარიში: 33003300330\n"
        f"🏦საქართველოს ბანკი\n"
        f"✅დადასტურებისთვის გამოაგზავნეთ გადარიცხვის სურათი!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = await update.message.photo[-1].get_file()
    file_path = f"{user.id}_photo.jpg"
    await photo.download_to_drive(file_path)

    user_info = context.user_data.get("user_info", "ინფორმაცია არ არის😢.")

    for admin_id in ADMIN_IDS:
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=open(file_path, "rb"),
            caption=user_info,
            parse_mode="Markdown"
        )

    await update.message.reply_text("✅ მადლობა! თქვენი მონაცემები წარმატებით გაიგზავნა ადმინისტრატორებისთვის.")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern="^(basic|standard|premium)$"))
    application.add_handler(CallbackQueryHandler(form_completed, pattern="form_completed"))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())