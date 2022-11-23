import json
import os.path

import requests

from bs4 import BeautifulSoup


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}


def get_data(url):
    """  """
    all_data = {}

    if not os.path.exists(f"data"):
        os.mkdir(f"data")

    with requests.Session() as session:

        response = session.get(url=url, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')

        catalog = soup.find("div", class_="content-wrapper").find_all("a", class_="item")

        for subcategory in catalog:
            url_to_subcategory = f"https://www.grand.ua-shop.in{subcategory.get('href')}"

            name_category = url_to_subcategory.split("/")[-2]

            if not os.path.exists(f"data/{name_category}"):
                os.mkdir(f"data/{name_category}")

            response = session.get(url=url_to_subcategory, headers=headers)

            soup = BeautifulSoup(response.text, 'lxml')
            cards = soup.select("a.img")

            all_cards = []
            count = 0
            for card in cards:

                try:
                    url_to_card = f"https://www.grand.ua-shop.in{card.get('href')}"

                    name_card = url_to_card.split("/")[-2]

                    if not os.path.exists(f"data/{name_category}/{name_card}"):
                        os.mkdir(f"data/{name_category}/{name_card}")

                    response = session.get(url=url_to_card, headers=headers)

                    soup = BeautifulSoup(response.text, 'lxml')

                    container = soup.find("div", id="navigation").parent

                    try:
                        product_name = container.find("h1", id="pagetitle").text.strip()
                        if " у фірмовому магазині" in product_name:
                            product_name = product_name.replace(" у фірмовому магазині", "")
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
                        trs = container.\
                            find("div", class_="tabs-container").\
                            find("div", class_="characteristics").\
                            find("tbody").find_all("tr")

                        characteristics = {}
                        for tr in trs:
                            key = tr.find("td", class_="type").find("span").text.strip()
                            value = tr.find("td", class_="value").text.strip()
                            characteristics[key] = value

                    except Exception:
                        characteristics = None

                    try:
                        videos = container. \
                            find("div", class_="tabs-container"). \
                            find("div", class_="videos"). \
                            find_all("div", class_="item lazy-video")
                        product_videos = [product_video.get("data-video").split(" ")[3].
                                          split("=")[-1].strip("\"") for product_video in videos]
                    except Exception:
                        product_videos = None

                    prom_description = f"{product_name}\n{product_description}\n{product_characteristics}"

                    with open(f"data/{name_category}/{name_card}/{name_card}.txt", "w", encoding="utf-8") as file:
                        file.write(prom_description)

                    all_cards.append(
                        {
                            "product_name": product_name,
                            "url_to_card": url_to_card,
                            "product_price": product_price,
                            "url_to_card_images": url_to_card_images,
                            "url_to_card_videos": product_videos,
                            "characteristics": characteristics
                        }
                    )

                    count += 1
                    print(f"#{count}/{len(cards)} in {name_category}")
                except Exception as ex:
                    print("Something wrong ...")
                    print(ex)
                    continue
            all_data[name_category] = all_cards

    with open("all_data.json", "w", encoding="utf-8") as file:
        json.dump(all_data, file, indent=4, ensure_ascii=False)


def download_img():
    """  """
    with open("all_data.json", "r", encoding="utf-8") as file:
        res = json.load(file)

    with requests.Session() as session:

        for k, v in res.items():

            if not os.path.exists(f"data/{k}"):
                os.mkdir(f"data/{k}")

            for card in v:
                url_to_card_images = card['url_to_card_images']
                title_name = card['url_to_card'].split("/")[-2]

                if not os.path.exists(f"data/{k}/{title_name}"):
                    os.mkdir(f"data/{k}/{title_name}")

                for index, url_to_card_image in enumerate(url_to_card_images):

                    response = session.get(url=url_to_card_image, headers=headers)
                    with open(f"data/{k}/{title_name}/{index}.png", "wb") as file:
                        file.write(response.content)

                    print(f"{index + 1}/{len(url_to_card_images)} in {title_name}")


def main():

    # get_data(url="https://www.grand.ua-shop.in/catalog/")
    download_img()


if __name__ == '__main__':
    main()