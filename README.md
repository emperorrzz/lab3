# Консольный калькулятор ипотеки

Python, pytest, GitHub Actions, Ubuntu 22.04.

## Запуск на Windows

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
python app.py
```

Программа спрашивает сумму кредита, годовую ставку и срок.
Можно передать значения сразу:

```powershell
python app.py --amount 3000000 --rate 12 --years 20
```

## Разовая подготовка Ubuntu

GitHub Actions Runner уже установлен под пользователем runner
с дополнительной меткой mortgage. Команды ниже выполнять под пользователем art.

Если раньше была установлена веб-версия, сначала убрать её службу:

```bash
sudo systemctl disable --now mortgage.service
sudo rm -f /etc/systemd/system/mortgage.service /etc/sudoers.d/mortgage
sudo systemctl daemon-reload
```

Подготовить папку приложения и права на неё:

```bash
sudo mkdir -p /opt/mortgage
sudo chown -R runner:runner /opt/mortgage
```

Службу GitHub Actions Runner останавливать не нужно.
Вручную копировать код не требуется: после push это сделает pipeline.

## Как работает CI/CD

Всё описано в .github/workflows/ci.yml:

1. После push и pull request задача test устанавливает pytest и запускает тесты на GitHub.
2. Только после успешных тестов push в main запускает задачу deploy на виртуалке.
3. Runner копирует app.py и calculator.py в /opt/mortgage.
4. Запускает установленную программу с примером данных для проверки.
5. Сохраняет SHA коммита в VERSION.

При падении тестов задача deploy пропускается, установленная версия не меняется.
Откат при ошибке самого deploy не реализован.

Консольное приложение запускается по запросу пользователя, печатает расчёт
и завершается. Ему не нужны веб-сервер, открытый порт или отдельная служба.

## Проверка на Ubuntu после успешного pipeline

```bash
python3 /opt/mortgage/app.py
python3 /opt/mortgage/app.py --version
```

Запускать установленную программу из /opt/mortgage, а не копию исходников.

## Демонстрация

1. Показать расчёт на Ubuntu.
2. Изменить TITLE в app.py на Windows, сделать commit и push.
3. Показать успешные test и deploy во вкладке Actions.
4. Снова запустить приложение на Ubuntu: название изменится.
5. Сломать формулу новым коммитом: тесты упадут, поставка будет пропущена.
6. Исправить формулу и отправить новый коммит.
