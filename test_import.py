import sys
import os

# Добавляем backend в PYTHONPATH
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from app.core.database import get_db
    print("✅ Импорт успешен!")
    print("Функция get_db:", get_db)
except Exception as e:
    print("❌ Ошибка импорта:", e)
    import traceback
    traceback.print_exc()