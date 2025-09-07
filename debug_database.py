import sys
import os

# Добавляем backend в sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print("Проверяем содержимое модуля app.core.database:")
try:
    import app.core.database as db_module
    print("\n✅ Модуль успешно импортирован")
    print("\nАтрибуты модуля:")
    for attr in dir(db_module):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    print("\nПроверяем наличие get_db:")
    if hasattr(db_module, 'get_db'):
        print("✅ get_db найден в модуле")
        print("Тип get_db:", type(db_module.get_db))
        print("Значение get_db:", db_module.get_db)
    else:
        print("❌ get_db НЕ найден в модуле")
        
except Exception as e:
    print(f"\n❌ Ошибка при импорте модуля: {e}")
    import traceback
    traceback.print_exc()