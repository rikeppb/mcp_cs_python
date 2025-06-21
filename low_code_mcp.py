# Import necessary libraries
import os
from typing import Any, Dict

import sys
print(sys.executable)

import google.generativeai as genai
import requests
from dotenv import load_dotenv

print("We are up and running!")

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {api_key}")
if not api_key or api_key.startswith("ADD YOUR"):
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

print(f"Gemini model loaded successfully: {model.model_name}")

PROMPT = "What is the current price of Bitcoin?"
chat = model.start_chat()
response = chat.send_message(PROMPT)
print(response.text)

print(response)

url = f"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
response = requests.get(url)
data = response.json()
print(data)


# Define the function
def get_crypto_price(symbol: str) -> Dict[str, Any]:
    """
    Get the current price of a cryptocurrency from Binance API
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])


price = get_crypto_price("BTCUSDT")
print(f"BTC Price in USDT: {price}")

tools = [
    {
        "function_declarations": [
            {
                "name": "get_crypto_price",
                "description": "Get cryptocurrency price in USDT from Binance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The cryptocurrency trading pair symbol (e.g., BTCUSDT, ETHUSDT). \
                                            The symbol for Bitcoin is BTCUSDT. \
                                            The symbol for Ethereum is ETHUSDT."
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    }
]

PROMPT = "What is the current price of Bitcoin?"
chat = model.start_chat()
response = chat.send_message(PROMPT, tools=tools)
print(response)


price = get_crypto_price("BTCUSDT")

final_response = chat.send_message(str(price))
print(final_response)

print(final_response.text)