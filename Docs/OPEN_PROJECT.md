# Как открыть проект в Unreal Engine 5.8 (Windows)

Открыть проект прямо с сайта GitHub нельзя: Unreal работает только с папкой на вашем диске.
GitHub — это хранилище и резервная копия. Проект нужно один раз **склонировать** на компьютер,
а дальше просто забирать обновления.

## 1. Что установить один раз

1. **Unreal Engine 5.8** через Epic Games Launcher (у вас уже есть).
2. **Visual Studio 2022** (Community, бесплатная): https://visualstudio.microsoft.com/
   В установщике отметить рабочую нагрузку **«Разработка игр на C++» (Game development with C++)**,
   а справа в её компонентах — **Unreal Engine installer** / **Windows 11 SDK** (или 10 SDK).
   Без Visual Studio C++-проект не соберётся.
3. **GitHub Desktop**: https://desktop.github.com/ — войти под своим аккаунтом GitHub.
   Git LFS в нём уже встроен.

## 2. Скачать проект

1. GitHub Desktop → **File → Clone repository** → вкладка *GitHub.com* → `cheiwe/hello_guest`.
2. **Local path** — короткий путь **без пробелов и кириллицы**, например `C:\Projects\hello_guest`.
   (Длинные пути и русские буквы в пути ломают сборку Unreal.)
3. **Clone**.

Вариант без программ: на странице репозитория **Code → Download ZIP**. Но тогда обновления придётся
скачивать заново целиком, а модели и звуки (Git LFS) в архив могут не попасть. Лучше GitHub Desktop.

## 3. Первое открытие

1. Открыть папку проекта и дважды кликнуть **`HelloGuest.uproject`**.
2. Появится окно *«The following modules are missing or built with a different engine version:
   HelloGuest. Would you like to rebuild them now?»* → **Yes**.
   Первая сборка C++ занимает 2–10 минут, окно может долго ничего не показывать — это нормально.
3. Если редактор пишет, что карта `L_Sandbox` не найдена, — это ожидаемо: её создаёт скрипт.
4. В редакторе: **Tools → Execute Python Script…** → выбрать `Scripts\Editor\create_test_map.py`.
   Появится серый тестовый уровень, он сохранится в `Content/Maps/L_Sandbox`.
5. Нажать **Play** (Alt+P).

Потом проект можно открывать и так: Epic Games Launcher → Unreal Engine → *Library* → *My Projects*,
или в окне выбора проектов при запуске редактора → **Browse** → `HelloGuest.uproject`.

## 4. Если сборка не удалась

Сообщение *«HelloGuest could not be compiled. Try rebuilding from source manually»*:

1. ПКМ по `HelloGuest.uproject` → **Generate Visual Studio project files**
   (на Windows 11 сначала *Show more options*).
2. Открыть появившийся `HelloGuest.sln`.
3. Вверху выбрать конфигурацию **Development Editor** и платформу **Win64**.
4. ПКМ по проекту **HelloGuest** в *Solution Explorer* → **Build**.
5. Скопировать ошибки из окна **Error List** / **Output** и прислать мне.
   Полный лог также лежит в `Saved\Logs\HelloGuest.log`.

## 5. Получать обновления

1. **Закрыть редактор Unreal.**
2. GitHub Desktop → **Fetch origin** → **Pull origin**.
3. Снова открыть `HelloGuest.uproject`; если изменился C++, редактор предложит пересобрать → **Yes**.

## 6. Отправить свои изменения (новые уровни, ассеты)

GitHub Desktop покажет изменённые файлы → внизу написать короткое описание → **Commit to main** →
**Push origin**. После этого я тоже их увижу.
