import requests
import time
import statistics
from urllib.parse import urlparse


def http_ping_check(url, count=5):
    """
    Выполняет многократную проверку доступности сайта по HTTP/HTTPS
    с выводом статистики в формате, похожем на ping
    """
    # Добавляем схему если отсутствует
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme
    port = parsed_url.port or (443 if scheme == 'https' else 80)

    print(f"HTTP PING {hostname} ({scheme.upper()}:{port})")

    success_count = 0
    response_times = []
    status_codes = []

    for i in range(count):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=True)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # в миллисекундах
            response_times.append(response_time)
            status_codes.append(response.status_code)
            success_count += 1

            # Форматируем вывод
            print(
                f"HTTP seq={i + 1} status={response.status_code} time={response_time:.1f} ms size={len(response.content)} bytes")

        except requests.exceptions.RequestException as e:
            print(f"HTTP seq={i + 1} failed: {str(e)}")
            response_times.append(None)
            status_codes.append(None)

        # Пауза между проверками
        if i < count - 1:
            time.sleep(1)

    # Статистика
    print(f"\n--- {hostname} HTTP ping statistics ---")
    packet_loss = ((count - success_count) / count) * 100
    print(f"{count} requests made, {success_count} successful, {packet_loss:.0f}% failed")

    # Статистика по кодам ответа
    successful_codes = [code for code in status_codes if code is not None]
    if successful_codes:
        code_counts = {}
        for code in successful_codes:
            code_counts[code] = code_counts.get(code, 0) + 1

        print("Status code distribution:")
        for code, count_val in code_counts.items():
            print(f"  {code}: {count_val} times")

    # Статистика по времени ответа
    successful_times = [t for t in response_times if t is not None]
    if successful_times:
        min_time = min(successful_times)
        avg_time = statistics.mean(successful_times)
        max_time = max(successful_times)

        # Вычисляем mdev (mean deviation)
        deviations = [abs(t - avg_time) for t in successful_times]
        mdev = statistics.mean(deviations) if deviations else 0

        print(f"response min/avg/max/mdev = {min_time:.3f}/{avg_time:.3f}/{max_time:.3f}/{mdev:.3f} ms")


# Основная программа
if __name__ == "__main__":
    website = input("Введите URL сайта для HTTP проверки: ").strip()

    if website:
        http_ping_check(website, 5)
    else:
        print("Вы не ввели URL сайта")