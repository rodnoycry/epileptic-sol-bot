# 🟥🟩 Generator Bot

A Telegram bot that overlays PNG images on a 🟥🟩 background video

## Features

- Accepts PNG images with transparent backgrounds
- Overlays images on a 🟥🟩 background video
- Simple and user-friendly interface
- Support for custom background videos

## Prerequisites

- Python 3.6 or higher
- FFmpeg installed on your system
  - For Windows: Download from [FFmpeg official website](https://ffmpeg.org/download.html)
  - For Mac: Install via Homebrew: `brew install ffmpeg`
  - For Linux: `sudo apt-get install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rodnoycry/epileptic-sol-bot.git
cd epileptic-sol-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```bash
cp .env.example .env
```

4. Edit `.env` file with your values:

- Get bot token from [@BotFather](https://t.me/BotFather)
- Add Solana address
- Add contract address
- Set support username
- Set memecoin chat username
- Set path to background video
