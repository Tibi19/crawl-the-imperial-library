import json

metadata = {}
with open("books_metadata.json", "r") as metadata_file:
    metadata = json.load(metadata_file)

datasets = metadata['books_metadata']

tags = set()
for data in datasets:
    for tag in data['tags']:
        tags.add(tag)

tags_list = list(tags)
tags_list = sorted(tags_list, key = lambda x : x.casefold())  
with open("books_tags.json", "w") as tags_file:
    json.dump(tags_list, tags_file, sort_keys = False, indent = 4)