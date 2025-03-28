# 🤖 BotReminder

A simple Discord bot to schedule reminders using slash commands. Get notified via channel messages or DMs and interact with reminders using buttons to ✅ mark as done or 🔁 snooze 1 hour.

---

## 🚀 Features

- Create reminders with `/recordatorio` (date, time, message)
- Receive scheduled notifications in a channel or direct message
- Interact with reminders: ✅ Mark as done / 🔁 Snooze 1 hour
- List all your reminders with `/misrecordatorios`
- Delete reminders with `/borrarrecordatorio`

---

## ⚙️ Requirements

- Python 3.10 or higher
- A registered Discord bot with a valid token
- Your Discord server ID (GUILD_ID)

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/JoGaleano/BotReminderGit.git
cd BotReminderGit

2.	Install dependencies:
pip install -r requirements.txt

3.	Create a .env file and add your bot credentials:
TOKEN=your_discord_bot_token
GUILD_ID=your_discord_guild_id

4.	Run the bot:
python bot_recordatorios_slash.py

🌐 Deploying on Railway
	1.	Push your project to GitHub (make sure .env is in .gitignore)
	2.	Create a new project at Railway
	3.	Connect your GitHub repo
	4.	Go to Variables and add:
	•	TOKEN=your_token_here
	•	GUILD_ID=your_guild_id_here
	5.	Railway will auto-detect your Procfile and start the bot ✨

    🔐 Security
	•	Never commit your real .env file
	•	If your token is exposed, rotate it immediately via the Discord Developer Portal

    ✨ Contributions

    Pull requests and suggestions are welcome!

📜 License

MIT © 2025 Jo Galeano