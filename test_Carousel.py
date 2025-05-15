import unittest
import json
from Carousel import CarouselHandler, SuppportedType, Artwork, Book, Song
from Carousel.Items import CarouselItem, qualify_link

class TestCarouselHandler(unittest.TestCase):
    def test_find_images_empty_html(self):
        """Test CarouselHandler with empty HTML input"""
        carousel = CarouselHandler("")
        result = carousel.to_obj()
        self.assertEqual(result, {"artworks": [], "books": [], "songs": []})

    def test_find_images_invalid_html(self):
        """Test CarouselHandler with invalid HTML input"""
        carousel = CarouselHandler("<html><body>Broken HTML Structure</div></body></html>")
        result = carousel.to_obj()
        self.assertEqual(result, {"artworks": [], "books": [], "songs": []})
        
    def test_van_gogh_matches_expected_output(self):
        """Test that processing van-gogh-paintings.html produces the expected output"""
        with open("files/van-gogh-paintings.html", 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Test data only has artworks so disable other types
        carousel = CarouselHandler(
            html_content, 
            supported_types=[SuppportedType("artworks", Artwork, "Cz5hV", "iELo6")]
        )
        
        result = carousel.to_obj()
        
        with open("files/expected-array.json", 'r', encoding='utf-8') as f:
            expected = json.load(f)
        
        self.assertEqual(result, expected)
    
    def test_specific_supported_types(self):
        """Test that specifying supported types filters results correctly"""
        with open("files/strokes.html", 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Only look for songs
        songs_only = [SuppportedType("songs", Song, "uciohe", "kIXOkb cULTof", skip_image_lookup=True)]
        carousel = CarouselHandler(html_content, supported_types=songs_only)
        result = carousel.to_obj()
        
        # Ensure only songs are present
        self.assertIn("songs", result)
        self.assertNotIn("artworks", result)
        self.assertNotIn("books", result)
        self.assertTrue(len(result["songs"]) > 0, "Should find at least one song")
    
    def test_artwork_item_creation(self):
        """Test artwork item creation with simulated HTML"""
        from bs4 import BeautifulSoup
        
        # Create a simplified test div for an artwork with proper structure
        # that matches what the Artwork.from_div method expects
        html = """
        <html>
        <div class="iELo6">
            <a href="/link/to/artwork">
                <img src="thumbnail.jpg" id="img-id" />
                <div class="KHK6lb">
                    <div class="pgNMRc">Artwork Title</div>
                    <div class="cxzHyb">2023</div>
                </div>
            </a>
        </div>
        </html>
        """
        # Parse with html.parser to ensure consistent behavior
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="iELo6")
        
        artwork = Artwork.from_div(div)
        self.assertEqual(artwork.title, "Artwork Title")
        self.assertEqual(artwork.extensions, ["2023"])
        self.assertEqual(artwork.link, "https://www.google.com/link/to/artwork")
        self.assertEqual(artwork.image, "thumbnail.jpg")
        self.assertEqual(artwork.id, "img-id")
    
    def test_book_item_creation(self):
        """Test book item creation with simulated HTML"""
        from bs4 import BeautifulSoup
        
        # Create a simplified test div for a book
        html = """
        <div class="Z8r5Gb X8kvh PZPZlf">
            <a href="/link/to/book">
                <img src="book-cover.jpg" id="book-id" />
                <div class="TT9RUc uV10if">
                    <div class="JjtOHd">Book Title</div>
                    <div class="ellip yF4Rkc AqEFvb">Author Name</div>
                </div>
            </a>
        </div>
        """
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="Z8r5Gb")
        
        book = Book.from_div(div)
        self.assertEqual(book.title, "Book Title")
        self.assertEqual(book.extensions, ["Author Name"])
        self.assertEqual(book.link, "https://www.google.com/link/to/book")
        self.assertEqual(book.image, "book-cover.jpg")
        self.assertEqual(book.id, "book-id")
    
    def test_song_item_creation(self):
        """Test song item creation with simulated HTML"""
        from bs4 import BeautifulSoup
        
        # Create a simplified test div for a song
        html = """
        <div class="kIXOkb cULTof">
            <a href="/link/to/song">
                <img src="album-cover.jpg" id="song-id" />
                <div class="junCMe">
                    <div class="CYJS5e title">Song Title</div>
                    <div class="uDMnUc wYIIv"><span>Album Name</span> · <span>2023</span></div>
                </div>
            </a>
        </div>
        """
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="kIXOkb")
        
        song = Song.from_div(div)
        self.assertEqual(song.title, "Song Title")
        self.assertEqual(song.extensions, ["Album Name", "2023"])
        self.assertEqual(song.link, "https://www.google.com/link/to/song")
        self.assertEqual(song.image, "album-cover.jpg")
        self.assertEqual(song.id, "song-id")
    
    def test_error_handling_in_from_div(self):
        """Test error handling when HTML structure is unexpected"""
        from bs4 import BeautifulSoup
        
        # Create malformed HTML for testing
        html = """
        <div class="iELo6">
            <a href="/link/to/artwork">
                <!-- Missing img tag that would normally have the id attribute -->
                <div class="KHK6lb">
                    <!-- Empty title div -->
                    <div class="pgNMRc"></div>
                </div>
            </a>
        </div>
        """
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="iELo6")
        
        with self.assertRaises(ValueError):
            Artwork.from_div(div)
    
    def test_get_img_from_id_not_found(self):
        """Test handling of image ID that doesn't exist"""
        carousel = CarouselHandler("<html><script></script></html>")
        
        with self.assertRaises(ValueError):
            carousel.get_img_from_id("nonexistent-id")
            
    def test_get_img_from_id_success(self):
        """Test that the image lookup function successfully extracts image data"""
        # Create HTML with a script containing image data and ID reference
        test_id = "test-image-id"
        test_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
        
        html_content = f"""
        <html>
        <body>
            <div>Some content</div>
            <script>
                var s="data:image/jpeg;base64,/9j/4AAQSkZJRg=="
                var ii=['{test_id}']
            </script>
        </body>
        </html>
        """
        
        carousel = CarouselHandler(html_content)
        
        # Test the image lookup function
        image_data = carousel.get_img_from_id(test_id)
        
        # Verify the extracted image data matches what we expect
        self.assertEqual(image_data, test_image_data)
        
    def test_get_img_from_id_with_escaped_equals(self):
        """Test that the image lookup function handles escaped equals signs"""
        # Create HTML with a script containing image data with escaped equals sign
        test_id = "escaped-equals-id"
        # The actual image data in the HTML has escaped equals signs
        escaped_html = """
        <html>
        <body>
            <script>
                var s="data:image/jpeg;base64,/9j/4AAQSkZJRg\\x3d\\x3d"
                var ii=['escaped-equals-id']
            </script>
        </body>
        </html>
        """
        
        carousel = CarouselHandler(escaped_html)
        
        # Test the image lookup function
        image_data = carousel.get_img_from_id(test_id)
        
        # Verify the equals signs are properly unescaped
        self.assertEqual(image_data, "data:image/jpeg;base64,/9j/4AAQSkZJRg==")
    
    def test_error_handling_in_book_from_div(self):
        """Test error handling when HTML structure is unexpected for Book"""
        from bs4 import BeautifulSoup
        
        # Create malformed HTML for testing Book
        html = """
        <div class="Z8r5Gb X8kvh PZPZlf">
            <a href="/link/to/book">
                <!-- Missing img tag that would normally have the id attribute -->
                <div class="TT9RUc uV10if">
                    <!-- Empty title div -->
                    <div class="JjtOHd"></div>
                </div>
            </a>
        </div>
        """
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="Z8r5Gb")
        
        with self.assertRaises(ValueError):
            Book.from_div(div)
    
    def test_error_handling_in_song_from_div(self):
        """Test error handling when HTML structure is unexpected for Song"""
        from bs4 import BeautifulSoup
        
        # Create malformed HTML for testing Song
        html = """
        <div class="kIXOkb cULTof">
            <a href="/link/to/song">
                <!-- Missing img tag that would normally have the id attribute -->
                <div a="junCMe">
                    <!-- Empty title div -->
                    <div class="CYJS5e title"></div>
                </div>
            </a>
        </div>
        """
        soup = BeautifulSoup(html, features="html.parser")
        div = soup.find('div', class_="kIXOkb")
        
        with self.assertRaises(ValueError):
            Song.from_div(div)
    
    def test_to_obj_empty_extensions(self):
        """Test that empty extensions are removed from the output object"""
        item = CarouselItem("Test Item", [], "https://example.com")
        obj = item.to_obj()
        
        self.assertNotIn("extensions", obj)
        self.assertEqual(obj["name"], "Test Item")
        self.assertEqual(obj["link"], "https://example.com")
    
    def test_qualify_link(self):
        """Test the qualify_link function properly handles different URL formats"""
        from Carousel.Items import qualify_link
        
        # Already qualified links should remain unchanged
        self.assertEqual(qualify_link("https://example.com"), "https://example.com")
        self.assertEqual(qualify_link("http://example.com"), "http://example.com")
        
        # Relative links should be prefixed with Google domain
        self.assertEqual(qualify_link("/search"), "https://www.google.com/search")
        self.assertEqual(qualify_link(""), "https://www.google.com")
    
    def test_mixed_html_content(self):
        """Test processing HTML with a mix of different carousel types"""
        from bs4 import BeautifulSoup
        
        # Create HTML with artworks, books, and songs with the correct structure
        html = """
        <html>
        <body>
            <div class="Cz5hV">
                <div class="iELo6">
                    <a href="/link/to/artwork">
                        <img src="artwork.jpg" id="artwork-id" />
                        <div class="KHK6lb">
                            <div class="pgNMRc">Artwork Title</div>
                            <div class="cxzHyb">2023</div>
                        </div>
                    </a>
                </div>
            </div>
            <div class="JCZQSb">
                <div class="Z8r5Gb X8kvh PZPZlf">
                    <a href="/link/to/book">
                        <img src="book.jpg" id="book-id" />
                        <div class="TT9RUc uV10if">
                            <div class="JjtOHd">Book Title</div>
                            <div class="ellip yF4Rkc AqEFvb">Author</div>
                        </div>
                    </a>
                </div>
            </div>
            <div class="uciohe">
                <div class="kIXOkb cULTof">
                    <a href="/link/to/song">
                        <img src="song.jpg" id="song-id" />
                        <div class="junCMe">
                            <div class="CYJS5e title">Song Title</div>
                            <div class="uDMnUc wYIIv"><span>Artist</span> · <span>2023</span></div>
                        </div>
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        carousel = CarouselHandler(html)
        result = carousel.to_obj()
        
        # Check that all types are found
        self.assertIn("artworks", result)
        self.assertIn("books", result)
        self.assertIn("songs", result)
        
        # Check contents
        self.assertEqual(len(result["artworks"]), 1)
        self.assertEqual(result["artworks"][0]["name"], "Artwork Title")
        
        self.assertEqual(len(result["books"]), 1)
        self.assertEqual(result["books"][0]["name"], "Book Title")
        
        self.assertEqual(len(result["songs"]), 1)
        self.assertEqual(result["songs"][0]["name"], "Song Title")

if __name__ == "__main__":
    unittest.main()