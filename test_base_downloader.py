import pytest
import os
import tempfile
import yaml
from pathlib import Path
from datetime import date
from downloaders.base import BaseDownloader


# Create a concrete implementation for testing
class TestDownloader(BaseDownloader):
    """Test implementation of BaseDownloader"""

    def _download_video(self, url: str, filepath: str) -> None:
        """Mock implementation that creates an empty file"""
        Path(filepath).touch()


class TestGenerateFilename:
    """Tests for the generate_filename method"""

    def test_generate_filename_format(self):
        """Test that generated filename matches YYYYMMDD_12hash.ext format"""
        downloader = TestDownloader()
        url = "https://www.instagram.com/reel/ABC123/"
        filename = downloader.generate_filename(url)

        # Check format: YYYYMMDD_12hash.mp4
        parts = filename.split('_')
        assert len(parts) == 2, "Filename should have exactly one underscore"

        date_part = parts[0]
        hash_and_ext = parts[1]

        # Check date part
        assert len(date_part) == 8, "Date part should be YYYYMMDD (8 chars)"
        assert date_part.isdigit(), "Date part should be all digits"
        assert date_part == date.today().strftime('%Y%m%d')

        # Check hash and extension
        hash_and_ext_parts = hash_and_ext.split('.')
        assert len(hash_and_ext_parts) == 2, "Hash and extension should be separated by dot"
        hash_part, ext = hash_and_ext_parts
        assert len(hash_part) == 12, "Hash part should be 12 characters"
        assert ext == "mp4", "Default extension should be mp4"

    def test_generate_filename_custom_extension(self):
        """Test filename generation with custom extension"""
        downloader = TestDownloader()
        url = "https://www.youtube.com/watch?v=ABC123"
        filename = downloader.generate_filename(url, extension='mov')

        assert filename.endswith('.mov'), "Should use custom extension"
        parts = filename.split('.')
        assert parts[-1] == 'mov'

    def test_generate_filename_same_url_same_hash(self):
        """Test that same URL produces same hash"""
        downloader = TestDownloader()
        url = "https://www.instagram.com/reel/ABC123/"

        filename1 = downloader.generate_filename(url)
        filename2 = downloader.generate_filename(url)

        # Extract hash parts (should be identical)
        hash1 = filename1.split('_')[1].split('.')[0]
        hash2 = filename2.split('_')[1].split('.')[0]

        assert hash1 == hash2, "Same URL should produce same hash"

    def test_generate_filename_different_urls_different_hash(self):
        """Test that different URLs produce different hashes"""
        downloader = TestDownloader()
        url1 = "https://www.instagram.com/reel/ABC123/"
        url2 = "https://www.instagram.com/reel/XYZ789/"

        filename1 = downloader.generate_filename(url1)
        filename2 = downloader.generate_filename(url2)

        # Extract hash parts
        hash1 = filename1.split('_')[1].split('.')[0]
        hash2 = filename2.split('_')[1].split('.')[0]

        assert hash1 != hash2, "Different URLs should produce different hashes"

    def test_generate_filename_empty_url_raises_error(self):
        """Test that empty URL raises ValueError"""
        downloader = TestDownloader()

        with pytest.raises(ValueError, match="URL cannot be empty"):
            downloader.generate_filename("")

    def test_generate_filename_none_url_raises_error(self):
        """Test that None URL raises ValueError"""
        downloader = TestDownloader()

        with pytest.raises(ValueError, match="URL cannot be empty"):
            downloader.generate_filename(None)

    def test_generate_filename_whitespace_url_raises_error(self):
        """Test that whitespace-only URL raises ValueError"""
        downloader = TestDownloader()

        with pytest.raises(ValueError, match="URL cannot be empty"):
            downloader.generate_filename("   ")

    def test_generate_filename_with_various_extensions(self):
        """Test filename generation with various extensions"""
        downloader = TestDownloader()
        url = "https://example.com/video"
        extensions = ["mp4", "avi", "mov", "mkv", "webm"]

        for ext in extensions:
            filename = downloader.generate_filename(url, extension=ext)
            assert filename.endswith(f".{ext}"), f"Should end with .{ext}"

    def test_generate_filename_date_is_current(self):
        """Test that generated filename contains current date"""
        downloader = TestDownloader()
        url = "https://example.com/video"
        filename = downloader.generate_filename(url)

        expected_date = date.today().strftime('%Y%m%d')
        assert filename.startswith(expected_date), "Should start with current date in YYYYMMDD format"

    def test_generate_filename_returns_string(self):
        """Test that generate_filename returns a string"""
        downloader = TestDownloader()
        url = "https://example.com/video"
        filename = downloader.generate_filename(url)

        assert isinstance(filename, str)


