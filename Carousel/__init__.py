from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from typing import List, Optional

from Carousel.Items import *

@dataclass
class SuppportedType:
    """
    Configuration class for different carousel item types.
    
    Defines the mapping between HTML structure and item types for parsing
    various Google search carousel types.
    
    Attributes:
        output_name (str): Key name for this type in output JSON
        item_type (CarouselItem): Class to instantiate for this type
        container_div_class (str): CSS class of the container div
        container_item_div_class (str): CSS class of individual item divs
        skip_image_lookup (Optional[bool]): Whether to skip image lookup for this type
    """
    output_name: str
    item_type: CarouselItem
    container_div_class: str
    container_item_div_class: str
    skip_image_lookup: Optional[bool] = False

default_supported_types = [
    SuppportedType("artworks", Artwork, "Cz5hV", "iELo6"),
    SuppportedType("books", Book, "JCZQSb", "Z8r5Gb X8kvh PZPZlf", skip_image_lookup=True),
    SuppportedType("songs", Song, "uciohe", "kIXOkb cULTof", skip_image_lookup=True)
]

class CarouselHandler:
    """
    Main handler for extracting carousel items from Google search HTML.
    
    Parses HTML content to find various carousel item types and converts them
    into structured data objects.
    """
    def find_type(self, st: SuppportedType) -> List[CarouselItem]:
        """
        Finds and extracts all carousel items of a specific type from HTML.
        
        Args:
            st (SuppportedType): The type configuration to search for
            
        Returns:
            List[CarouselItem]: A list of parsed carousel items of the specified type
        """
        try:
            container = self.soup.find('div', {"class": st.container_div_class})
            container_items = container.find_all('div', {'class': st.container_item_div_class})
        except AttributeError:
            return []
        
        items: List[CarouselItem] = [st.item_type.from_div(d) for d in container_items]

        if st.skip_image_lookup:
            return items
        
        for item in items:
            try:
                item.image = self.get_img_from_id(item.id)
            except ValueError:
                pass
        
        return items
        
    def __init__(self, html_: str, *, supported_types: List[SuppportedType]=default_supported_types):
        """
        Initialises the carousel handler and processes HTML content.
        
        Args:
            html_ (str): HTML content to parse
            supported_types (List[SuppportedType], optional): Carousel types to search for.
                Defaults to default_supported_types.
        """
        # Load and parse HTML
        self.soup = BeautifulSoup(html_, features="html.parser")
        
        self.objects = {t.output_name: self.find_type(t) for t in supported_types}
        
    def get_img_from_id(self, id: str) -> str:
        """
        Retrieves the full image data for a carousel item by its ID.
        
        Searches through script tags in the HTML to find image data associated
        with the specified ID.
        
        Args:
            id (str): The ID of the carousel item
            
        Returns:
            str: Image data as a data URI
            
        Raises:
            ValueError: If no image could be found for the given ID
        """
        #
        # Optimisations which could improve performance:
        #
        # 1. Cache the images by their id, so that if an ID is found when searching for another ID, we can quickly find it later
        #       - This didn't result in any hits as the scripts seem to be in the same order as the images
        # 2. Cache when scripts are not containing images. Some scripts are for other things, so instead of always running regex
        #       on these scripts, we can instead remember that they don't store an image
        # 3. Start searching for the nth ID from the nth image - the scripts appear to be in the same order as the images that
        #       they reference, so we can start looking from the image's index, and then wrap around if needed.
        #

        scripts = self.soup.find_all("script")
        target = f"var ii=['{id}']"
        
        # Use regex to capture the image data
        img_pattern =   r"""
            var\s+s\s*=\s*(['"`])       # Match var s = '<quote>
            (data:image[^'"`]+)         # Match value starting with data:image... Not specific for jpeg.
            \1                          # Match the same closing quote
        """

        for script in scripts:
            try:
                contents = script.contents[0]
            except KeyError:
                continue
            except IndexError:
                continue
            
            img_match = re.search(img_pattern, contents, re.VERBOSE)
            if img_match:
                # This script contains an image
                
                # Get image from script. 
                img = img_match.group(2)
                
                # Fix corrupted `=`
                img = re.sub(r'\\x3d', '=', img)
                
                # Check if this image is the one for the current ID.
                # Look from the back, so we don't scan the whole image data first.
                # <long img data><target><some other code>
                if contents.rfind(target) != -1:
                    return img

        raise ValueError(f"Could not find img for id {target}")
        
    def to_obj(self) -> dict:
        """
        Converts all carousel items to a dictionary format for JSON serialisation.
        
        Returns:
            dict: A dictionary with carousel type names as keys and lists of
                  serialised carousel items as values
        """
        # todo Write a JSON Serialiser to do this 
        return {k: [p.to_obj() for p in v] for k, v in self.objects.items()}

