from pynwb.base import ExternalImage, Images, ImageReferences
from pynwb.testing import TestCase


class TestExternalImage(TestCase):
    """Test the ExternalImage class."""

    def test_init(self):
        """Test creating an ExternalImage."""
        file_path = "path/to/image.jpg"
        ext_img = ExternalImage(name="test_external_image", data=file_path, image_format="JPEG")

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)
        self.assertEqual(ext_img.image_format, "JPEG")
        self.assertIsNone(ext_img.description)

    def test_init_with_fields(self):
        """Test creating an ExternalImage with a description, image format, and image mode."""
        file_path = "path/to/image.jpg"
        description = "An external image"
        ext_img = ExternalImage(name="test_external_image", data=file_path, description=description,
                                image_format="JPEG", image_mode='RGB')

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)
        self.assertEqual(ext_img.description, description)
        self.assertEqual(ext_img.image_format, "JPEG")
        self.assertEqual(ext_img.image_mode, 'RGB')

    def test_init_invalid_image_format(self):
        with self.assertRaises(ValueError):
            ExternalImage(name="test_external_image", data="path/to/image.jpg", image_format="INVALID_FORMAT")

    def test_url_as_file_path(self):
        """Test creating an ExternalImage with a URL as the file path."""
        file_path = "https://example.com/image.jpg"
        ext_img = ExternalImage(name="test_external_image", data=file_path, image_format="JPEG")

        self.assertEqual(ext_img.name, "test_external_image")
        self.assertEqual(ext_img.data, file_path)

    def test_in_images_container(self):
        """Test adding an ExternalImage to an Images container."""
        ext_img1 = ExternalImage(name="test_external_image1", data="path/to/image1.jpg", image_format="JPEG")
        ext_img2 = ExternalImage(name="test_external_image2", data="path/to/image2.png", image_format="PNG")
        ext_img3 = ExternalImage(name="test_external_image3", data="path/to/image3.gif", image_format="GIF")

        # Create an Images container with the ExternalImage objects
        images = Images(name="test_images", images=[ext_img1, ext_img2, ext_img3])

        # Check that the ExternalImage objects are in the Images container
        self.assertIn("test_external_image1", images.images)
        self.assertIn("test_external_image2", images.images)
        self.assertIs(images.images["test_external_image1"], ext_img1)
        self.assertIs(images.images["test_external_image2"], ext_img2)
        self.assertIs(images.images["test_external_image3"], ext_img3)

    def test_with_image_references(self):
        """Test using ExternalImage with ImageReferences."""
        ext_img1 = ExternalImage(name="test_external_image1", data="path/to/image1.jpg", image_format="JPEG")
        ext_img2 = ExternalImage(name="test_external_image2", data="path/to/image2.png", image_format="PNG")
        ext_img3 = ExternalImage(name="test_external_image3", data="path/to/image3.gif", image_format="GIF")

        # Create ImageReferences with the ExternalImage objects
        image_references = ImageReferences(name="order_of_images", data=[ext_img3, ext_img2, ext_img1])

        # Create an Images container with the ExternalImage objects and ImageReferences
        images = Images(name="test_images", images=[ext_img1, ext_img2, ext_img3], order_of_images=image_references)

        # Check that the order in ImageReferences is correct
        self.assertIs(images.order_of_images[0], ext_img3)
        self.assertIs(images.order_of_images[1], ext_img2)
        self.assertIs(images.order_of_images[2], ext_img1)
