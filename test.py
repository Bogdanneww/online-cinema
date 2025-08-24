# test.py
try:
    with open("test_file.txt", "w") as f:
        f.write("Цей файл був створений для тестування.")
    print("Файл успішно створено!")
except Exception as e:
    print(f"Помилка: {e}")
