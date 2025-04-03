=====
Usage
=====

Configuration
============

* Install the module in your Odoo instance
* Configure the "telegram_bot_token" parameter with your Telegram Bot API Token
* Configure the "telegram_chat_id" parameter with the chat ID where notifications should be sent

To obtain a Telegram Bot Token:

1. Start a chat with @BotFather on Telegram
2. Follow the instructions to create a new bot
3. Copy the API token provided

To get your chat ID:

1. Start a chat with your bot
2. Send a message to the bot
3. Access https://api.telegram.org/bot<YourBOTToken>/getUpdates
4. Look for the "chat" object and note the "id" field

Using the module
===============

Once configured, the module will automatically send notifications for the following events:

* Sales Order Confimed
* Quotation Sent
* Sales Order Cancelled

You can customize which events trigger notifications in the module settings.
