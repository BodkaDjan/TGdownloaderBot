import requests
from bs4 import BeautifulSoup


def get_power_outage_info():
    try:
        response = requests.get('https://www.dtek-krem.com.ua/ua/shutdowns')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Предположим, что отключения записаны в теги <div class="outage">
            outages = soup.find_all('div', class_='outage')

            messages = []
            for outage in outages:
                location = outage.find('span', class_='location').text
                time = outage.find('span', class_='time').text
                messages.append(f"📍 {location}: ⏳ {time}")

            return "\n".join(messages) if messages else "Нет информации об отключениях света."
        else:
            return "Не удалось получить данные об отключениях света."
    except Exception as e:
        return f"Ошибка при получении данных: {e}"