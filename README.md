# semester_1

## Установка и запуск проекта

- `git clone https://github.com/Giknyx/semester_1.git` - клонирование репозитория
- `cd semester_1/`
- `poetry install` - создание виртуального окружения и установка зависимостей
- `установите PostgreSQL`
- `sudo -i -u postgres` - вход в консоль postgres. При необходимости, нужно авторизоваться
- `psql`
- `CREATE DATABASE semester_1;` - создание базы данных
- `\q` - выход из psql
- `exit` - выход из консоли postgres
- `cd semester_1/`
- `subl config.py` или `pycharm-professional config.py` - измените файл конфигурации
- `poetry shell` - вход в виртуальное окружение
- `cd semester_1/`
- `export FLASK_APP='manage.py'` - объявление переменной среды
- `python3 create_db.py` - создание таблиц
- `flask db migrate` - миграции
- `python3 manage.py` - запуск сервера
