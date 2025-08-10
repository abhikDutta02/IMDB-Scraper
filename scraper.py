import requests
import os
import json

from bs4 import BeautifulSoup
from time import sleep

def scrape_imdb_top_movies(year):
    url = f"https://www.imdb.com/search/title/?release_date={year}-01-01,{year}-12-31&title_type=feature"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all movie containers
    movie_blocks = soup.find_all('div', class_='ipc-metadata-list-summary-item__c')

    dataset_top50 = {}

    for idx, block in enumerate(movie_blocks[:50], start=1):
        try:
            # Movie Title
            title_tag = block.find('h3', class_='ipc-title__text ipc-title__text--reduced')
            raw_title = title_tag.get_text(strip=True)
            title = raw_title.split('. ', 1)[-1] if '. ' in raw_title else raw_title

            # Release year and runtime
            metadata_spans = block.find_all('span', class_='sc-15ac7568-7 cCsint dli-title-metadata-item')
            release_year = metadata_spans[0].get_text(strip=True) if len(metadata_spans) > 0 else ''
            runtime = metadata_spans[1].get_text(strip=True) if len(metadata_spans) > 1 else ''

            # Rating
            rating_tag = block.find('span', class_='ipc-rating-star--rating')
            rating = rating_tag.get_text(strip=True) if rating_tag else ''

            # Description
            desc_tag = block.find('div', class_='ipc-html-content-inner-div')
            description = desc_tag.get_text(strip=True) if desc_tag else ''

            dataset_top50[idx] = {
                'title': title,
                'release_year': release_year,
                'runtime': runtime,
                'rating': rating,
                'description': description
            }

        except Exception as e:
            print(f"[Warning] Skipping entry {idx} due to error: {e}")
            continue

    return dataset_top50

# Main scraping loop
if __name__ == '__main__':
    os.makedirs('DataSets', exist_ok=True)

    for year in range(2000,2005):
        print(f"Scraping IMDb data for year: {year}")
        movies = scrape_imdb_top_movies(year)
        print(f"Saved {len(movies)} movies for {year} to DataSets/IMDB_Top_50_{year}.json")

        with open(f'DataSets/IMDB_Top_50_{year}.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)

        sleep(1)  # Be polite and avoid being blocked
