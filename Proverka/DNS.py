import dns.resolver
import sys
from urllib.parse import urlparse
from typing import List, Dict, Optional

def normalize_domain(domain):
    """Извлекает домен из URL если необходимо"""
    if domain.startswith(('http://', 'https://')):
        parsed = urlparse(domain)
        return parsed.hostname or domain
    return domain
    google.com
def get_dns_servers():
    """Возвращает список DNS серверов для использования"""
    return [
        '8.8.8.8',  # Google DNS
        '1.1.1.1',  # Cloudflare DNS
        '208.67.222.222',  # OpenDNS
    ]

def dns_lookup(domain, record_type='A', dns_server=None):
    """
    Выполняет DNS запрос указанного типа
    """
    domain = normalize_domain(domain)
    
    try:
       
        resolver = dns.resolver.Resolver()
        
        
        if dns_server:
            resolver.nameservers = [dns_server]
        
        
        answers = resolver.resolve(domain, record_type)
        
        results = []
        for rdata in answers:
            results.append(str(rdata))
        
        return {
            'success': True,
            'domain': domain,
            'type': record_type,
            'results': results,
            'dns_server': dns_server or 'system'
        }
        
    except dns.resolver.NoAnswer:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': f'No {record_type} record found',
            'dns_server': dns_server or 'system'
        }
    except dns.resolver.NXDOMAIN:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': 'Domain does not exist',
            'dns_server': dns_server or 'system'
        }
    except dns.resolver.Timeout:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': 'DNS query timed out',
            'dns_server': dns_server or 'system'
        }
    except Exception as e:
        return {
            'success': False,
            'domain': domain,
            'type': record_type,
            'error': f'Error: {str(e)}',
            'dns_server': dns_server or 'system'
        }

def check_all_records(domain, dns_server=None):
    """
    Проверяет все основные типы DNS записей для домена
    """
    domain = normalize_domain(domain)
    
    print(f"\nDNS LOOKUP {domain}")
    if dns_server:
        print(f"DNS Server: {dns_server}")
    print("─" * 60)
    
    record_types = [
        ('A', 'IPv4 addresses'),
        ('AAAA', 'IPv6 addresses'),
        ('MX', 'Mail servers'),
        ('NS', 'Name servers'),
        ('TXT', 'Text records'),
        ('CNAME', 'Canonical name'),
        ('SOA', 'Start of authority')
    ]
    
    all_results = {}
    
    for record_type, description in record_types:
        print(f"\n{record_type:6} ({description}):")
        print("  " + "─" * 50)
        
        result = dns_lookup(domain, record_type, dns_server)
        all_results[record_type] = result
        
        if result['success']:
            for i, record in enumerate(result['results'], 1):
                if record_type == 'MX':
                    
                    parts = record.split()
                    if len(parts) >= 2:
                        priority = parts[0]
                        server = ' '.join(parts[1:])
                        print(f"  {i:2d}. Priority: {priority}, Server: {server}")
                    else:
                        print(f"  {i:2d}. {record}")
                else:
                    print(f"{i:2d}. {record}")
        else:
            print(f"{result['error']}")
    
    return all_results

def check_with_multiple_dns(domain):
    """
    Проверяет DNS записи используя несколько DNS серверов
    """
    domain = normalize_domain(domain)
    dns_servers = get_dns_servers()
    
    print(f"\nDNS LOOKUP {domain} - Multiple DNS Servers")
    print("─" * 60)
    
    for dns_server in dns_servers:
        print(f"\n📡 Using DNS: {dns_server}")
        result = dns_lookup(domain, 'A', dns_server)
        
        if result['success']:
            print(f" A records: {', '.join(result['results'])}")
        else:
            print(f"{result['error']}")

def detailed_mx_check(domain):
    """
    Детальная проверка MX записей с проверкой A записей для mail серверов
    """
    domain = normalize_domain(domain)
    
    print(f"\nDETAILED MX CHECK {domain}")
    print("─" * 60)
    
    mx_result = dns_lookup(domain, 'MX')
    
    if not mx_result['success']:
        print(f"{mx_result['error']}")
        return
    
    print("MX Records found:")
    for i, mx_record in enumerate(mx_result['results'], 1):
        parts = mx_record.split()
        if len(parts) >= 2:
            priority = parts[0]
            mail_server = ' '.join(parts[1:])
            
            print(f"\n{i}. Mail Server: {mail_server}")
            print(f"   Priority: {priority}")
            
            
            a_result = dns_lookup(mail_server, 'A')
            if a_result['success']:
                print(f"   IPv4: {', '.join(a_result['results'])}")
            else:
                print(f"   IPv4: Not found")
            
            
            aaaa_result = dns_lookup(mail_server, 'AAAA')
            if aaaa_result['success']:
                print(f"   IPv6: {', '.join(aaaa_result['results'])}")

