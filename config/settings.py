"""
Configuration settings for the multi-agent debate system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
CODING_DIR = BASE_DIR / "coding"
CODING_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "gpt-4o"
API_KEY = os.getenv("OPENAI_API_KEY")

# Agent configuration
MAX_GROUP_MESSAGES = 15  # Maximum messages per group in Phase 1
MAX_DEBATE_ROUNDS = 10     # Maximum debate rounds in Phase 2

# Termination keywords
REPORT_READY_KEYWORD = "REPORT_READY"
CONSENSUS_REACHED_KEYWORD = "CONSENSUS_REACHED"

# Group names
GROUP_NAMES = ["Group1", "Group2", "Group3"]

# Code execution settings
CODE_EXECUTION_TIMEOUT = 60  # seconds
USE_VIRTUAL_ENV = False  # Set to True to use isolated virtual environments
