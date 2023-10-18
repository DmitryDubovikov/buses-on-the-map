# Автобусы на карте Москвы

Веб-приложение показывает передвижение автобусов на карте Москвы.

<img src="screenshots/buses.gif">

## Как запустить

- Скачайте код
- Откройте в браузере файл index.html


## Настройки

Внизу справа на странице можно включить отладочный режим логгирования и указать нестандартный адрес веб-сокета.

<img src="screenshots/settings.png">

Настройки сохраняются в Local Storage браузера и не пропадают после обновления страницы. Чтобы сбросить настройки удалите ключи из Local Storage с помощью Chrome Dev Tools —> Вкладка Application —> Local Storage.

Если что-то работает не так, как ожидалось, то начните с включения отладочного режима логгирования.

## Формат данных

Фронтенд ожидает получить от сервера JSON сообщение со списком автобусов:

```js
{
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
  ]
}
```

Те автобусы, что не попали в список `buses` последнего сообщения от сервера будут удалены с карты.

Фронтенд отслеживает перемещение пользователя по карте и отправляет на сервер новые координаты окна:

```js
{
  "msgType": "newBounds",
  "data": {
    "east_lng": 37.65563964843751,
    "north_lat": 55.77367652953477,
    "south_lat": 55.72628839374007,
    "west_lng": 37.54440307617188,
  },
}
```



## Используемые библиотеки

- [Leaflet](https://leafletjs.com/) — отрисовка карты
- [loglevel](https://www.npmjs.com/package/loglevel) для логгирования


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).

# Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```bash
pip install -r requirements.txt
```

# Как запустить

```bash
python server.py
```

```bash
python fake_bus.py
```

Вы можете установить значения параметров, передав их как аргументы командной строки при запуске скрипта server.py:

```bash
python server.py -host your_host_value -browser_port your_browser_port_value -bus_port your_bus_port_value
```
Если параметры не указаны явно при запуске, они примут значения по умолчанию:

    host: "127.0.0.1"
    browser_port: "8000"
    bus_port: "8080"

Вы можете установить значения параметров, передав их как аргументы командной строки при запуске скрипта fake_bus.py:

```bash
python fake_bus.py -host your_host_value -port your_port_value -r your_routes_number -b your_buses_per_route -id your_emulator_id -w your_websockets_number
```

Если параметры не указаны явно при запуске, они примут значения по умолчанию:

    host: "127.0.0.1"
    port: "8080"
    routes_number: None
    buses_per_route: 1
    emulator_id: "1"
    websockets_number: 5