def dns_benchmark(domain):
    """
    Тестирование скорости ответа разных DNS серверов
    """
    import time
    
    domain = normalize_domain(domain)
    dns_servers = get_dns_servers()
    
    print(f"\nDNS BENCHMARK {domain}")
    print("─" * 60)
    
    results = []
    
    for dns_server in dns_servers:
        start_time = time.time()
        result = dns_lookup(domain, 'A', dns_server)
        response_time = (time.time() - start_time) * 1000  # в миллисекундах
        
        status = 'Выполнено' if result['success'] else 'Отказ'
        results.append({
            'server': dns_server,
            'time': response_time,
            'success': result['success'],
            'records': result['results'] if result['success'] else []
        })
        
        if result['success']:
            print(f"{status} {dns_server:15} - {response_time:6.1f} ms - {', '.join(result['results'])}")
        else:
            print(f"{status} {dns_server:15} - {response_time:6.1f} ms - {result['error']}")
    
    
    successful_results = [r for r in results if r['success']]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x['time'])
        print(f"\n🏆 Fastest DNS: {fastest['server']} ({fastest['time']:.1f} ms)")

def main():
    """Основная функция программы"""
    print("DNS LOOKUP CHECK")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("Введите домен для проверки DNS: ").strip()
        if not domain:
            print("Не указан домен")
            return
    
    domain = normalize_domain(domain)
    
    print("\nВыберите тип проверки:")
    print("1 - Полная проверка всех записей")
    print("2 - Проверка с разными DNS серверами")
    print("3 - Детальная проверка MX записей")
    print("4 - Бенчмарк DNS серверов")
    print("5 - Проверка конкретного типа записи")
    
    choice = input("Ваш выбор [1]: ").strip() or "1"
    
    if choice == "1":
        check_all_records(domain)
    elif choice == "2":
        check_with_multiple_dns(domain)
    elif choice == "3":
        detailed_mx_check(domain)
    elif choice == "4":
        dns_benchmark(domain)
    elif choice == "5":
        record_type = input("Введите тип записи (A, AAAA, MX, NS, TXT, CNAME): ").strip().upper()
        if record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']:
            result = dns_lookup(domain, record_type)
            print(f"\n{record_type} records for {domain}:")
            if result['success']:
                for i, record in enumerate(result['results'], 1):
                    print(f" {i}. {record}")
            else:
                print(f" {result['error']}")
        else:
            print("Неверный тип DNS записи")
    else:
        print("Неверный выбор")


def quick_dns_check(domain):
    """Быстрая проверка основных DNS записей"""
    return check_all_records(domain)

def get_domain_ips(domain):
    """Возвращает все IP адреса домена"""
    domain = normalize_domain(domain)
    results = {}
    
    a_result = dns_lookup(domain, 'A')
    if a_result['success']:
        results['ipv4'] = a_result['results']
    
    aaaa_result = dns_lookup(domain, 'AAAA')
    if aaaa_result['success']:
        results['ipv6'] = aaaa_result['results']
    
    return results

def check_dns_health(domain):
    """Проверяет здоровье DNS конфигурации домена"""
    domain = normalize_domain(domain)
    
    print(f"\nDNS HEALTH CHECK {domain}")
    print("─" * 60)
    
    checks = [
        ('A', 'IPv4 addresses', True),
        ('NS', 'Name servers', True),
        ('MX', 'Mail servers', False),  
        ('SOA', 'Start of authority', True)
    ]
    
    health_status = True
    
    for record_type, description, required in checks:
        result = dns_lookup(domain, record_type)
        
        if result['success']:
            print(f" {record_type}: {len(result['results'])} records found")
        else:
            if required:
                print(f" {record_type}: {result['error']}")
                health_status = False
            else:
                print(f"  {record_type}: {result['error']} (optional)")
    
    if health_status:
        print(f"\n DNS configuration looks healthy")
    else:
        print(f"\n  DNS configuration has issues")

if __name__ == "__main__":
    try:
        import dns.resolver
    except ImportError:
        print("Ошибка: Библиотека dnspython не установлена")
        print("Установите её: pip install dnspython")
        sys.exit(1)
    
    main()