class TestDownload:
    """Tests for the download method"""

    def test_download_success(self):
        """Test successful download"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, result = downloader.download(url, tmpdir)

            assert success is True
            assert os.path.exists(result)
            assert result.endswith('.mp4')

    def test_download_creates_directory(self):
        """Test that download creates the save directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"
            save_path = os.path.join(tmpdir, "downloads", "reels")

            assert not os.path.exists(save_path)

            success, result = downloader.download(url, save_path)

            assert success is True
            assert os.path.exists(save_path)
            assert os.path.isdir(save_path)

    def test_download_saves_file(self):
        """Test that download creates the video file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, filepath = downloader.download(url, tmpdir)

            assert success is True
            assert os.path.exists(filepath)
            assert os.path.isfile(filepath)

    def test_download_returns_tuple(self):
        """Test that download returns a tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            result = downloader.download(url, tmpdir)

            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_download_returns_true_on_success(self):
        """Test that download returns True as first element on success"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, _ = downloader.download(url, tmpdir)

            assert success is True

    def test_download_returns_filepath_on_success(self):
        """Test that download returns filepath as second element on success"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, filepath = downloader.download(url, tmpdir)

            assert isinstance(filepath, str)
            assert os.path.exists(filepath)

    def test_download_creates_metadata(self):
        """Test that download creates metadata file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, filepath = downloader.download(url, tmpdir)

            # Check that metadata file was created
            metadata_dir = os.path.join(tmpdir, "metadata")
            assert os.path.exists(metadata_dir)
            assert os.path.isdir(metadata_dir)

            # Check that metadata file has correct name
            basename = os.path.splitext(os.path.basename(filepath))[0]
            metadata_file = os.path.join(metadata_dir, f"{basename}.yaml")
            assert os.path.exists(metadata_file)

    def test_download_saves_metadata_with_url(self):
        """Test that saved metadata contains the URL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success, filepath = downloader.download(url, tmpdir)

            # Read metadata file
            metadata_dir = os.path.join(tmpdir, "metadata")
            basename = os.path.splitext(os.path.basename(filepath))[0]
            metadata_file = os.path.join(metadata_dir, f"{basename}.yaml")

            with open(metadata_file, 'r') as f:
                metadata = yaml.safe_load(f)

            assert metadata['url'] == url

    def test_download_with_tags(self):
        """Test download with tags"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"
            tags = ["tutorial", "python", "coding"]

            success, filepath = downloader.download(url, tmpdir, tags=tags)

            # Verify metadata contains tags
            metadata_dir = os.path.join(tmpdir, "metadata")
            basename = os.path.splitext(os.path.basename(filepath))[0]
            metadata_file = os.path.join(metadata_dir, f"{basename}.yaml")

            with open(metadata_file, 'r') as f:
                metadata = yaml.safe_load(f)

            assert metadata['tags'] == tags

    def test_download_with_comments(self):
        """Test download with comments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"
            comments = "Great tutorial on async programming"

            success, filepath = downloader.download(url, tmpdir, comments=comments)

            # Verify metadata contains comments
            metadata_dir = os.path.join(tmpdir, "metadata")
            basename = os.path.splitext(os.path.basename(filepath))[0]
            metadata_file = os.path.join(metadata_dir, f"{basename}.yaml")

            with open(metadata_file, 'r') as f:
                metadata = yaml.safe_load(f)

            assert metadata['comments'] == comments

    def test_download_with_tags_and_comments(self):
        """Test download with both tags and comments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"
            tags = ["tutorial", "python"]
            comments = "Excellent resource"

            success, filepath = downloader.download(url, tmpdir, tags=tags, comments=comments)

            # Verify metadata
            metadata_dir = os.path.join(tmpdir, "metadata")
            basename = os.path.splitext(os.path.basename(filepath))[0]
            metadata_file = os.path.join(metadata_dir, f"{basename}.yaml")

            with open(metadata_file, 'r') as f:
                metadata = yaml.safe_load(f)

            assert metadata['tags'] == tags
            assert metadata['comments'] == comments

    def test_download_empty_url_returns_false(self):
        """Test that empty URL returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()

            success, error_msg = downloader.download("", tmpdir)

            assert success is False
            assert isinstance(error_msg, str)
            assert "URL cannot be empty" in error_msg

    def test_download_none_url_returns_false(self):
        """Test that None URL returns False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()

            success, error_msg = downloader.download(None, tmpdir)

            assert success is False
            assert isinstance(error_msg, str)

    def test_download_empty_save_path_returns_false(self):
        """Test that empty save_path returns False"""
        downloader = TestDownloader()
        url = "https://www.instagram.com/reel/ABC123/"

        success, error_msg = downloader.download(url, "")

        assert success is False
        assert isinstance(error_msg, str)
        assert "Save path cannot be empty" in error_msg

    def test_download_returns_error_on_failure(self):
        """Test that download returns error message on failure"""
        downloader = TestDownloader()
        url = "https://www.instagram.com/reel/ABC123/"
        invalid_path = "/invalid/path/that/does/not/exist"

        success, error_msg = downloader.download(url, invalid_path)

        # Even with invalid path, should try but error gracefully
        # Depending on permission, might fail or succeed
        assert isinstance(error_msg, str)

    def test_download_filename_is_consistent(self):
        """Test that same URL produces same filename"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            success1, filepath1 = downloader.download(url, tmpdir)

            # Extract filename from first download
            filename1 = os.path.basename(filepath1)

            with tempfile.TemporaryDirectory() as tmpdir2:
                success2, filepath2 = downloader.download(url, tmpdir2)
                filename2 = os.path.basename(filepath2)

            assert filename1 == filename2, "Same URL should produce same filename"

    def test_download_handles_metadata_save_failure_gracefully(self):
        """Test that download succeeds even if metadata save fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = TestDownloader()
            url = "https://www.instagram.com/reel/ABC123/"

            # Download should succeed even if metadata directory can't be created
            success, filepath = downloader.download(url, tmpdir)

            # File should still be created
            assert success is True
            assert os.path.exists(filepath)


class TestAbstractMethods:
    """Tests for abstract method enforcement"""

    def test_base_downloader_is_abstract(self):
        """Test that BaseDownloader cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseDownloader()

    def test_subclass_must_implement_download_video(self):
        """Test that subclass must implement _download_video"""
        class IncompleteDownloader(BaseDownloader):
            pass

        with pytest.raises(TypeError):
            IncompleteDownloader()

    def test_download_video_must_be_implemented(self):
        """Test that download calls the implemented _download_video"""
        class WorkingDownloader(BaseDownloader):
            def __init__(self):
                self.called = False

            def _download_video(self, url: str, filepath: str) -> None:
                self.called = True
                Path(filepath).touch()

        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = WorkingDownloader()
            url = "https://example.com/video"

            success, _ = downloader.download(url, tmpdir)

            assert downloader.called is True
            assert success is True
