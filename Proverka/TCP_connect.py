import socket
import time
import statistics
from urllib.parse import urlparse


def simple_tcp_ping(url, count=5, port=None):
    """
    Упрощенная версия TCP ping с возможностью указания порта
    """
    # Извлекаем hostname
    if url.startswith(('http://', 'https://')):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not port:  # Если порт не указан явно, используем из URL или по умолчанию
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    else:
        hostname = url
        if not port:
            port = 80  # Порт по умолчанию

    # Получаем IP
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"Ошибка: не удается разрешить {hostname}")
        return

    print(f"TCP PING {hostname} ({ip_address}):{port}")

    times = []
    successful = 0

    for i in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            start = time.time()
            sock.connect((ip_address, port))
            elapsed = (time.time() - start) * 1000
            sock.close()

            times.append(elapsed)
            successful += 1
            print(f"tcp_seq={i + 1} connect time={elapsed:.1f} ms")

        except socket.timeout:
            print(f"tcp_seq={i + 1} timeout")
            times.append(None)
        except Exception as e:
            print(f"tcp_seq={i + 1} failed: {e}")
            times.append(None)

        if i < count - 1:
            time.sleep(1)

    # Статистика
    print(f"\n--- {hostname}:{port} tcp statistics ---")
    loss = ((count - successful) / count) * 100
    print(f"{count} attempts, {successful} successful, {loss:.0f}% failure")

    good_times = [t for t in times if t is not None]
    if good_times:
        min_t = min(good_times)
        avg_t = statistics.mean(good_times)
        max_t = max(good_times)
        dev_t = statistics.mean([abs(t - avg_t) for t in good_times])
        print(f"connect min/avg/max/dev = {min_t:.3f}/{avg_t:.3f}/{max_t:.3f}/{dev_t:.3f} ms")


# Основная программа с выбором порта
if __name__ == "__main__":
    website = input("Введите URL или IP адрес: ").strip()

    if website:
        port_input = input("Порт (по умолчанию автоопределение): ").strip()
        port = int(port_input) if port_input else None

        simple_tcp_ping(website, 5, port)
    else:
        print("Не указан URL")