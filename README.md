# Постим комиксы XKCD

Учебный проект по постингу случайного комикса в группу VK c сайта [xkcd.com](https://xkcd.com).
___________________
### Требования
Нужен Python от версии 3.8.

### Как установить 
Скачайте код.
Нужно запустить `pip` (или `pip3` при наличии конфликтов с Python2) 
для установки зависимостей:
```commandline
pip install -r requirements.txt
```
Рекомендуется использовать [virtual/venv](https:..docs.python.org/3/library/venv.html) 
для изоляции проекта
______
### Переменные окружения
Определите переменную окружения в файле `.env` в формате: `ПЕРЕМЕННАЯ=значение`:
- `VK_TOKEN` — токен для доступа, получение которого описана на странице описания [процедуры Implicit Flow](https://dev.vk.com/api/access-token/implicit-flow-user).
- `GROUP_ID` — id группы, куда будут поститься комиксы

### Работа со скриптом
Перед запуском нужно получить токен для доступа от VK, а перед этим зарегистрировать standalone приложение, 
создать группу для постинга комиксов и заполнить переменные окружения.

После запуска скрипта будет скачан случайный комикс вместе с его комментарием, 
после чего он будет опубликован на стене указанной группы vk, а файл будет стёрт.

### Пример запуска скрипта: 
```commandline
(venv) python load_and_public_comics.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).