import requests
from bs4 import BeautifulSoup

url = "https://hianime.to/recently-updated"


def check_for_new_episode(tracked_show) :
    if not tracked_show :
        return None

    response = requests.get(url)
    if response.status_code != 200 :
        print("Failed to retrieve the page")
        return None

    soup = BeautifulSoup(response.text , 'html.parser')
    shows_wrap = soup.find('div' , class_='film_list-wrap')

    for item in shows_wrap.find_all('div' , class_='flw-item') :
        current_show_name = item.select_one('.film-detail .film-name a').get_text(strip=True)

        if tracked_show.lower() in current_show_name.lower() :
            show_url = item.select_one('.film-detail .film-name a')['href']
            full_url = f"https://hianime.to{show_url}"
            return full_url

    return None


