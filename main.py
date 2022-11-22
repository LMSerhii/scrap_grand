import requests

from bs4 import BeautifulSoup


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}


def get_data(url):
    """  """
    with requests.Session() as session:

        response = session.get(url=url, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')

        catalog = soup.find("div", class_="content-wrapper").find_all("a", class_="item")

        for subcategory in catalog[:2]:
            url_to_subcategory = f"https://www.grand.ua-shop.in{subcategory.get('href')}"
            response = session.get(url=url_to_subcategory, headers=headers)

            soup = BeautifulSoup(response.text, 'lxml')
            cards = soup.select("a.img")
            for card in cards:

                try:
                    url_to_card = f"https://www.grand.ua-shop.in{card.get('href')}"

                    response = session.get(url=url_to_card, headers=headers)

                    soup = BeautifulSoup(response.text, 'lxml')

                    container = soup.find("div", id="navigation").parent

                    try:
                        product_name = container.find("h1", id="pagetitle").text.strip()
                    except Exception:
                        product_name = None

                    try:
                        product_price = container.select_one("div.price span").text.strip().replace("\xa0", '')
                    except Exception:
                        product_price = None

                    try:
                        product_description = container.find("div", class_="text")
                    except Exception:
                        product_description = None

                    try:
                        url_to_card_images = [f"https://www.grand.ua-shop.in{url.find('img').get('src')}" for url in
                                          container.find("div", class_="main-img").find_all("div")]
                    except Exception:
                        url_to_card_images = None

                    try:
                        product_characteristics = container.find("div", class_="tabs-container").find("div",
                                                                                                  class_="characteristics")
                    except Exception:
                        product_characteristics = None

                    try:
                        videos = container. \
                            find("div", class_="tabs-container"). \
                            find("div", class_="videos"). \
                            find_all("div", class_="item lazy-video")
                        product_videos = [product_video.get("data-video").split(" ")[3].
                                          split("=")[-1].strip("\"") for product_video in videos]
                    except Exception:
                        product_videos = None

                    print(f"{product_name}\n"
                          f"{product_price}\n"
                          f"{product_description}\n"
                          f"{url_to_card_images}\n"
                          f"{product_characteristics}\n"
                          f"{product_videos}\n\n\n")

                except Exception:
                    continue


def main():

    get_data(url="https://www.grand.ua-shop.in/catalog/")


if __name__ == '__main__':
    main()