import re

NEW_LINE_SYMBOL = "##new-line##"

##### PRIVATE FUNCTIONS #####

def _is_item_empty(item):
    item_string = item.string
    if(item_string is not None):
        is_only_spaces = re.compile("[ ]+").match(item_string)
        is_empty = item_string == ""
        is_new_line = item_string == "\n"
        return is_only_spaces or is_empty or is_new_line

def _strip_escapes(text):
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    return text.translate(translator)

def _parse_header_paragraph(paragraph):
    return "<header>" + paragraph + "</header>"

def _parse_center_paragraph(paragraph):
    return "<center>" + paragraph + "</center>"

def _parse_title_paragraph(paragraph):
    return "<title>" + paragraph + "</title>"

def _parse_quote_paragraph(paragraph):
    return "<quote>" + paragraph + "</quote>"

def _parse_italic_paragraph(paragraph):
    return "<italic>" + paragraph + "</italic>"

def _parse_bold_paragraph(paragraph):
    return "<bold>" + paragraph + "</bold>"

def _parse_new_line_paragraph(paragraph):
    return paragraph.replace(NEW_LINE_SYMBOL, "\n")

def _parse_image_paragraph(paragraph_item):
    root = "https://www.imperial-library.info"
    link_extension = paragraph_item.find("img")['src']
    link_extension = _strip_escapes(link_extension)
    link_extension = link_extension.strip()
    link = root + link_extension
    return f"<image={link}>"

def _parse_paragraph(paragraph_item):
    paragraph_raw = str(paragraph_item)

    paragraph = paragraph_item.text
    paragraph = _strip_escapes(paragraph)
    paragraph = paragraph.strip()

    if("<img" in paragraph_raw):
        return _parse_image_paragraph(paragraph_item)

    if("<blockquote>" in paragraph_raw):
        paragraph = _parse_quote_paragraph(paragraph)
    if("<em>" in paragraph_raw):
        paragraph = _parse_italic_paragraph(paragraph)
    if("<strong>" in paragraph_raw):
        paragraph = _parse_bold_paragraph(paragraph)
    if("<h4>" in paragraph_raw or "<h3>" in paragraph_raw):
        paragraph = _parse_header_paragraph(paragraph)
    if("<h2>" in paragraph_raw):
        paragraph = _parse_title_paragraph(paragraph)
    if("rtecenter" in paragraph_raw):
        paragraph = _parse_center_paragraph(paragraph)

    if(NEW_LINE_SYMBOL in paragraph_raw):
        paragraph = _parse_new_line_paragraph(paragraph)

    return paragraph

def _process_items(items, book_text):
    for item in items:

        if item.name == "div":
            item_raw = str(item)
            # we already have info about author
            if "field field-type-text field-field-author" in item_raw:
                continue
            # if item has book navigation we are past content
            if "book-navigation" in item_raw: 
                break

            div_contents = item.find_all(recursive = False)
            if len(div_contents) > 0:
                _process_items(div_contents, book_text)
                if "field-field-comment" in item_raw:
                    book_text['paragraphs'].append("")
                continue

        if _is_item_empty(item):
            continue

        paragraph = _parse_paragraph(item)
        book_text['paragraphs'].append(paragraph)

def _process_tags(tag_items):
    tags = []
    for item in tag_items:
        tag = item.text
        tag = tag.strip()
        tags.append(tag)
    return tags

def _process_category(tag_items):
    for item in tag_items:
        if "/categories/" in str(item):
            return item.text.strip()
    return "##missing-category##"

##### EXPORT FUNCTIONS #####

def get_book_text(id, book_html):
    content_nodes = book_html.find_all(class_="node-content clear-block prose")[-1].contents
    book_text = {
        "id" : id,
        "paragraphs" : []
    }
    _process_items(content_nodes, book_text)
    return book_text

def get_tags(book_html):
    tag_nodes = book_html.find("ul", class_="links inline").find_all("li")
    return _process_tags(tag_nodes)

def get_category(book_html):
    tag_nodes = book_html.find("ul", class_="links inline").find_all("li")
    return _process_category(tag_nodes)