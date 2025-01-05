import requests
from bs4 import BeautifulSoup
import pandas as pd

# To get a list of course links using bs4
def get_course_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    course_links = soup.select('li.products__list-item a.course-card')

    return ['https://courses.analyticsvidhya.com' + link['href'] for link in course_links if 'href' in link.attrs]

# To get course-details(title, desc, curriculum)
def get_course_details(course_url):
    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # price_tags = soup.select('li.products__list-item')
    # print(price_tags)

    title_tag = soup.select_one('h1.section__heading')
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    description_tag = soup.select('.rich-text__wrapper span, .rich-text__wrapper p')
    description = "".join([description.get_text(strip=True) for description in description_tag])

    curriculum_chapter_list = soup.select('li.course-curriculum__chapter')

    chapters_with_lessons = []

    for chapter in curriculum_chapter_list:
        chapter_title_tag = chapter.select_one('h5.course-curriculum__chapter-title')
        chapter_title = chapter_title_tag.get_text(strip=True)

        lesson_tag = chapter.select('span.course-curriculum__chapter-lesson') 
        lessons = [lesson.get_text(strip=True) for lesson in lesson_tag]

        chapters_with_lessons.append(f"{chapter_title}: {', '.join(lessons)}")

        # print(title)
    return ({
        'title' : title,
        'description' : description, 
        'curriculum' : ';'.join(chapters_with_lessons)
    })


def get_total_pages(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the last page number in the pagination links
    pagination_links = soup.select('a.pagination__page-number')
    # if pagination_links:
        # last_page = max(int(link.get_text(strip=True)) for link in pagination_links)
    return 9

# Main function to scrape all courses
def scrape_courses():
    base_url = 'https://courses.analyticsvidhya.com/collections/courses'

    # Get the total number of pages
    total_pages = get_total_pages(base_url)
    print(f"Total pages found: {total_pages}")

    course_urls = []

    # Iterate through all pages and collect course links
    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}...")
        page_url = f"{base_url}?page={page}"
        course_urls.extend(get_course_links(page_url))

    # Remove duplicate links (if any)
    course_urls = list(set(course_urls))

    # Extract details for each course
    course_data = []
    for course_url in course_urls:
        print(f"Scraping course: {course_url}")
        course_data.append(get_course_details(course_url))

    # Save to CSV
    df = pd.DataFrame(course_data)
    df.to_csv('analytics_vidhya_courses.csv', index=False)
    print("Scraping completed. Data saved to 'analytics_vidhya_courses.csv'")

if __name__ == "__main__":
    scrape_courses()
