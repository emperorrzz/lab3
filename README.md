# Калькулятор ипотеки

Учебный CI/CD: Python, unittest, GitHub Actions, Ubuntu 22.04 LTS.
Без Docker, линтера и сторонних зависимостей Python.

## Локальный запуск

```bash
python -m unittest discover -s tests -v
python app.py
```

Открыть http://127.0.0.1:8000.

## GitHub

Создать пустой репозиторий без README, затем из папки проекта:

```bash
git add .
git commit -m "Add mortgage calculator and GitHub Actions"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Заменить адрес своим. Git должен быть авторизован в GitHub.
Для первого коммита настроить свои `git config user.name` и `git config user.email`.

## Виртуалка Ubuntu 22.04

Виртуалке нужен интернет и доступ с Windows для просмотра приложения.
Для учебного runner на сервере использовать приватный репозиторий.

```bash
sudo apt update
sudo apt install -y python3 git curl
sudo adduser runner
sudo -iu runner
```

В репозитории GitHub: Settings → Actions → Runners → New self-hosted runner → Linux x64.
Выполнить предложенные GitHub команды в `/home/runner/actions-runner`.
При регистрации добавить метку `mortgage`, стандартные метки сохранить.
Runner регистрировать от пользователя `runner`, не root.

В каталоге runner:

```bash
sudo ./svc.sh install runner
sudo ./svc.sh start
cd /home/runner
git clone https://github.com/USERNAME/REPOSITORY.git mortgage-source
cd mortgage-source
sudo bash deploy/setup.sh runner
```

При клонировании приватного репозитория потребуется авторизация GitHub.
Если UFW включён, разрешить порт: `sudo ufw allow 8000/tcp`.
Открыть с Windows `http://<IP-виртуалки>:8000`.

## Как работает поставка

После push запускается job test на Ubuntu runner GitHub. После успешных тестов
push в main запускает job deploy на виртуалке. Он получает тот же коммит,
копирует приложение в /opt/mortgage, записывает SHA в VERSION, перезапускает
mortgage.service и проверяет /health. Для остальных веток и pull request — только тесты.

Пока runner виртуалки не подключён, deploy ожидает его: поставка ещё не выполнена.
Приложение работает отдельной службой systemd, в том числе после перезагрузки.
Падение тестов блокирует deploy. Автоматический откат при ошибке самого deploy
в этом базовом варианте не реализован.

## Демонстрация

1. Показать приложение и тесты во вкладке Actions.
2. Изменить TITLE в app.py, сделать commit и push в main.
3. Дождаться test и deploy, обновить страницу виртуалки: название и SHA изменятся.
4. Временно сломать формулу и сделать push: test упадёт, deploy будет пропущен,
   сервер сохранит предыдущую версию.
5. Исправить формулу новым коммитом и сделать push.

Диагностика: `systemctl status mortgage.service`,
`sudo journalctl -u mortgage.service -n 50`, `curl http://127.0.0.1:8000/health`.
