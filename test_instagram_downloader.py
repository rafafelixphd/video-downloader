import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from downloaders.instagram import InstagramDownloader


class TestInstagramDownloaderInstantiation:
    """Tests for InstagramDownloader instantiation"""

    def test_instagram_downloader_instantiation(self):
        """Test that InstagramDownloader can be instantiated"""
        downloader = InstagramDownloader()
        assert downloader is not None
        assert isinstance(downloader, InstagramDownloader)

    def test_instagram_downloader_has_loader(self):
        """Test that InstagramDownloader has an instaloader context"""
        downloader = InstagramDownloader()
        assert hasattr(downloader, 'loader')
        assert downloader.loader is not None


class TestInstagramDownloaderFilename:
    """Tests for filename generation inherited from BaseDownloader"""

    def test_instagram_uses_base_filename_format(self):
        """Test that Instagram downloader uses BaseDownloader filename format"""
        downloader = InstagramDownloader()
        url = "https://www.instagram.com/reel/ABC123/"
        filename = downloader.generate_filename(url)

        # Verify format: YYYYMMDD_12hash.mp4
        assert '_' in filename
        assert filename.endswith('.mp4')

    def test_instagram_filename_has_date_prefix(self):
        """Test that filename has date prefix from BaseDownloader"""
        downloader = InstagramDownloader()
        url = "https://www.instagram.com/reel/ABC123/"
        filename = downloader.generate_filename(url)

        date_part = filename.split('_')[0]
        assert len(date_part) == 8  # YYYYMMDD format
        assert date_part.isdigit()

    def test_instagram_filename_has_hash(self):
        """Test that filename includes hash from BaseDownloader"""
        downloader = InstagramDownloader()
        url = "https://www.instagram.com/reel/ABC123/"
        filename = downloader.generate_filename(url)

        hash_part = filename.split('_')[1].split('.')[0]
        assert len(hash_part) == 12  # 12 character hash


class TestInstagramDownloaderErrorHandling:
    """Tests for error handling in Instagram downloader"""

    def test_instagram_invalid_url_raises_error(self):
        """Test that non-Instagram URL raises RuntimeError"""
        downloader = InstagramDownloader()

        with pytest.raises(RuntimeError, match="URL must be an Instagram URL"):
            downloader._download_video("https://www.youtube.com/watch?v=ABC123", "dummy_path")

    def test_instagram_malformed_url_raises_error(self):
        """Test that malformed URL raises RuntimeError"""
        downloader = InstagramDownloader()

        with pytest.raises(RuntimeError):
            downloader._download_video("https://www.instagram.com/", "dummy_path")

    def test_instagram_invalid_shortcode_raises_error(self):
        """Test that invalid shortcode raises RuntimeError"""
        downloader = InstagramDownloader()

        with pytest.raises(RuntimeError):
            downloader._download_video("https://www.instagram.com/reel/!!!invalid!!!/", "dummy_path")

    @patch('downloaders.instagram.instaloader.Post')
    def test_instagram_non_video_post_raises_error(self, mock_post_class):
        """Test that non-video post raises RuntimeError"""
        # Mock a post that is not a video
        mock_post = MagicMock()
        mock_post.is_video = False
        mock_post_class.from_shortcode.return_value = mock_post

        downloader = InstagramDownloader()

        with pytest.raises(RuntimeError, match="does not point to a video"):
            downloader._download_video("https://www.instagram.com/reel/ABC123/", "dummy_path")

    @patch('downloaders.instagram.instaloader.Post')
    def test_instagram_handles_instaloader_exception(self, mock_post_class):
        """Test that InstaloaderException is caught and converted to RuntimeError"""
        import instaloader

        mock_post_class.from_shortcode.side_effect = instaloader.InstaloaderException("Connection failed")

        downloader = InstagramDownloader()

        with pytest.raises(RuntimeError, match="Instagram download failed"):
            downloader._download_video("https://www.instagram.com/reel/ABC123/", "dummy_path")


