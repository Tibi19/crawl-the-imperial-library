import json

metadata = {}
with open("books_metadata.json", "r") as metadata_file:
    metadata = json.load(metadata_file)

datasets = metadata['books_metadata']

id_corrector = 0

length = len(datasets)
for i in range(length):

    if i == length - 1:
        break

    data = datasets[i]
    id = data['id'].casefold()
    next_data = datasets[i + 1]
    next_id = next_data['id'].casefold()

    if id == next_id:
        id_corrected = f"{id}{id_corrector}"

        data['id'] = id_corrected

        text_file_path = f"book_texts/{data['fileName']}"

        with open(text_file_path, "r") as text_file_read:
            book_text = json.load(text_file_read)

        book_text['id'] = id_corrected
        with open(text_file_path, "w") as text_file_write:
            json.dump(book_text, text_file_write, sort_keys = False, indent = 4)

        id_corrector += 1
    
with open("books_metadata.json", "w") as metadata_file_write:
    json.dump(metadata, metadata_file_write, sort_keys = False, indent = 4)