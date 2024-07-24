## <a id="title1">Часть 1. О проекте</a>

Swans Telegram Detector - это решение в виде Telegram-бота, позволяющее производить детекцию и классификацию виды лебедей по фотографиям. 


## <a id="title2">Часть 2. Запуск приложения</a>
### Установка вручную

Для того, чтобы запустить приложение, необходимо скачать все зависимости из файла ```requirements.txt```.
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Затем запустите файл main.py. 
```
$ cd tg_bot
$ python main.py
```

### Установка через Docker Compose

Если на вашем компьютере установлен Docker и Docker Compose, то запустите приложение следующей командой

```
$ docker compose up
```

## <a id="title3">Часть 3. Демонстрация работы</a>

<img src="../screencast/screencast.gif" width="600" height="400">

## <a id="title3">Часть 4. Стек технологий</a>

**Используемый стек технологий:**
* Telegram Bot API
* YOLO
* Docker Compose
