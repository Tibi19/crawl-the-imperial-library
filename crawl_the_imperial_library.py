from bs4 import BeautifulSoup
import requests
import json
import re
import crawl_book_element

#### FUNCTIONS ####

def replace_line_breaks(text):
    return re.sub("<br.*?>", crawl_book_element.NEW_LINE_SYMBOL, text)

def parse_author(item):
    author = ""
    author_tag = item.find(class_="views-field views-field-field-author-value")
    if author_tag is not None:
        author = author_tag.span.string
    return author.strip()

def parse_description(item):
    description = ""
    description_tag = item.find(class_="views-field views-field-field-summary-value")
    if description_tag is not None:
        description = description_tag.span.string
    return description.strip()

def get_item_link(item_link_extension):
    root = "https://www.imperial-library.info"
    item_link_extension = item_link_extension.strip()
    return root + item_link_extension

def get_item_html(item_link_extension, error_log_output, is_status_success):
    item_link = get_item_link(item_link_extension)
    item_html = ""
    try:
        item_url_response = requests.get(item_link)
        item_html = item_url_response.text
    except Exception as error:
        error_log_output.append({
            "title" : title,
            "task" : "url request",
            "error" : str(error)
        })
        is_status_success = False
    return item_html, is_status_success

def get_item_beautiful_soup(item_html, is_status_success):
    if not item_html or not is_status_success:
        return None, False

    item_html = replace_line_breaks(item_html)
    return BeautifulSoup(item_html, "html.parser"), True

def get_book_text(id, item_soup, error_log_output, is_status_success):
    book_text = {
        "id" : id,
        "paragraphs" : [] 
    }

    if not is_status_success:
        return book_text, False

    try:
        book_text = crawl_book_element.get_book_text(id, item_soup)
    except Exception as error:
        error_log_output.append({
            "title" : title,
            "task" : "content parsing",
            "error" : str(error)
        })
        is_status_success = False

    return book_text, is_status_success

def get_tags_and_category(item_soup, error_log_output, is_status_success):
    tags = []
    category = ""

    if not is_status_success:
        return tags, category, False

    try:
        tags = crawl_book_element.get_tags(item_soup)
        category = crawl_book_element.get_category(item_soup)
    except Exception as error:
        error_log_output.append({
            "title" : title,
            "task" : "tags parsing",
            "error" : str(error)
        })
        is_status_success = False

    return tags, category, is_status_success

def write_book_text(book_text):
    with open(f"book_texts/{file_name}", "w") as text_file:
        json.dump(book_text, text_file, sort_keys = False, indent = 4)

def write_metadata(books_metadata):
    with open("books_metadata.json", "w") as metadata_file:
        json.dump(books_metadata, metadata_file, sort_keys = False, indent = 4)

def write_categories(categories):
    with open("books_categories.json", "w") as categories_file:
        json.dump(categories, categories_file, sort_keys = False, indent = 4)

def write_errors(error_log):
    with open("error_log.json", "w") as log_file:
        json.dump(error_log, log_file, sort_keys = False, indent = 4)

#### MAIN ####

html = "https://www.imperial-library.info/books/all/by-title"
html_response = requests.get(html)
doc = html_response.text

items = doc.find(class_="item-list").ul.contents
books_metadata = { "books_metadata" : [] }
categories_set = set()
error_log = []
books_count = 0
books_count_succesful = 0

for item in items:

    if item.name != "li":
        continue

    is_item_succesful = True # will be changed to False if any getter function fails

    title = item.find("a").string 

    id = "".join(char for char in title if char.isalnum())

    author = parse_author(item)
    description = parse_description(item)

    item_link_extension = item.find("a")["href"]

    file_name = item_link_extension.split("/")[-1] + ".json"

    item_html, is_item_succesful = get_item_html(item_link_extension, error_log, is_item_succesful)
    item_soup, is_item_succesful = get_item_beautiful_soup(item_html, is_item_succesful)
    book_text, is_item_succesful = get_book_text(id, item_soup, error_log, is_item_succesful)
    tags, category, is_item_succesful = get_tags_and_category(item_soup, error_log, is_item_succesful)

    books_metadata['books_metadata'].append({
        "id" : id,
        "title" : title,
        "author" : author,
        "description" : description,
        "tags" : tags,
        "category" : category,
        "fileName": file_name
    })

    if category:
        categories_set.add(category)

    write_book_text(book_text)

    books_count += 1
    books_count_succesful += 1 if is_item_succesful else 0
    success_string = "passed" if is_item_succesful else "ERROR"
    print(f"{books_count}. " + title + " by " + author + " - RESULT: " + success_string)
     
print(f"Books parsed: {books_count_succesful} / {books_count}")

write_metadata(books_metadata)
write_categories(list(categories_set))
write_errors(error_log)
