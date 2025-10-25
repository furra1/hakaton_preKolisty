import requests
import time
import statistics
import socket
from urllib.parse import urlparse


def advanced_ping_check(url, count=5):
    """
    Выполняет многократную проверку пинга и выводит статистику в формате ping
    """
    # Извлекаем hostname из URL
    if url.startswith(('http://', 'https://')):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
    else:
        hostname = url

    # Получаем IP адрес
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"ping: cannot resolve {hostname}: Unknown host")
        return

    print(f"PING {hostname} ({ip_address}) 56(84) bytes of data.")

    success_count = 0
    ping_times = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(f"https://{hostname}", timeout=10)
            end_time = time.time()

            ping_time = (end_time - start_time) * 1000  # в миллисекундах
            ping_times.append(ping_time)
            success_count += 1

            # Форматируем вывод как в ping
            print(f"64 bytes from {hostname} ({ip_address}): icmp_seq={i + 1} ttl=54 time={ping_time:.1f} ms")

        except requests.exceptions.RequestException as e:
            print(f"From {ip_address} icmp_seq={i + 1} Destination Host Unreachable")
            ping_times.append(None)

        # Пауза между проверками (как в реальном ping)
        if i < count - 1:
            time.sleep(1)

    # Статистика в формате ping
    print(f"\n--- {hostname} ping statistics ---")
    packet_loss = ((count - success_count) / count) * 100
    print(
        f"{count} packets transmitted, {success_count} received, {packet_loss:.0f}% packet loss, time {count * 1000}ms")

    # Вычисляем статистику RTT
    successful_pings = [t for t in ping_times if t is not None]
    if successful_pings:
        min_time = min(successful_pings)
        avg_time = statistics.mean(successful_pings)
        max_time = max(successful_pings)

        # Вычисляем mdev (mean deviation) - среднее отклонение
        deviations = [abs(t - avg_time) for t in successful_pings]
        mdev = statistics.mean(deviations) if deviations else 0

        print(f"rtt min/avg/max/mdev = {min_time:.3f}/{avg_time:.3f}/{max_time:.3f}/{mdev:.3f} ms")


# Основная программа
if __name__ == "__main__":
    website = input("Введите URL сайта для проверки: ").strip()

    if website:
        advanced_ping_check(website, 5)  # Фиксированное количество проверок = 5
    else:
        print("Вы не ввели URL сайта")