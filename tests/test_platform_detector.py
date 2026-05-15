"""
Tests for the platform_detector module.

Verifies that the detect_platform() function correctly identifies platforms
and returns the appropriate downloader instances.
"""

import pytest
from platform_detector import detect_platform
from downloaders.instagram import InstagramDownloader
from downloaders.youtube import YouTubeLinkedInDownloader


class TestDetectPlatform:
    """Test suite for the detect_platform() function."""

    # Instagram URL tests
    def test_instagram_reel_url(self):
        """Test detection of Instagram reel URL."""
        url = 'https://www.instagram.com/reel/ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, InstagramDownloader)
        assert not isinstance(downloader, YouTubeLinkedInDownloader)

    def test_instagram_url_without_trailing_slash(self):
        """Test detection of Instagram URL without trailing slash."""
        url = 'https://www.instagram.com/reel/ABC123'
        downloader = detect_platform(url)
        assert isinstance(downloader, InstagramDownloader)

    def test_instagram_url_with_uppercase(self):
        """Test case-insensitive detection of Instagram URL."""
        url = 'https://www.INSTAGRAM.com/reel/XYZ789/'
        downloader = detect_platform(url)
        assert isinstance(downloader, InstagramDownloader)

    def test_instagram_post_url(self):
        """Test detection of Instagram post URL."""
        url = 'https://instagram.com/p/ABC123DEF/'
        downloader = detect_platform(url)
        assert isinstance(downloader, InstagramDownloader)

    # YouTube URL tests
    def test_youtube_watch_url(self):
        """Test detection of YouTube watch URL."""
        url = 'https://www.youtube.com/watch?v=ABC123xyz'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)
        assert not isinstance(downloader, InstagramDownloader)

    def test_youtube_youtu_be_short_url(self):
        """Test detection of YouTube youtu.be short URL."""
        url = 'https://youtu.be/ABC123xyz'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_youtube_url_with_uppercase(self):
        """Test case-insensitive detection of YouTube URL."""
        url = 'https://www.YOUTUBE.com/watch?v=ABC123xyz'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_youtu_be_url_with_uppercase(self):
        """Test case-insensitive detection of youtu.be short URL."""
        url = 'https://YOUTU.BE/ABC123xyz'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_youtube_playlist_url(self):
        """Test detection of YouTube playlist URL."""
        url = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    # LinkedIn URL tests
    def test_linkedin_post_url(self):
        """Test detection of LinkedIn post URL."""
        url = 'https://www.linkedin.com/posts/activity-12345678_ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)
        assert not isinstance(downloader, InstagramDownloader)

    def test_linkedin_video_url(self):
        """Test detection of LinkedIn video URL."""
        url = 'https://linkedin.com/feed/video/12345678/'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_linkedin_url_with_uppercase(self):
        """Test case-insensitive detection of LinkedIn URL."""
        url = 'https://www.LINKEDIN.com/posts/ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    # Unknown platform tests
    def test_unknown_url_defaults_to_youtube_downloader(self):
        """Test that unknown URLs default to YouTubeLinkedInDownloader."""
        url = 'https://example.com/video/ABC123'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)
        assert not isinstance(downloader, InstagramDownloader)

    def test_vimeo_url_defaults_to_youtube_downloader(self):
        """Test that Vimeo URLs default to YouTubeLinkedInDownloader."""
        url = 'https://vimeo.com/123456789'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_generic_url_defaults_to_youtube_downloader(self):
        """Test that generic URLs default to YouTubeLinkedInDownloader."""
        url = 'https://example.org/video'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    # Edge cases
    def test_mixed_case_instagram_url(self):
        """Test detection with mixed case Instagram URL."""
        url = 'https://www.InStAgRaM.com/reel/ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, InstagramDownloader)

    def test_mixed_case_youtube_url(self):
        """Test detection with mixed case YouTube URL."""
        url = 'https://www.YoUtUbE.com/watch?v=ABC123'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_mixed_case_youtu_be_url(self):
        """Test detection with mixed case youtu.be URL."""
        url = 'https://YoUtU.bE/ABC123'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    def test_mixed_case_linkedin_url(self):
        """Test detection with mixed case LinkedIn URL."""
        url = 'https://www.LiNkEdIn.com/posts/ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, YouTubeLinkedInDownloader)

    # Return type validation
    def test_returns_base_downloader_instance(self):
        """Test that returned object is a BaseDownloader instance."""
        from downloaders.base import BaseDownloader
        url = 'https://www.instagram.com/reel/ABC123/'
        downloader = detect_platform(url)
        assert isinstance(downloader, BaseDownloader)

    def test_each_call_returns_new_instance(self):
        """Test that each call returns a new instance."""
        url = 'https://www.instagram.com/reel/ABC123/'
        downloader1 = detect_platform(url)
        downloader2 = detect_platform(url)
        assert downloader1 is not downloader2
        assert isinstance(downloader1, InstagramDownloader)
        assert isinstance(downloader2, InstagramDownloader)
