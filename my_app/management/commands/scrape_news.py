import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from django.core.management.base import BaseCommand
from urllib.parse import urljoin
from my_app.models import ScrapedArticle

class Command(BaseCommand):
    help = 'Scrapes news headlines and links from Prothom Alo latest news page and stores them in the database.'

    def handle(self, *args, **options):
        target_url = 'https://www.prothomalo.com/collection/latest'
        base_url = 'https://www.prothomalo.com'
        source_name = 'Prothom Alo'

        self.stdout.write(self.style.SUCCESS(f'Starting to scrape news from {target_url}'))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(target_url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error fetching URL {target_url}: {e}'))
            return

        soup = BeautifulSoup(response.content, 'lxml')
        articles_data = []

        possible_article_containers = []
        possible_article_containers.extend(soup.find_all('div', class_='card-with-image-zoom'))
        possible_article_containers.extend(soup.find_all('a', class_='news_with_item'))
        possible_article_containers.extend(soup.find_all('div', class_='news_item--type-general')) 
        possible_article_containers.extend(soup.find_all('div', class_='bn-story-card')) 

        unique_containers = list(dict.fromkeys(possible_article_containers))
        # print(unique_containers)
        if not unique_containers:
            self.stdout.write(self.style.WARNING('No potential article containers found. The website structure might have changed significantly.'))
            return

        for container in unique_containers:
            print(container)
            print("____________________________________________________________")
            title_text = None
            article_url = None
            if container.name == 'a' and container.has_attr('href'):
                link_tag = container
            else:
                link_tag = container.find('a', class_='title-link', href=True)
                if not link_tag:
                    link_tag = container.find('a', href=True)

            if link_tag and link_tag['href']:
                raw_url = link_tag['href']
                if not raw_url.startswith('http'):
                    article_url = urljoin(base_url, raw_url)
                else:
                    article_url = raw_url
            else:
                continue 

            title_span_parent = container.find('span', class_='tilte-no-link-parent')
            if title_span_parent:
                title_parts = []
                for child in title_span_parent.children:
                    if isinstance(child, NavigableString):
                        cleaned_text = child.strip()
                        if cleaned_text:
                            title_parts.append(cleaned_text)
                    elif isinstance(child, Tag) and child.name == 'span':
                        cleaned_text = child.get_text(strip=True)
                        if cleaned_text:
                            title_parts.append(cleaned_text)
                title_text = " ".join(title_parts).strip()

            if not title_text:
                h_tag = container.find(['h2', 'h3', 'h1'], class_=['headline-title', 'title', 'name']) 
                if not h_tag: 
                     h_tag = container.find(['h2', 'h3', 'h1'])
                if h_tag:
                    title_text = h_tag.get_text(strip=True)

            if not title_text and link_tag:
                if link_tag.has_attr('aria-label') and link_tag['aria-label']:
                    title_text = link_tag['aria-label'].strip()
                elif link_tag.has_attr('title') and link_tag['title']:
                    title_text = link_tag['title'].strip()

            if not title_text and link_tag:
                title_text = link_tag.get_text(strip=True).replace("\n", " ").strip()


            if title_text and article_url and len(title_text) > 5 : 
                is_duplicate = False
                for existing_item in articles_data:
                    if existing_item['url'] == article_url:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    articles_data.append({'title': title_text.strip(), 'url': article_url})

        if not articles_data:
            self.stdout.write(self.style.WARNING('No valid articles with titles and links were extracted. Please check selectors and website structure.'))
            return

        self.stdout.write(self.style.SUCCESS(f"Successfully extracted {len(articles_data)} unique articles with titles and links."))

        saved_count = 0
        skipped_count = 0
        for item in articles_data:
            try:
                article_obj, created = ScrapedArticle.objects.get_or_create(
                    url=item['url'],
                    defaults={
                        'title': item['title'],
                        'source': source_name
                    }
                )
                if created:
                    saved_count += 1
                    self.stdout.write(self.style.SUCCESS(f"SAVED: {item['title']} ({item['url']})"))
                else:
                    skipped_count +=1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error saving/updating article '{item['title']}': {e}"))

        self.stdout.write(self.style.SUCCESS(f'Finished processing. Saved {saved_count} new articles. Skipped {skipped_count} existing articles.'))