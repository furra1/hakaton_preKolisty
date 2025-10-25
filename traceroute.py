import subprocess
import platform
import sys
from urllib.parse import urlparse

def normalize_hostname(hostname):
    """Извлекает hostname из URL если необходимо"""
    if hostname.startswith(('http://', 'https://')):
        parsed = urlparse(hostname)
        return parsed.hostname or hostname
    return hostname

def get_traceroute_command(hostname, max_hops):
    """Возвращает команду traceroute для текущей ОС"""
    if platform.system().lower() == "windows":
        return ["tracert", "-h", str(max_hops), "-w", "3000", hostname]
    else:
        return ["traceroute", "-m", str(max_hops), "-w", "3", "-q", "1", hostname]

def fix_encoding(text):
    """Исправляет проблемы с кодировкой текста"""
    try:
        # Пробуем разные кодировки
        for encoding in ['utf-8', 'cp866', 'cp1251', 'iso-8859-1']:
            try:
                return text.encode('utf-8').decode(encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
        return text
    except:
        return text

def execute_traceroute(hostname, max_hops=30):
    """
    Выполняет трассировку маршрута к указанному хосту
    """
    # Подготовка параметров
    target = normalize_hostname(hostname)
    
    print(f"\nTRACEROUTE {target}")
    print(f"Максимум прыжков: {max_hops}")
    print("─" * 60)
    
    try:
        # Формируем команду
        command = get_traceroute_command(target, max_hops)
        
        # Выполняем команду с правильной кодировкой
        if platform.system().lower() == "windows":
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='cp866',  # Кодировка для русской Windows
                timeout=120
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Кодировка для Linux/Mac
                timeout=120
            )
        
        # Обрабатываем результат
        if result.returncode == 0:
            output = fix_encoding(result.stdout)
            print(output)
            return True
        else:
            error_msg = fix_encoding(result.stderr)
            if "не найден" in error_msg or "not found" in error_msg:
                print("Ошибка: Команда traceroute/tracert не найдена")
                print("Убедитесь, что traceroute установлен в системе")
            else:
                print(f"Ошибка выполнения: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Таймаут: трассировка заняла слишком много времени")
        return False
    except FileNotFoundError:
        print("Ошибка: Команда traceroute/tracert недоступна")
        print("\nДля установки:")
        if platform.system().lower() == "windows":
            print("• Traceroute встроен в Windows как 'tracert'")
        else:
            print("• Ubuntu/Debian: sudo apt install traceroute")
            print("• CentOS/RHEL: sudo yum install traceroute")
            print("• macOS: предустановлен")
        return False
    except UnicodeDecodeError as e:
        print(f"Ошибка кодировки: {e}")
        print("Попробуйте изменить настройки консоли")
        return False
    except Exception as error:
        print(f"Неожиданная ошибка: {error}")
        return False

def main():
    """Основная функция программы"""
    print("ПРОВЕРКА TRACEROUTE")
    print("=" * 50)
    
    # Настраиваем кодировку вывода
    try:
        if platform.system().lower() == "windows":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass
    
    # Получаем целевой хост
    if len(sys.argv) > 1:
        target = sys.argv[1]
        max_hops = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    else:
        target = input("Введите домен или IP-адрес: ").strip()
        if not target:
            print("Не указан целевой адрес")
            return
        
        try:
            hops_input = input("Максимум прыжков [30]: ").strip()
            max_hops = int(hops_input) if hops_input else 30
        except ValueError:
            print("Используется значение по умолчанию: 30 прыжков")
            max_hops = 30
    
    # Выполняем трассировку
    success = execute_traceroute(target, max_hops)
    
    # Итоговое сообщение
    if success:
        print("\nТрассировка завершена")
    else:
        print("\nТрассировка не удалась")

# Альтернативная версия с использованием chcp для Windows
def execute_traceroute_windows_fixed(hostname, max_hops=30):
    """Версия для Windows с исправлением кодировки через chcp"""
    if platform.system().lower() != "windows":
        return execute_traceroute(hostname, max_hops)
    
    target = normalize_hostname(hostname)
    
    print(f"\nTRACEROUTE {target}")
    print(f"Максимум прыжков: {max_hops}")
    print("─" * 60)
    
    try:
        # Сначала меняем кодировку консоли на UTF-8
        chcp_result = subprocess.run(["chcp", "65001"], capture_output=True, shell=True)
        
        # Выполняем tracert
        command = ["tracert", "-h", str(max_hops), "-w", "3000", target]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Ошибка: {result.stderr}")
            return False
            
    except Exception as error:
        print(f"Ошибка: {error}")
        return False

# Простая версия без обработки кодировки (вывод как есть)
def execute_traceroute_simple(hostname, max_hops=30):
    """Простая версия без сложной обработки кодировки"""
    target = normalize_hostname(hostname)
    
    print(f"\nTRACEROUTE {target}")
    print(f"Максимум прыжков: {max_hops}")
    print("─" * 60)
    
    try:
        command = get_traceroute_command(target, max_hops)
        
        # Просто запускаем команду без перехвата вывода
        result = subprocess.run(command, timeout=120)
        
        if result.returncode == 0:
            print("\nТрассировка завершена")
            return True
        else:
            print("\nТрассировка завершена с ошибкой")
            return False
            
    except Exception as error:
        print(f"Ошибка: {error}")
        return False

if __name__ == "__main__":
    # Пробуем разные методы в зависимости от ОС
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Введите домен или IP-адрес: ").strip()
    
    if target:
        if platform.system().lower() == "windows":
            # Для Windows пробуем улучшенную версию
            execute_traceroute_windows_fixed(target)
        else:
            # Для Linux/Mac используем стандартную версию
            execute_traceroute(target)