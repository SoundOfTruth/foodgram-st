# foodgram-st

## Описание
Foodgram — это веб-приложение для обмена рецептами со следующими функциями:
- Публикация рецептов.
- Просмотр рецептов как своих так и других пользователей.
- Добаваление рецептов в избранное.
- Добавление рецептов в список покупок.
- Скачивание списка покупок в формате csv.
- Подписка на других пользователей.
## Стек технологий

- **Backend**: Python 3.10, Django, Django REST Framework, PostgreSQL
- **Frontend**: React
- **Контейнеризация**: Docker, Docker Compose
- **Web-сервер**: Nginx

### 1. Клонирование репозитория

```bash
git clone https://github.com/SoundOfTruth/foodgram-st.git
cd foodgram-st
```

### 2. Enviroment

Для запуска проекта необходимо создать и заполнить .env файл
по примеру ниже, либо из .env.example

```bash
SECRET='secret'
DEBUG='False'
POSTGRES_DB='django'
POSTGRES_USER='django_user'
POSTGRES_PASSWORD='mysecretpassword'
DB_HOST='db'
DB_PORT='5432'
ALLOWED_HOSTS='127.0.0.1, localhost, frontend'
```

### 3. Запуск контейнеров

Перейдите в папку **infra** и запустите контейнеры с помощью:
```bash
cd infra
docker compose up -d
```

Запуск контейнеров для разработки с запущенным бекендом вне докера
```bash
cd infra-dev
docker compose -f docker-compose-dev.yml up -d
```

### 4. Загрузка данных

Все данные загружаются автоматически через заготовленные скрипты
Загрузку можно отключить убрав команду bash data/set_up_data.sh
из сервиса бэкенда в infra/docker-compose.yml.
для очиски бд от тестовых данных можно использовать
```bash
docker exec foodgram-backend python manage.py flush --no-input
```
для загрускит только ингредиентов можно использовать
```bash
docker exec foodgram-backend bash data/set_up_ingredients.sh
```

### 5. Доступ к проекту

* Главная страница: http://localhost
* Документация API: http://localhost/api/docs/
* Админ-панель Django: http://localhost/admin

### 6. Остановка сервисов
Для остановки контейнеров выполните:
```bash
docker compose down
```

## Примеры API-запросов

### Получение списка рецептов
```http
GET /api/recipes/
```

#### Пример ответа:
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 3,
            "author": {
                "email": "admin@admin.admin",
                "id": 2,
                "username": "admin",
                "first_name": "admin",
                "last_name": "admin",
                "is_subscribed": false,
                "avatar": null
            },
            "ingredients": [
                {
                    "id": 1326,
                    "name": "пиво",
                    "measurement_unit": "мл",
                    "amount": 250
                },
                {
                    "id": 1228,
                    "name": "пельмени",
                    "measurement_unit": "г",
                    "amount": 250
                }
            ],
            "name": "Пельмени с пивом",
            "image": "http://localhost/media/recipes/images/cedbf7a8-12e9-4b8d-8e30-1af316b312f3.jpeg",
            "text": "Пельмени с пивом.",
            "cooking_time": 15,
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 2,
            "author": {
                "email": "test@test.test",
                "id": 1,
                "username": "test",
                "first_name": "test",
                "last_name": "test",
                "is_subscribed": false,
                "avatar": null
            },
            "ingredients": [
                {
                    "id": 1749,
                    "name": "сыр",
                    "measurement_unit": "г",
                    "amount": 500
                }
            ],
            "name": "Сыр",
            "image": "http://localhost/media/recipes/images/7ed1f688-ec6f-4a45-bc28-5d8c05e0366a.jpeg",
            "text": "Просто сыр",
            "cooking_time": 1,
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 1,
            "author": {
                "email": "test@test.test",
                "id": 1,
                "username": "test",
                "first_name": "test",
                "last_name": "test",
                "is_subscribed": false,
                "avatar": null
            },
            "ingredients": [
                {
                    "id": 255,
                    "name": "водка",
                    "measurement_unit": "мл",
                    "amount": 500
                },
                {
                    "id": 505,
                    "name": "кальмары",
                    "measurement_unit": "г",
                    "amount": 1000
                }
            ],
            "name": "Вкусное комбо",
            "image": "http://localhost/media/recipes/images/054c0ea2-7ce0-4119-b548-a7e0e314c611.jpeg",
            "text": "вк.",
            "cooking_time": 5,
            "is_favorited": false,
            "is_in_shopping_cart": false
        }
    ]
}
```

### Добавление рецепта (POST)
```http
POST /api/recipes/
```

#### Тело запроса:
```json
{
  "name": "Солянка",
  "ingredients": [
    {
      "id": 252,
      "amount": 400
    }
  ],
  "cooking_time": 60
} 
```

### Удаление рецепта (DELETE)
```http
DELETE /api/recipes/1/
```

## Автор

Думлер Евгений Алексаднрович
ОмГТУ Информатика и вычислительная техника 3 курс