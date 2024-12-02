# BMSTU DIRECT: бот обратной связи

## Как запускать

Требует `docker` для запуска

```shell
  docker compose -f docker-compose.yml --env-file .env up --build
```

Загружает окружение из `.env` файла. Пример содержимого `.env` представлен в файле .env-example

## Как создать .env

```shell
    cp .env-example .env
```


## Структура бота
``` 
├── config.py         - парсер енв файла
├── core              - сам бот
  ├── filters         - фильтры, используемые при обработке хендлеров
    └── role.py       - для отличия обычных юзеров и админов.
  ├── handlers        - сами хендлеры
    ├── admin.py      - для админов
    └── user.py       - и обычных пользователей соответсвенно
  ├── middlewares
    ├── db.py
    ├── role.py         - определяем роль
    └── user_control.py - мидлваря с полезным функционалом 
  ├── models
    ├── enums.py       - модель ролей пользователей
  ├── states           - стейты
    └── ticket_states.py
  ├── text
    └── text.py
  └── utils
      ├── funcs.py
      ├── keyboards.py - например клавиатуры
      └── variables.py - и какие то переменные
├── services          - вспомогательные самописные модули
    ├── db            - бд
      ├── base.py      - файлы ниже для подключения и описания моделей 
      ├── db_pool.py
      ├── models.py
      └── services
         └── repository. py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── config. py
├── README.md
├── requirements.txt
└── services
    ├── db
      ├── base.py
      ├── db_pool.py
      ├── models.py
      └── services
         └── repository. py  - сам интерфейс для взаимодействия с бд.
```