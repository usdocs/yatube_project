# Социальная сеть блогеров
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=5fe620)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=ffffff&color=5fe620)](https://www.djangoproject.com/)

### Краткое описание:
Web-приложение для социальной сети, в которой пользователи могут публиковать записи/сообщения и просматривать сообщению других пользователей. Реализованы механизм комментариев к записям, возможность подписки на публикации интересующий авторов.

### Технологии проекта
* Python — высокоуровневый язык программирования.
* Django — высокоуровневый Python веб-фреймворк, который позволяет быстро создавать безопасные и поддерживаемые веб-сайты.

### Web-приложение позволяет:
* работать с публикациями:
  * получать список всех публикаций
  * создавать (обновлять, удалять) публикации

* работать с комментариями к публикациям:
  * добавлять (получать, обновлять, удалять) комментарии

* Получать список сообществ
* Подписываться на пользователей
 

### Как запустить проект (на Windows):

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:usdocs/yatube_project.git 
cd yatube_project 
```

Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```

Обновить менеджер пакетов pip:
```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Перейти в каталог с manage.py
```
cd yatube
```

Выполнить миграции:
```
python manage.py migrate
```

Запустить проект:
```
python manage.py runserver
```

### Разработчик проекта

Автор: Andrey Balakin  
E-mail: [usdocs@ya.ru](mailto:usdocs@ya.ru)
