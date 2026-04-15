import os
import requests
import time
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style, init

init(autoreset=True)

def anim_text(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loader(duration=1):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for i in range(duration * 10):
        sys.stdout.write(f"\r{Fore.MAGENTA}  {chars[i % len(chars)]}  {Fore.WHITE}Обработка пакетов...")
        sys.stdout.flush()
        time.sleep(0.1)
    print("\r" + " " * 30 + "\r", end="")

def get_url_info(user_input):
    """Определяет домен, протокол и режим работы"""
    raw = user_input.strip().lower()
    if not raw.startswith(('http://', 'https://')):
        raw = 'https://' + raw
    
    parsed = urlparse(raw)
    try:
        puny_netloc = parsed.netloc.encode('idna').decode('ascii')
        target_url = raw.replace(parsed.netloc, puny_netloc)
    except:
        target_url = raw
        
    return target_url, parsed.netloc, parsed.path

def download_assets(soup, base_url, folder):
    os.makedirs(folder, exist_ok=True)
    tags = {'script': 'src', 'link': 'href', 'img': 'src'}
    count = 0
    
    for tag, attr in tags.items():
        for el in soup.find_all(tag, **{attr: True}):
            asset_url = urljoin(base_url, el[attr])
            ext = os.path.splitext(urlparse(asset_url).path)[1].lower()
            
            if ext in ['.js', '.css', '.py', '.png', '.jpg', '.svg', '.html']:
                try:
                    name = os.path.basename(urlparse(asset_url).path) or "index.html"
                    content = requests.get(asset_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}).content
                    with open(os.path.join(folder, name), "wb") as f:
                        f.write(content)
                    print(f"    {Fore.CYAN}⤑ {Fore.WHITE}Захвачен: {Fore.BLUE}{name}")
                    count += 1
                except: continue
    return count

def run():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*60}")
    anim_text(f"{Fore.CYAN}{Style.BRIGHT}          ULTIMATE SITE CLONER v4.0 PRO")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*60}\n")

    user_input = input(f"{Fore.YELLOW} Введите домен или полную ссылку: {Style.RESET_ALL}").strip()
    target_url, domain, path = get_url_info(user_input)
    
    cite_path = os.path.join(os.getcwd(), "Cite")
    main_path = os.path.join(cite_path, "main")

    # Режим работы
    is_subpage = path.strip('/') != ""
    mode_text = "РЕЖИМ: СТРАНИЦА" if is_subpage else "РЕЖИМ: ВЕСЬ ДОМЕН"
    print(f"\n{Fore.GREEN}[*] {Fore.WHITE}{mode_text} | {Fore.YELLOW}{domain}")
    
    loader(2)

    try:
        # 1. Работаем с целевой страницей
        print(f"\n{Fore.MAGENTA}[1] {Fore.WHITE}Анализ точки входа: {Fore.CYAN}{target_url}")
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        entry_folder = os.path.join(cite_path, "target_page" if is_subpage else "main")
        os.makedirs(entry_folder, exist_ok=True)
        
        with open(os.path.join(entry_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(res.text)
        
        num = download_assets(soup, target_url, entry_folder)
        print(f"  {Fore.GREEN}✔ {Fore.WHITE}Готово. Файлов: {num}")

        # 2. Поиск маршрутов (только если введена главная или если нужно найти ссылки на странице)
        print(f"\n{Fore.MAGENTA}[2] {Fore.WHITE}Поиск внутренних маршрутов в <a>...")
        found_links = set()
        for a in soup.find_all('a', href=True):
            full_link = urljoin(target_url, a['href']).split('#')[0].rstrip('/')
            if domain in urlparse(full_link).netloc and full_link != target_url:
                found_links.add(full_link)

        if not found_links:
            print(f"  {Fore.RED}✘ {Fore.WHITE}Дополнительные маршруты не найдены.")
        else:
            print(f"  {Fore.GREEN}✔ {Fore.WHITE}Найдено путей: {len(found_links)}")
            
            for link in found_links:
                route_name = urlparse(link).path.strip('/').replace('/', '_') or "sub"
                route_dir = os.path.join(cite_path, route_name)
                print(f"\n{Fore.YELLOW}---> {Fore.WHITE}Переход: {Fore.CYAN}{link}")
                
                try:
                    r = requests.get(link, timeout=7)
                    s = BeautifulSoup(r.text, 'html.parser')
                    os.makedirs(route_dir, exist_ok=True)
                    with open(os.path.join(route_dir, "index.html"), "w", encoding="utf-8") as f:
                        f.write(r.text)
                    download_assets(s, link, route_dir)
                except:
                    print(f"     {Fore.RED}Ошибка доступа.")

        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.GREEN}{Style.BRIGHT} ОПЕРАЦИЯ ЗАВЕРШЕНА. ВСЕ ДАННЫЕ В /Cite/")
        print(f"{Fore.MAGENTA}{'='*60}")

    except Exception as e:
        print(f"\n{Fore.RED}[КРИТИЧЕСКАЯ ОШИБКА]: {e}")

if __name__ == "__main__":
    if "copy.py" in sys.argv[0]:
        print(Fore.RED + "ПЕРЕИМЕНУЙ ФАЙЛ!")
    else:
        run()
