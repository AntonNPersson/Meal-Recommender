from Backend.Services.telegram_service import TelegramBotService

def main():
    secret_api_key = "7757803111:AAHRr2uxq_RQHqt9Qn31VOHQdh2IKjU9kUA" # ITS SECRET, DO NOT SHARE! :D
    telegram_bot_service = TelegramBotService(secret_api_key)

    telegram_bot_service.start()

if __name__ == "__main__":
    main()