# Python Auth Project

## Возможности
- Регистрация по email и паролю.
- Пароли хранятся не в открытом виде, а в виде хеша.
- Пользователи сохраняются локально в `users.json`.
- Вход и выход из аккаунта.
- Авторизация через Google OAuth.
- Профиль авторизованного пользователя.

## Запуск

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Скопируй `.env.example` в `.env`.

Минимально задай:
```env
SECRET_KEY=любая-длинная-случайная-строка
```

После этого запусти:
```bash
python app.py
```

Открой:
http://127.0.0.1:5000

## Google
Для кнопки Google нужно создать OAuth 2.0 Client ID в Google Cloud Console.

В Authorized redirect URIs добавь:
http://127.0.0.1:5000/auth/google/callback

Затем впиши данные в `.env`:
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

Без Google Client ID/Secret регистрация и вход по email/паролю будут работать, а Google OAuth - нет.

## Важно
`users.json` хранит аккаунты локально. Для настоящего продакшн-сайта лучше использовать PostgreSQL/MySQL и дополнительные меры защиты.
