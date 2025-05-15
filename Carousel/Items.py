import html
from dataclasses import dataclass
from typing import List, Optional

from bs4 import Tag

def qualify_link(link: str) -> str:
    """
    Ensures a link is a fully qualified URL.
    
    Args:
        link (str): The link to qualify, which may be a full URL or a path
        
    Returns:
        str: A fully qualified URL, prefixed with Google's domain if needed
    """
    # This doesn't handle regions (could be .co.uk), or if it doesn't actually come from google
    # I believe it's out of scope, but we could use regex or similar to find what google link to use
    if link.startswith("https://") or link.startswith("http://"):
        return link
    return "https://www.google.com" + link


@dataclass
class CarouselItem:
    """
    Base class representing an item in a Google search carousel.
    
    Attributes:
        title (str): The title of the carousel item
        extensions (List[str]): Additional information about the item
        link (str): URL to the item's full details
        image (Optional[str]): Image URL or data URI for the item
        id (Optional[str]): Unique identifier for the item
    """
    title: str
    extensions: List[str]
    link: str
    image: Optional[str] = None
    id: Optional[str] = None
    
    def to_obj(self) -> dict:
        """
        Converts the carousel item to a dictionary for JSON serialisation.
        
        Returns:
            dict: A dictionary representation of the carousel item
        """
        results = {
            "name": self.title,
            "extensions": self.extensions,
            "link": self.link,
            "image": self.image
        }
        # Remove empty extensions to match target output
        if not self.extensions:
            results.pop("extensions")
        return results
    
    @classmethod
    def from_div(cls, div: Tag) -> "CarouselItem":
        """Generates an Instance from a div.

        Args:
            div (Tag): The div tag to look for information in

        Raises:
            NotImplementedError: Raised by default if not overridden in subclass
        """
        # todo write a general from_div() method that will work for each item type
        raise NotImplementedError()
   
class Artwork(CarouselItem):
    """
    Represents an artwork item in a Google search carousel.
    
    Inherits from the CarouselItem class and provides specific parsing
    for artwork HTML structure.
    """
    @classmethod
    def from_div(cls, div: Tag) -> "Artwork":
        """
        Creates an Artwork instance from a div HTML element.
        
        Args:
            div (Tag): BeautifulSoup Tag containing artwork information
            
        Returns:
            Artwork: A new Artwork instance with extracted data
            
        Raises:
            ValueError: If the div has an invalid structure for artwork
        """
        try:
            link_tag = div.find("a")
            img_tag = link_tag.find("img")
            info_div = link_tag.find("div", {"class": "KHK6lb"})
        except AttributeError as e:
            raise ValueError("Invalid Artwork div structure") from e
        
        if not img_tag:
            raise ValueError("Invalid Artwork div structure") 
        
        id = None
        img = None
        # Try to get image directly
        try:
            img = html.unescape(img_tag["data-src"])
        except KeyError:
            # Use thumbnail and get ID
            # ID will be used to find full image later
            try:
                img = html.unescape(img_tag["src"])
            except KeyError:
                pass
            
            try:
                id = img_tag["id"]
            except KeyError:
                pass
                
        link = link_tag['href']
        
        try:
            title = html.unescape(info_div.find("div", {"class": "pgNMRc"}).get_text())
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Carousel missing title") from e
        
        # It's OK for the date to be missing, use None if not found
        extensions = info_div.find("div", {"class": "cxzHyb"}).contents

        
        return cls(title, extensions, qualify_link(link), id=id, image=img)

class Book(CarouselItem):
    """
    Represents a book item in a Google search carousel.
    
    Inherits from the CarouselItem class and provides specific parsing
    for book HTML structure.
    """
    @classmethod
    def from_div(cls, div: Tag) -> "Book":
        """
        Creates a Book instance from a div HTML element.
        
        Args:
            div (Tag): BeautifulSoup Tag containing book information
            
        Returns:
            Book: A new Book instance with extracted data
            
        Raises:
            ValueError: If the div has an invalid structure for a book
        """
        try:
            link_tag = div.find("a")
            img_tag = link_tag.find("img")
            info_div = link_tag.find("div", {"class", "TT9RUc uV10if"})
        except AttributeError as e:
            raise ValueError("Invalid Book div structure") from e
        
        if not img_tag:
            raise ValueError("Invalid Book div structure")
        
        id = None
        img = None
        # Try to get image directly
        try:
            img = html.unescape(img_tag["data-src"])
        except KeyError:
            # Use thumbnail and get ID
            # ID will be used to find full image later
            try:
                img = html.unescape(img_tag["src"])
            except KeyError:
                pass
            
            try:
                id = img_tag["id"]
            except KeyError:
                pass
                
        link = link_tag['href']
        
        try:
            title = html.unescape(info_div.find("div", {"class": "JjtOHd"}).contents[0])
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Carousel missing title") from e

        extensions = info_div.find("div", {"class": "ellip yF4Rkc AqEFvb"}).contents

        return cls(title, extensions, qualify_link(link), id=id, image=img)


class Song(CarouselItem):
    """
    Represents a song item in a Google search carousel.
    
    Inherits from the CarouselItem class and provides specific parsing
    for song HTML structure.
    """
    @classmethod
    def from_div(cls, div: Tag) -> "Song":
        """
        Creates a Song instance from a div HTML element.
        
        Args:
            div (Tag): BeautifulSoup Tag containing song information
            
        Returns:
            Song: A new Song instance with extracted data
            
        Raises:
            ValueError: If the div has an invalid structure for a song
        """
        try:
            link_tag = div.find("a")
            img_tag = link_tag.find("img")
            info_div = link_tag.find("div", {"class", "junCMe"})
        except AttributeError as e:
            raise ValueError("Invalid Song div structure") from e
            
        if not img_tag:
            raise ValueError("Invalid Song div structure")
        
        id = None
        img = None
        # Try to get image directly
        try:
            img = html.unescape(img_tag["data-src"])
        except KeyError:
            # Use thumbnail and get ID
            # ID will be used to find full image later
            try:
                img = html.unescape(img_tag["src"])
            except KeyError:
                pass
            
            try:
                id = img_tag["id"]
            except KeyError:
                pass
                
        link = link_tag['href']
        
        try:
            title = html.unescape(info_div.find("div", {"class": "CYJS5e title"}).contents[0])
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Carousel missing title") from e
        
        # Remove divider between album and date
        extensions = [c.get_text() for c in info_div.find("div", {"class": "uDMnUc wYIIv"}).contents if c.get_text() != " · "]
        
        return cls(title, extensions, qualify_link(link), id=id, image=img)