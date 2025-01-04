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

        # curriculum
        chapters_with_lessons.append({
           'chapter-title' : chapter_title,
           'lessons' : lessons
        })

    return ({
        'title' : title,
        'description' : description, 
        'curriculum' : chapters_with_lessons
    })

def scrape_courses():
    url = 'https://courses.analyticsvidhya.com/collections/courses'

    course_urls = get_course_links(url)

    course_data = []
    for course_url in course_urls:
        course_data.append(get_course_details(course_url))

    df = pd.DataFrame(course_data)
    df.to_csv('analytics_vidhya_courses.csv', index=False)
    print("Scraping completed. Data saved to 'analytics_vidhya_courses.csv'")

if __name__ == "__main__":
    scrape_courses()
