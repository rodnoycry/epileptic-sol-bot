import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
IS_PROD = os.getenv('IS_PROD') == "true"
BOT_TOKEN = os.getenv('BOT_TOKEN' if IS_PROD else 'DEV_BOT_TOKEN')
SOLANA_ADDRESS = os.getenv('SOLANA_ADDRESS')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
SUPPORT_USERNAME = os.getenv('SUPPORT_USERNAME')
MEMECOIN_CHAT = os.getenv('MEMECOIN_CHAT')
BACKGROUND_VIDEO_PATH = os.getenv('BACKGROUND_VIDEO_PATH')