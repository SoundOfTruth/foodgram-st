# foodgram-st

## Описание

## Стек технологий

- **Backend**: Python 3, Django, Django REST Framework, PostgreSQL
- **Frontend**: React
- **Контейнеризация**: Docker, Docker Compose
- **Web-сервер**: Nginx

### 1. Клонирование репозитория

```bash
git clone https://github.com/SoundOfTruth/foodgram-st.git
cd foodgram-st
```

### 2. Enviroment

Для запуска проекта необходимо создать .env файл
и по примеру из .env.example его заполнить

### 3. Запуск контейнеров

Перейдите в папку **infra** и запустите контейнеры с помощью:
```bash
cd infra
docker compose up -d
```

Запуск контейнеров для разработки с запущенным бекендом вне докера
```bash
docker compose -f docker-compose-dev.yml up -d
```

### 4. Загрузка данных

Все данные загружаются автоматически через скрипт data/set_up_data.sh
Загрузку можно отключить убрав команду bash data/set_up_data.sh
из сервиса бэкенда в infra/docker-compose.yml, либо поменяв на set_up_ingredients.sh
для загрузки исключительно ингредиентов

### 5. Доступ к проекту

* Главная страница: http://localhost
* Документация API: http://localhost/api/docs/
* Админ-панель Django: http://localhost/admin

### 6. Остановка сервисов
Для остановки контейнеров выполните:
```bash
docker-compose down
```
