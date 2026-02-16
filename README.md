# Yandex.Music2YoutubeMusicMigrationTool
Portable executable Yandex Music to YouTube Music migration tool.
## **ENGLISH**
YaMusic 2 YTMusic Transfer Tool
Inspired by gosha20777/yandex2ytmusic

A desktop utility designed to migrate your "Liked" tracks from Yandex Music to YouTube Music with automated matching and duplicate protection.

1. YouTube Authentication
YouTube Music requires a session cookie to act on your behalf.
- Open [YouTube Music](https://music.youtube.com) in your browser.
- Press `F12` to open Developer Tools and navigate to the **Network** tab.
- Find request (e.g., `browse`), right-click it, and select **Copy** -> **Copy as cURL (bash)**.
- Go to the https://curlconverter.com/json/ and paste your cURL command to extract the JSON.
- Find headers {} and copy the entire file in the correct format (see your correct headers.json will look like this.txt).
- Save the resulting JSON into a file named `headers.json` in the application folder.

2. Yandex Authentication
- Obtain your **Yandex OAuth Token**.
- Paste this token into the application's input field and click **Verify Token**.

3. Migration Process
- Select a destination playlist from the dropdown.
- Click **Start Transfer**. 
- *Note: The button requires a double-click (confirmation) to prevent accidental starts.*

## Technical Features

Smart Caching: Stores matches in `music_cache.db` to avoid redundant API calls.
Real-time Logging: Integrated console with color-coded success and error messages.
Batch Resilience: Automatically switches to single-track mode if a batch upload fails.
Fuzzy Matching: Uses a 70% similarity threshold for high-accuracy track identification.

## Credits
This project was inspired by the original CLI version by [gosha20777](https://github.com/gosha20777/yandex2ytmusic).

## **РУССКИЙ**
YaMusic 2 YTMusic Migration tool
Основан на проекте gosha20777/yandex2ytmusic

Инструмент для автоматизированного переноса понравившихся треков из Яндекс.Музыки в YouTube Music.

1. Подготовка YouTube:
   - Откройте YouTube Music в браузере (Chrome/Edge).
   - Нажмите `F12` -> вкладка `Network` (Сеть).
   - Найдите запрос (например, `browse`), кликните правой кнопкой -> `Copy` -> `Copy as cURL (bash)`.
   - Перейдите на сайт https://curlconverter.com/json/ и вставьте туда cURL, чтобы получить чистый JSON.
   - Найдите headers {} и скопируйте целиком в корректном формате (смотреть your correct headers.json will look like this.txt).
   - Сохраните этот JSON в файл `headers.json` в папке с программой.

2. Подготовка Yandex:
   - Получите свой OAuth-токен.
   - Вставьте его в соответствующее поле в программе.

3. Запуск:
   - Вставьте свой yandex_token
   - Запустите `ya2ytmusic.exe`.
   - Нажмите "Verify Token" для проверки связи.
   - Выберите плейлист или создайте новый.
   - Нажмите "Start Transfer" (потребуется двойное подтверждение).

## Технические особенности
- Кэширование: Программа создает `music_cache.db`. Если вы запускаете перенос повторно, она не будет заново искать уже сопоставленные треки, что экономит время и лимиты API.
- Логи: Все ошибки и успехи отображаются в реальном времени в окне консоли внутри интерфейса.
- Безопасность: Токены хранятся локально в `settings.json`.

## Ограничения
- YouTube может временно заблокировать добавление треков, если их слишком много (более 200 за раз). Программа автоматически замедляется или переходит на поштучное добавление при возникновении ошибок 400.

## Благодарности
Этот проект был вдохновлен оригинальной версией CLI от [gosha20777](https://github.com/gosha20777/yandex2ytmusic).

<img width="291" height="426" alt="python_5AAVZhGqMt" src="https://github.com/user-attachments/assets/2508aefb-edfb-4bbd-96c1-97a63ddbb99f" />
