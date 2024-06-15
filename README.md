## Запуск

### 1. Установка
* [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Клонирование
```
git clone https://github.com/rTiRe/crud_tours.git
cd crud_tours
```

### 3. Создание файла окружения
В основной папке присутствует файл-пример `.env.example`.
Для начала работы его достаточно переименовать в `.env`, но, конечно, желательно поменять значения.
* `POSTGRES_HOST` - адрес postgres.
* `POSTGRES_PORT` - порт, на котором запущена БД
* `POSTGRES_DB` - имя используемой базы данных
* `POSTGRES_USER` - имя пользователя postgres
* `POSTGRES_PASSWORD` - пароль postgres
* `APP_PORT` - порт, на котором запущено приложение
* `APP_HOST` - хост, на котором будет запущено приложение
* `SMTP_HOST` - хост smtp сервера
* `SMTP_PORT` - порт smtp сервера
* `SMTP_USERNAME` - имя пользователя smtp
* `SMTP_PASSWORD` - пароль smtp
* `DEBUG_MODE` - дебаг режим

> [!IMPORTANT]
> `POSTGRES_HOST=host.docker.internal` если запуск будет производиться через `docker compose up`
>
> Если запуск будет производиться в режиме `dev mode`, то есть 2 пути:
>
> 1. Ставим `DEBUG_MODE=true`, тогда значение `POSTGRES_HOST` всегда будет равно `127.0.0.1`
>
> 2. Сами, ручками ставим `POSTGRES_HOST`, но не трогаем `DEBUG_MODE`, оставляем в `false`.
>
> `docker compose` **всегда** запускает приложеине на хосту `0.0.0.0`, не зависимо от того, что вы указали в `APP_HOST`.
>
> Без `docker compose` - см. [инструкцию](#Запуск-в-режиме-разработки)

### 4. Управление контейнером

#### Запуск
```
docker compose up
```
#### Запуск в detach режиме
```
docker compose up -d
```
#### Запуск с пребилдом
```
docker compose up --build
```
#### Остановка
```
docker compose stop
```
#### Остановка + удаление
```
docker compose down
```
#### Запуск в режиме разработки
Установите `DEBUG_MODE` значение `true`.
`POSTGRES_HOST` изменится на 127.0.0.1 **принудительно**.

Дальше, котите - запускайте через `uvicorn`, указав при этом желаемый желаемый хост, либо просто запускаете `main.py`, тогда адрес хоста подтянется из `APP_HOST`.

> [!IMPORTANT]
> Необходимо проверить [файл окружения](#3-Создание-файла-окружения)