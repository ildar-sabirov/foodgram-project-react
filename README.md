## О проекте:
![workflow](https://github.com/ildar-sabirov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

---
+ Адрес сайта: diplom.sytes.net
+ Email администратора: admin@admin.ru
+ Пароль администратора: admin
---
Foodgram - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии:

+ python 3.10.12
+ Django 3.2.3
+ djangorestframework 3.12.4
+ JSON Web Token Authentication
+ SQLite
+ gunicorn
+ nginx
+ Docker

## Установка проекта:

Клонируйте репозиторий:
```
git clone git@github.com:ildar-sabirov/foodgram-project-react.git
```
Заполните .env по примеру .env.example.

## Собираем образы Docker:

В терминале в корне проекта Foodgram последовательно выполните команды из листинга; замените username на ваш логин на Docker Hub:
```
cd frontend  # В директории frontend...
docker build -t username/foodgram_frontend .
cd ../backend  # То же в директории backend...
docker build -t username/foodgram_backend .
```

## Загружаем образы на Docker Hub:

Отправьте собранные образы фронтенда и бэкенда на Docker Hub:
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
```

## Настраиваем и копируем конфиг для сервера:

В docker-compose.production.yml замените username на ваш логин на Docker Hub.

Скопируйте на сервер в директорию foodgram/ файл docker-compose.production.yml. 
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram/docker-compose.production.yml
```

- `path_to_SSH` — путь к файлу с SSH-ключом;
- `SSH_name` — имя файла с SSH-ключом (без расширения);
- `username` — ваше имя пользователя на сервере;
- `server_ip` — IP вашего сервера.

Скопируйте файл .env на сервер, в директорию foodgram/.

## Устанавливаем Docker Compose на сервер:

Поочерёдно выполните на сервере команды для установки Docker и Docker Compose для Linux.
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

## Запускаем Docker Compose на сервере:

Для запуска Docker Compose в режиме демона команду docker compose up нужно запустить с флагом -d. Выполните эту команду на сервере в папке foodgram/:
```
sudo docker compose -f docker-compose.production.yml up -d
```
Сразу после запуска всех контейнеров Docker Compose перейдёт в фоновый режим, а вы сможете вводить новые команды в терминал. 

Выполните миграции, соберите статические файлы бэкенда:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

## Перенаправляем все запросы на докер.

На сервере в редакторе nano откройте конфиг Nginx: nano /etc/nginx/sites-enabled/default. Измените настройки location в секции server.
```
location / {
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_pass              http://127.0.0.1:здесь_указать_порт_контейнера_nginx;
```

Перезагрузите конфиг Nginx:
```
sudo service nginx reload
```

Откройте в браузере страницу админки вашего проекта — https://ваш_домен/ cтраница должна отображаться правильно, со стилевым оформлением. Если же статика всё равно не подгрузилась, очистите кеш браузера и перезагрузите страницу.

## Настройка CI/CD:

Workflow уже создан, замените username на ваш логин на Docker Hub по пути:
```
foodgram/.github/workflows/main.yml
```

Осталось настроить переменные c токенами, паролями и другими приватными данными на платформе GitHub Actions.

Перейдите в настройки репозитория — Settings, выберите на панели слева Secrets and Variables → Actions, нажмите New repository secret.

Сохраните переменные `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `SSH_KEY`, `SSH_PASSPHRASE`, `USER`, `HOST`, `TELEGRAM_TO` и `TELEGRAM_TOKEN` с необходимыми значениями: введите имя секрета и его значение, затем нажмите Add secret.

## Автор:
Ильдар Сабиров - [ildar-sabirov](https://github.com/ildar-sabirov)