class TestInstagramDownloaderDownloadIntegration:
    """Integration tests for download method (using mocks)"""

    @patch('downloaders.instagram.instaloader.Post')
    def test_instagram_download_creates_file(self, mock_post_class):
        """Test that download method creates the video file via mocked download"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks for Post
            mock_post = MagicMock()
            mock_post.is_video = True
            mock_post_class.from_shortcode.return_value = mock_post

            downloader = InstagramDownloader()
            save_path = os.path.join(tmpdir, "downloads")
            os.makedirs(save_path, exist_ok=True)

            # Mock the download_post method to create an actual MP4 file
            def mock_download(post, target):
                # Create a dummy MP4 file
                mp4_path = os.path.join(target, "video.mp4")
                Path(mp4_path).touch()

            downloader.loader.download_post = mock_download

            url = "https://www.instagram.com/reel/ABC123/"
            success, filepath = downloader.download(url, save_path)

            # Verify the file was moved correctly
            assert success is True
            assert os.path.exists(filepath)
            assert filepath.endswith('.mp4')

    def test_instagram_download_method_returns_tuple(self):
        """Test that download method returns a tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = InstagramDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            # This will fail due to invalid post, but we're testing the signature
            success, result = downloader.download(url, tmpdir)

            assert isinstance(success, bool)
            assert isinstance(result, str)

    def test_instagram_download_empty_url_returns_false(self):
        """Test that empty URL returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = InstagramDownloader()

            success, error_msg = downloader.download("", tmpdir)

            assert success is False
            assert "URL cannot be empty" in error_msg

    def test_instagram_download_empty_save_path_returns_false(self):
        """Test that empty save_path returns False"""
        downloader = InstagramDownloader()
        url = "https://www.instagram.com/reel/ABC123/"

        success, error_msg = downloader.download(url, "")

        assert success is False
        assert "Save path cannot be empty" in error_msg


class TestInstagramDownloaderURLParsing:
    """Tests for URL parsing and shortcode extraction"""

    def test_instagram_url_with_trailing_slash(self):
        """Test parsing URL with trailing slash"""
        downloader = InstagramDownloader()

        # Should extract shortcode without raising ValueError for format
        try:
            with patch('downloaders.instagram.instaloader.Post') as mock_post_class:
                mock_post = MagicMock()
                mock_post.is_video = False
                mock_post_class.from_shortcode.return_value = mock_post

                downloader._download_video("https://www.instagram.com/reel/ABC123/", "dummy_path")
        except RuntimeError as e:
            # Should fail because it's not a video, not because URL is invalid
            assert "does not point to a video" in str(e)

    def test_instagram_url_without_trailing_slash(self):
        """Test parsing URL without trailing slash"""
        downloader = InstagramDownloader()

        try:
            with patch('downloaders.instagram.instaloader.Post') as mock_post_class:
                mock_post = MagicMock()
                mock_post.is_video = False
                mock_post_class.from_shortcode.return_value = mock_post

                downloader._download_video("https://www.instagram.com/reel/ABC123", "dummy_path")
        except RuntimeError as e:
            # Should fail because it's not a video, not because URL is invalid
            assert "does not point to a video" in str(e)

    def test_instagram_various_url_formats(self):
        """Test that downloader accepts various Instagram URL formats"""
        downloader = InstagramDownloader()

        urls = [
            "https://www.instagram.com/reel/ABC123/",
            "https://www.instagram.com/reel/ABC123",
            "https://instagram.com/reel/ABC123/",
            "https://instagram.com/reel/ABC_123-456/",
        ]

        for url in urls:
            try:
                with patch('downloaders.instagram.instaloader.Post') as mock_post_class:
                    mock_post = MagicMock()
                    mock_post.is_video = False
                    mock_post_class.from_shortcode.return_value = mock_post

                    downloader._download_video(url, "dummy_path")
            except RuntimeError as e:
                # All should fail with "not a video" not "invalid URL"
                assert "does not point to a video" in str(e), f"Unexpected error for {url}: {str(e)}"
