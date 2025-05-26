import json


class ConfigManager:
    """Менеджер конфигурации для загрузки настроек из JSON файла"""

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """Загружает конфигурацию из файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Конфигурационный файл {self.config_path} не найден. Используются настройки по умолчанию.")
            return self.get_default_config()
        except json.JSONDecodeError:
            print(f"Ошибка чтения конфигурационного файла {self.config_path}. Используются настройки по умолчанию.")
            return self.get_default_config()

    def get_default_config(self):
        """Возвращает конфигурацию по умолчанию"""
        return {
            "ui": {
                "window": {
                    "title": "Калькулятор",
                    "initial_width": 525,
                    "initial_height": 500,
                    "background_color": "#212224",
                    "icon_path": "img/icon.png"
                },
                "fonts": {
                    "base_font_size": 15,
                    "entry_font_size": 25,
                    "options_font_size": 10
                },
                "colors": {
                    "background": "#212224",
                    "button_default": "#24282c",
                    "button_equals": "#307af7",
                    "text_default": "white"
                }
            },
            "sounds": {
                "default_options": {
                    "enabled": True,
                    "type": "drums"
                },
                "files": {
                    "drums": ["sounds/drums1.wav"],
                    "memes": ["sounds/mem1.wav"]
                }
            }
        }

    def get(self, *keys):
        """Получает значение из конфигурации по ключам"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def save_config(self):
        """Сохраняет текущую конфигурацию в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
