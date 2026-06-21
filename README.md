# QIYM — интернет-магазин одежды

Django-приложение с поддержкой трёх языков (казахский, русский, английский).

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Запуск

### 1. Клонировать репозиторий

```bash
cd kiim_shop
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate   # Windows
uv pip install -r requirements.txt
```

### 3. Применить миграции

```bash
python manage.py migrate
```

### 4. Создать суперпользователя (для доступа в админку)

```bash
python manage.py createsuperuser
```

### 5. Запустить сервер

```bash
python manage.py runserver
```

Сайт откроется на [http://localhost:8000](http://localhost:8000)  
Админка: [http://localhost:8000/admin](http://localhost:8000/admin)

## Заполнение данными

Через админку нужно создать:

- **Категории** (`/admin/shop/category/`) — например: Мужчины, Женщины, Дети
- **Баннеры** (`/admin/shop/banner/`) — изображения для слайдера на главной
- **Товары** (`/admin/shop/product/`) — с фото, ценой, размерами и цветами

Медиафайлы сохраняются в папку `media/` в корне проекта.

## Структура проекта

```
kiim_shop/
├── kiim_shop/        # настройки Django
├── shop/             # основное приложение
│   ├── models.py     # модели (товары, категории, заказы)
│   ├── views.py      # логика
│   ├── forms.py      # формы
│   └── translations/ # JSON-файлы переводов
├── templates/shop/   # HTML-шаблоны
├── media/            # загружаемые файлы
└── manage.py
```
