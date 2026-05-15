import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from downloaders.youtube import YouTubeLinkedInDownloader


class TestYouTubeLinkedInDownloaderInstantiation:
    """Tests for YouTubeLinkedInDownloader instantiation"""

    def test_youtube_downloader_instantiation(self):
        """Test that YouTubeLinkedInDownloader can be instantiated"""
        downloader = YouTubeLinkedInDownloader()
        assert downloader is not None
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_youtube_downloader_has_ydl_opts(self):
        """Test that YouTubeLinkedInDownloader has yt-dlp options configured"""
        downloader = YouTubeLinkedInDownloader()
        assert hasattr(downloader, 'ydl_opts')
        assert downloader.ydl_opts is not None
        assert 'format' in downloader.ydl_opts
        assert downloader.ydl_opts['format'] == 'best[ext=mp4]'


class TestYouTubeLinkedInDownloaderFilename:
    """Tests for filename generation inherited from BaseDownloader"""

    def test_youtube_uses_base_filename_format(self):
        """Test that YouTube downloader uses BaseDownloader filename format"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"
        filename = downloader.generate_filename(url)

        # Verify format: YYYYMMDD_12hash.mp4
        assert '_' in filename
        assert filename.endswith('.mp4')

    def test_youtube_filename_has_date_prefix(self):
        """Test that filename has date prefix from BaseDownloader"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"
        filename = downloader.generate_filename(url)

        date_part = filename.split('_')[0]
        assert len(date_part) == 8  # YYYYMMDD format
        assert date_part.isdigit()

    def test_youtube_filename_has_hash(self):
        """Test that filename includes hash from BaseDownloader"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"
        filename = downloader.generate_filename(url)

        hash_part = filename.split('_')[1].split('.')[0]
        assert len(hash_part) == 12  # 12 character hash

    def test_linkedin_uses_base_filename_format(self):
        """Test that LinkedIn downloader uses BaseDownloader filename format"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.linkedin.com/feed/update/urn:li:activity:123456/"
        filename = downloader.generate_filename(url)

        # Verify format: YYYYMMDD_12hash.mp4
        assert '_' in filename
        assert filename.endswith('.mp4')


class TestYouTubeLinkedInDownloaderErrorHandling:
    """Tests for error handling in YouTube/LinkedIn downloader"""

    def test_youtube_invalid_url_raises_error(self):
        """Test that non-YouTube/LinkedIn URL raises RuntimeError"""
        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="URL must be a YouTube or LinkedIn URL"):
            downloader._download_video("https://www.instagram.com/reel/ABC123/", "dummy_path")

    def test_youtube_twitter_url_raises_error(self):
        """Test that Twitter URL raises RuntimeError"""
        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="URL must be a YouTube or LinkedIn URL"):
            downloader._download_video("https://twitter.com/user/status/123456", "dummy_path")

    def test_youtube_empty_url_raises_error(self):
        """Test that empty URL raises RuntimeError"""
        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="URL must be a YouTube or LinkedIn URL"):
            downloader._download_video("", "dummy_path")

    @patch('downloaders.youtube.yt_dlp.YoutubeDL')
    def test_youtube_handles_download_error(self, mock_ydl_class):
        """Test that DownloadError is caught and converted to RuntimeError"""
        import yt_dlp

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Video not found")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="Download failed"):
            downloader._download_video("https://www.youtube.com/watch?v=ABC123", "dummy_path")

    @patch('downloaders.youtube.yt_dlp.YoutubeDL')
    def test_youtube_handles_generic_exception(self, mock_ydl_class):
        """Test that generic exceptions are caught and converted to RuntimeError"""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="Error downloading video"):
            downloader._download_video("https://www.youtube.com/watch?v=ABC123", "dummy_path")

    @patch('downloaders.youtube.yt_dlp.YoutubeDL')
    def test_youtube_handles_none_info(self, mock_ydl_class):
        """Test that None info response raises RuntimeError"""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = None
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = YouTubeLinkedInDownloader()

        with pytest.raises(RuntimeError, match="Failed to extract video information"):
            downloader._download_video("https://www.youtube.com/watch?v=ABC123", "dummy_path")


