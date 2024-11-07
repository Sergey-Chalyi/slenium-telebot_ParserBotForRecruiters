# Work.ua Resume Parser Bot

A Telegram bot that helps to search and filter resumes from Work.ua, one of the largest job search websites in Ukraine. The bot allows users to specify various search criteria and filters to find relevant candidates.

## Features

- Search resumes by specialty and location
- Select from 29 different professional categories
- Apply various filters:
  - Search parameters (title only, with synonyms, any word)
  - Employment type (full-time, part-time)
  - Age range
  - Gender
  - Salary range
  - Education level
- Get direct links to matching resumes

## Prerequisites

- Python 3.7+
- Chrome browser
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sergey-Chalyi/slenium-telebot_ParserBotForRecruiters.git
cd slenium-telebot_ParserBotForRecruiters
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory and add your Telegram Bot Token:
```
API_TOKEN=your_telegram_bot_token_here
```

## Usage

1. Start the bot:
```bash
python tg_parser_bot.py
```

2. In Telegram, find your bot and start interaction with `/start` command

3. Follow the bot's prompts to:
   - Select website (currently only work.ua is supported)
   - Enter desired specialty
   - Specify location
   - Choose professional category
   - Apply filters as needed

## Project Structure

- `tg_parser_bot.py` - Main Telegram bot file with user interaction logic
- `work_au_parser.py` - Selenium-based parser for work.ua website
- `requirements.txt` - Project dependencies

## Available Categories

1. IT, computers, internet
2. Administration, middle management
3. Construction, architecture
4. Accounting, audit
5. Hotel and restaurant business, tourism
6. Design, creativity
7. Media, publishing, printing
8. Beauty, fitness, sports
9. Culture, music, show business
10. Logistics, warehouse, FEA
11. Marketing, advertising, PR
12. Medicine, pharmaceuticals
13. Real estate
14. Education, science
15. Security, safety
16. Sales, procurement
17. Working specialties, production
18. Retail
19. Secretariat, office management
20. Agriculture, agribusiness
21. Insurance
22. Service industry
23. Telecommunications
24. Top management
25. Transport, auto business
26. HR management
27. Finance, banking
28. Law
29. Other spheres of activity


## Technical Details

The project uses:
- `selenium` for web scraping
- `pyTelegramBotAPI` for Telegram bot functionality
- `python-dotenv` for environment variables management
- Chrome WebDriver in headless mode

## Error Handling

- The bot includes comprehensive error handling for:
  - Invalid user inputs
  - Website parsing errors
  - Connection timeouts
  - Network issues
  - Unsupported message types (voice, audio, video)

## Limitations

- Currently only supports work.ua website
- Some resume details might be inaccessible due to website restrictions
- Rate limiting may apply
- Requires stable internet connection

## Security Notes

- Bot token should be kept secure and never committed to version control
- The parser respects website's robots.txt and includes appropriate delays between requests
- User data is not stored persistently

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contacts

Email: ch.sergey.rb@gmail.com