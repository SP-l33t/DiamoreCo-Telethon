[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/hidden_coding)

[![Static Badge](https://img.shields.io/badge/Telegram-Chat-yes?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/hidden_codding_chat)

[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/DiamoreCryptoBot/app?startapp=737844465)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON 3.10 🔥🔥

> 🇪🇳 README in english available [here](README.md)

## Функционал  
| Функционал                  | Поддерживается |
|-----------------------------|:--------------:|
| Многопоточность             |       ✅        |
| Привязка прокси к сессии    |       ✅        |
| Авто дневная награда        |       ✅        |
| Авто выполнение квестов     |       ✅        |
| Авто игра                   |       ✅        |
| Авто реферал                |       ✅        |
| Поддержка telethon .session |       ✅        |


## [Настройки](https://github.com/AlexKrutoy/DiamoreCoBot/blob/main/.env-example/)
| Настройка                              |                                                                                                                              Описание                                                                                                                               |
|----------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**                  |                                                                                             Данные платформы, с которой запускать сессию Telegram (сток - **Android**)                                                                                              | 
| **GLOBAL_CONFIG_PATH**                 | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
| **CLICKS**                             |                                                                                                  Сколько алмазов бот получит за игру (по умолчанию - [300, 1000])                                                                                                   |
| **AUTO_UPGRADE_CLICKING_POWER**        |                                                                                                Прокачивать кол-во алмазов за клик или нет (по умолчанию - **False**)                                                                                                |
| **AUTO_UPGRADE_CLICKING_POWER_LEVEL**  |                                                                                                Макс уровень прокачки кол-ва алмазов за клик (по умолчанию - **20**)                                                                                                 |
| **AUTO_UPGRADE_TIMER**                 |                                                                                                  Прокачивать длительность игры или нет (по умолчанию - **False**)                                                                                                   |
| **AUTO_UPGRADE_TIMER_LEVEL**           |                                                                                                   Макс уровень прокачки длительности игры (по умолчанию - **20**)                                                                                                   |
| **AUTO_UPGRADE_REDUCE_COOLDOWN**       |                                                                                              Прокачивать уменьшение КД между играми или нет (по умолчанию - **True**)                                                                                               |
| **AUTO_UPGRADE_REDUCE_COOLDOWN_LEVEL** |                                                                                              Макс уровень прокачки уменьшения КД между играми (по умолчанию - **20**)                                                                                               |
| **REF_ID**                             |                                                                                                           Аргумент после ?startapp= в реферальной ссылке                                                                                                            |
| **SESSIONS_PER_PROXY**                 |                                                                                           Количество сессий, которые могут использовать один прокси (По умолчанию **1** )                                                                                           |
| **RANDOM_DELAY_IN_RUN**                |                                                                        Задержка для старта каждой сессии от 1 до установленного значения (по умолчанию : **30**, задержка в интервале 1..30)                                                                        |
| **USE_PROXY_FROM_FILE**                |                                                                                             Использовать-ли прокси из файла `bot/config/proxies.txt` (True / **False**)                                                                                             |
| **DEVICE_PARAMS**                      |                                                                                  Вводить параметры устройства, чтобы сделать сессию более похожую, на реальную  (True / **False**)                                                                                  |
| **DEBUG_LOGGING**                      |                                                                                               Включить логирование трейсбэков ошибок в папку /logs (True / **False**)                                                                                               |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/AlexKrutoy/DiamoreCoBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/AlexKrutoy/DiamoreCoBot.git
cd DiamoreCoBot
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/DiamoreCoBot >>> python3 main.py --action (1/2)
# Or
~/DiamoreCoBot >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/DiamoreCoBot >>> python main.py --action (1/2)
# Или
~/DiamoreCoBot >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```




### Контакты

Для поддержки или вопросов, свяжитесь со мной в Telegram: [@UNKNXWNPLXYA](https://t.me/UNKNXWNPLXYA)