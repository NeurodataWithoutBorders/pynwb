from pynwb.base import ExternalImage, Images, ImageReferences
from pynwb.testing import TestCase


class TestExternalImage(TestCase):
    """Test the ExternalImage class."""

    def test_init(self):
        """Test creating an ExternalImage."""
        file_path = "path/to/image.jpg"
        ext_img = ExternalImage(name="test_external_image", data=file_path)

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)
        self.assertIsNone(ext_img.description)

    def test_init_with_description(self):
        """Test creating an ExternalImage with a description."""
        file_path = "path/to/image.jpg"
        description = "An external image"
        ext_img = ExternalImage(name="test_external_image", data=file_path, description=description)

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)
        self.assertEqual(ext_img.description, description)

    def test_url_as_file_path(self):
        """Test creating an ExternalImage with a URL as the file path."""
        file_path = "https://example.com/image.jpg"
        ext_img = ExternalImage(name="test_external_image", data=file_path)

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)

    def test_in_images_container(self):
        """Test adding an ExternalImage to an Images container."""
        ext_img1 = ExternalImage(name="test_external_image1", data="path/to/image1.jpg")
        ext_img2 = ExternalImage(name="test_external_image2", data="path/to/image2.jpg")

        # Create an Images container with the ExternalImage objects
        images = Images(name="test_images", images=[ext_img1, ext_img2])

        # Check that the ExternalImage objects are in the Images container
        self.assertIn("test_external_image1", images.images)
        self.assertIn("test_external_image2", images.images)
        self.assertIs(images.images["test_external_image1"], ext_img1)
        self.assertIs(images.images["test_external_image2"], ext_img2)

    def test_with_image_references(self):
        """Test using ExternalImage with ImageReferences."""
        ext_img1 = ExternalImage(name="test_external_image1", data="path/to/image1.jpg")
        ext_img2 = ExternalImage(name="test_external_image2", data="path/to/image2.jpg")

        # Create ImageReferences with the ExternalImage objects
        image_references = ImageReferences(name="order_of_images", data=[ext_img2, ext_img1])

        # Create an Images container with the ExternalImage objects and ImageReferences
        images = Images(name="test_images", images=[ext_img1, ext_img2], order_of_images=image_references)

        # Check that the order in ImageReferences is correct
        self.assertIs(images.order_of_images[0], ext_img2)
        self.assertIs(images.order_of_images[1], ext_img1)
