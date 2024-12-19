import requests
from bs4 import BeautifulSoup

url = "https://hianime.to/recently-updated"


def check_for_new_episode(tracked_show):
    """
    Check for a new episode of the tracked show on hianime.to.

    Args:
        tracked_show (str): The name of the show to track.

    Returns:
        str | None: The URL of the new episode if found, otherwise None.
    """
    if not tracked_show:
        print("No show provided to track.")
        return None

    print("Looking for a new episode...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    shows_wrap = soup.find('div', class_='film_list-wrap')

    if not shows_wrap:
        print("Could not find the shows section on the page.")
        return None

    for item in shows_wrap.find_all('div', class_='flw-item'):
        try:
            current_show_name = item.select_one('.film-detail .film-name a').get_text(strip=True)
            if tracked_show.lower() in current_show_name.lower():
                show_url = item.select_one('.film-detail .film-name a')['href']
                full_url = show_url if show_url.startswith("http") else f"https://hianime.to{show_url}"
                print(f"New episode found for '{tracked_show}': {full_url}")
                return full_url
        except AttributeError:
            # Skip this item if expected elements are not found
            continue

    print("No new episode found for the tracked show.")