class TestYouTubeLinkedInDownloaderDownloadIntegration:
    """Integration tests for download method (using mocks)"""

    @patch('downloaders.youtube.yt_dlp.YoutubeDL')
    def test_youtube_download_creates_file(self, mock_ydl_class):
        """Test that download method creates the video file via mocked download"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks for YoutubeDL
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {'id': 'ABC123', 'title': 'Test Video'}
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            downloader = YouTubeLinkedInDownloader()
            save_path = os.path.join(tmpdir, "downloads")
            os.makedirs(save_path, exist_ok=True)

            # We need to actually create the file that yt-dlp would create
            def mock_extract_info(url, download):
                expected_file = os.path.join(save_path, downloader.generate_filename(url))
                # Remove .mp4 extension as yt-dlp adds it
                output_path = expected_file.rsplit('.', 1)[0]
                Path(output_path + '.mp4').touch()
                return {'id': 'ABC123', 'title': 'Test Video'}

            mock_ydl_instance.extract_info = mock_extract_info
            # Also need to handle the outtmpl assignment
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            url = "https://www.youtube.com/watch?v=ABC123"
            success, filepath = downloader.download(url, save_path)

            # The success should be True because extract_info returns non-None
            assert success is True
            assert isinstance(filepath, str)

    def test_youtube_download_method_returns_tuple(self):
        """Test that download method returns a tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = YouTubeLinkedInDownloader()
            url = "https://www.youtube.com/watch?v=ABC123"

            # This will fail due to missing video, but we're testing the signature
            success, result = downloader.download(url, tmpdir)

            assert isinstance(success, bool)
            assert isinstance(result, str)

    def test_youtube_download_empty_url_returns_false(self):
        """Test that empty URL returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = YouTubeLinkedInDownloader()

            success, error_msg = downloader.download("", tmpdir)

            assert success is False
            assert "URL cannot be empty" in error_msg

    def test_youtube_download_empty_save_path_returns_false(self):
        """Test that empty save_path returns False"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"

        success, error_msg = downloader.download(url, "")

        assert success is False
        assert "Save path cannot be empty" in error_msg

    def test_linkedin_download_method_returns_tuple(self):
        """Test that LinkedIn URLs also return a tuple from download method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = YouTubeLinkedInDownloader()
            url = "https://www.linkedin.com/feed/update/urn:li:activity:123456/"

            success, result = downloader.download(url, tmpdir)

            assert isinstance(success, bool)
            assert isinstance(result, str)


class TestYouTubeLinkedInDownloaderURLSupport:
    """Tests for YouTube and LinkedIn URL format support"""

    def test_youtube_standard_url_format(self):
        """Test that standard YouTube URL format is recognized"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"

        # Should raise RuntimeError for actual download, not for URL validation
        with patch('downloaders.youtube.yt_dlp.YoutubeDL') as mock_ydl_class:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {'id': 'ABC123'}
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            # Should not raise "must be a YouTube or LinkedIn URL" error
            try:
                downloader._download_video(url, "dummy_path")
            except RuntimeError as e:
                assert "URL must be a YouTube or LinkedIn URL" not in str(e)

    def test_youtube_short_url_format(self):
        """Test that YouTube short URL format (youtu.be) is recognized"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://youtu.be/ABC123"

        with patch('downloaders.youtube.yt_dlp.YoutubeDL') as mock_ydl_class:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {'id': 'ABC123'}
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            # Should not raise "must be a YouTube or LinkedIn URL" error
            try:
                downloader._download_video(url, "dummy_path")
            except RuntimeError as e:
                assert "URL must be a YouTube or LinkedIn URL" not in str(e)

    def test_linkedin_url_format(self):
        """Test that LinkedIn URL format is recognized"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.linkedin.com/feed/update/urn:li:activity:123456/"

        with patch('downloaders.youtube.yt_dlp.YoutubeDL') as mock_ydl_class:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {'id': '123456'}
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            # Should not raise "must be a YouTube or LinkedIn URL" error
            try:
                downloader._download_video(url, "dummy_path")
            except RuntimeError as e:
                assert "URL must be a YouTube or LinkedIn URL" not in str(e)

    def test_case_insensitive_url_validation(self):
        """Test that URL validation is case-insensitive"""
        downloader = YouTubeLinkedInDownloader()
        url = "https://www.YOUTUBE.COM/watch?v=ABC123"

        with patch('downloaders.youtube.yt_dlp.YoutubeDL') as mock_ydl_class:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {'id': 'ABC123'}
            mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

            # Should not raise "must be a YouTube or LinkedIn URL" error
            try:
                downloader._download_video(url, "dummy_path")
            except RuntimeError as e:
                assert "URL must be a YouTube or LinkedIn URL" not in str(e)
