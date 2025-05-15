import json
from Carousel import CarouselHandler, SuppportedType, Artwork, Book, Song

"""
Example script for extracting carousel items from Google search HTML files.

"""

custom_supported_types = [
    SuppportedType("artworks", Artwork, "Cz5hV", "iELo6"),
    # SuppportedType("books", Book, "JCZQSb", "Z8r5Gb X8kvh PZPZlf", skip_image_lookup=True),
    # SuppportedType("songs", Song, "uciohe", "kIXOkb cULTof", skip_image_lookup=True)
]

if __name__ == "__main__":
    fp = "files/van-gogh-paintings.html"
    # fp = "files/picasso-paintings.html"
    # fp = "files/stephen-king.html"
    # fp = "files/strokes.html"
    
    # Load HTML page
    with open(fp, 'r', encoding='utf-8') as f:
        html_to_process = f.read()
        
    # Extract Carousel Items
    carousel = CarouselHandler(
        html_to_process, 
        # Comment the next line to enable all supported types (art, books, and songs)
        supported_types=custom_supported_types
    )
    
    # Output as JSON to file
    with open("files/output/van-gogh-output.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(carousel.to_obj(), indent=2, ensure_ascii=False))