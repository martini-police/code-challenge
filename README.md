# My Contribution

`Python 3.10.12`

- Handles Artwork, Songs, and Books
- Unit tests and output freeze test
 
[Example output here.](https://github.com/martini-police/code-challenge/tree/master/files/output)

## How it works

I have written CarouselHandler and CarouselItem classes. 

CarouselHandler is responsible for taking a Google SERP, and finding the items within it.
CarouselItem is a parent class of Artwork, Book, and Song. It is responsible for extracting information from valid `div`s. It has been written in such a way that other CarouselTypes (like Movies) can be easily implemented:

```py
default_supported_types = [
    SuppportedType("artworks", Artwork, "Cz5hV", "iELo6"),
    SuppportedType("books", Book, "JCZQSb", "Z8r5Gb X8kvh PZPZlf", skip_image_lookup=True),
    SuppportedType("songs", Song, "uciohe", "kIXOkb cULTof", skip_image_lookup=True),
    # SuppportedType("movies", ... ) # Add div classes here
]
```

CarouselHandler is responsible for parsing the HTML, and then finding each item type in the HTML. It is rare, but it is possible for a SERP to contain multiple CarouselTypes [("things to do in london" has "experiences" and "top sights")](https://www.google.com/search?q=Things+to+do+in+London&oq=Thin&gs_lcrp=EgZjaHJvbWUqDggAEEUYJxg7GIAEGIoFMg4IABBFGCcYOxiABBiKBTIGCAEQRRg5Mg0IAhAAGJIDGIAEGIoFMgoIAxAAGLEDGIAEMg0IBBAAGLEDGIAEGIoFMgYIBRBFGD0yBggGEEUYPTIGCAcQRRg90gEHOTM2ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8). This is supported but not fully tested. This class is also responsible for finding higher definition images from the script tags in the HTML.

For links, I have hardcoded the domain name to be "https://www.google.com" to match the output. This isn't ideal as the HTML could be taken from Google in another region (google.fr). I deemed it unnecessary for this exercise, but I would extract the base domain name from the HTML in real-life.

## Thought Process

I initially tried targeting the structure of an Artwork carousel item (e.g. a link tag with an image and a `div`) because I thought it would make the code more resilient to changes from Google. I didn't want to use class names as they weren't human readable / meaningful, and so there is a risk they could change and break the code.


However, after realising that the structure is different between Van Gogh and Picasso, but the `div` classes are the same, I decided to revert to using the `div` class names.


After testing against a Books carousel, I realised that the structure was very similar (apart from some flexboxes and other non-important elements), so we could just look up a different `div` class to find the items. 
Songs is an interesting case, as there can be 2 extensions (instead of the single date from Artwork).

## Further Improvements

- When looking for image data in the scripts, there are a few options to make the search process more efficient
  1. Cache the images by their ID, so that if an ID is found when searching for another ID, we can quickly find it later
    - This didn't result in any hits as the scripts seem to be in the same order as the images
  2. Cache when scripts are not containing images. Some scripts are for other things, so instead of always running regex on these scripts, we can instead remember that they don't store an image
  3. Start searching for the nth ID from the nth image - the scripts appear to be in the same order as the images that they reference, so we can start looking from the image's index, and then wrap around if needed.

> I tested these optimisations, but their impact was minimal. I decided that the relatively low number of scripts means that the complexity added to the code and the overhead of checking the cache etc probably wasn't worth it. For a bigger dataset, it may be worth it.

- The code could be made more elegant - I think a general `from_div` may work better than my current solution. However, as a proof of concept I believe this is sufficient. I would like to find the image, link and title in a more general way rather than relying on each type-specific `div` class. 

- I would like to write a proper JSON parser to convert the output to JSON, instead of the current messy way of doing it.

- There was some weirdness when handling escaped `=` characters. I've use a workaround, but would like to fix the root of problem.

## DRYness

There is a slight redundancy between the process of checking that a `div` contains a carousel item, and the extraction of data from such a `div`. They both rely on the same structure, so you _could_ just attempt to extract the data, and raise an error if the `div` isn't valid. However, I wanted to keep these matters separate, so that you are free to change both how a `div` is _found_ vs _handled_. There is probably a more happy medium, but I don't have more time for this project.

## Tests

The tests check that the output of Van Gogh is the same as the example array, and then some edge cases and unit tests.

```sh
$ python3 -m unittest test_Carousel.py
................
----------------------------------------------------------------------
Ran 16 tests in 0.395s

OK
```

## Usage

```py
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
## On macOS and Linux:
source venv/bin/activate
## On Windows:
# venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt

# Generate the example output array
python3 main.py
```

# Original ReadMe - Extract Van Gogh Paintings Code Challenge

Goal is to extract a list of Van Gogh paintings from the attached Google search results page.

![Van Gogh paintings](https://github.com/serpapi/code-challenge/blob/master/files/van-gogh-paintings.png?raw=true "Van Gogh paintings")

## Instructions

This is already fully supported on SerpApi. ([relevant test], [html file], [sample json], and [expected array].)
Try to come up with your own solution and your own test.
Extract the painting `name`, `extensions` array (date), and Google `link` in an array.

Fork this repository and make a PR when ready.

Programming language wise, Ruby (with RSpec tests) is strongly suggested but feel free to use whatever you feel like.

Parse directly the HTML result page ([html file]) in this repository. No extra HTTP requests should be needed for anything.

[relevant test]: https://github.com/serpapi/test-knowledge-graph-desktop/blob/master/spec/knowledge_graph_claude_monet_paintings_spec.rb
[sample json]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/van-gogh-paintings.json
[html file]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/van-gogh-paintings.html
[expected array]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/expected-array.json

Add also to your array the painting thumbnails present in the result page file (not the ones where extra requests are needed). 

Test against 2 other similar result pages to make sure it works against different layouts. (Pages that contain the same kind of carrousel. Don't necessarily have to be paintings.)

The suggested time for this challenge is 4 hours. But, you can take your time and work more on it if you want.
