#!/bin/bash

# Обновляем pip
pip install --upgrade pip

# Устанавливаем системные зависимости
apt-get update
apt-get install -y gcc g++

# Устанавливаем Python зависимости
pip install --no-cache-dir -r requirements.txt

# Запускаем миграции
alembic upgrade head