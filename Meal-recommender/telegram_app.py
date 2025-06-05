from Backend.Services.telegram_service import TelegramBotService

def main():
    secret_api_key = "" # Enter your Telegram Bot API key here
    if not secret_api_key:
        raise ValueError("Please set your Telegram Bot API key in the secret_api_key variable.")
    telegram_bot_service = TelegramBotService(secret_api_key)

    telegram_bot_service.start()

if __name__ == "__main__":
    main()