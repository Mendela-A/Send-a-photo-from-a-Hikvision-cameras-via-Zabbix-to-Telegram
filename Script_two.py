#!/usr/lib/zabbix/alertscripts/pic_get/bin/python3
import requests
from dotenv import load_dotenv
import os
import sys

# Завантаження змінних середовища
load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

def validate_environment():
    """Перевірка наявності необхідних змінних середовища"""
    if not bot_token:
        print("Error: BOT_TOKEN not set in .env file")
        sys.exit(1)
    if not chat_id:
        print("Error: CHAT_ID not set in .env file")
        sys.exit(1)

def validate_arguments():
    """Перевірка аргументів командного рядка"""
    if len(sys.argv) < 4:
        print("Usage: script.py <arg1> <filename> <caption>")
        print("Example: script.py alert photo123 'Alert message'")
        sys.exit(1)

def send_photo_with_text(photo_path, text):
    """Відправка фото з текстом до Telegram"""
    
    # Перевірка існування файлу
    if not os.path.exists(photo_path):
        print(f"Error: File '{photo_path}' not found")
        sys.exit(1)
    
    # Перевірка чи це дійсно файл
    if not os.path.isfile(photo_path):
        print(f"Error: '{photo_path}' is not a file")
        sys.exit(1)
    
    try:
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': ('image.jpg', photo_file, 'image/jpeg')}
            data = {
                'chat_id': chat_id,
                'caption': text
            }
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            
            # Відправка запиту з timeout
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            # Перевірка відповіді
            if response.status_code == 200:
                print("Photo sent successfully")
                result = response.json()
                if result.get('ok'):
                    print(f"Message ID: {result['result']['message_id']}")
            else:
                print(f"Error: Failed to send photo")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data.get('description', 'Unknown error')}")
                except:
                    print(f"Response: {response.text}")
                sys.exit(1)
                
            return response
            
    except FileNotFoundError:
        print(f"Error: Cannot open file '{photo_path}'")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timeout. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error - {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Валідація
    validate_environment()
    validate_arguments()
    
    # Формування шляху до файлу
    photo_path = f"/tmp/data/{sys.argv[2]}.jpg"
    caption_text = sys.argv[3]
    
    # Відправка фото
    send_photo_with_text(photo_path, caption_text)
