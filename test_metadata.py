import pytest
import os
import tempfile
import shutil
import yaml
from pathlib import Path
from datetime import date
from metadata import create_metadata, save_metadata


class TestCreateMetadata:
    """Tests for the create_metadata function"""

    def test_create_metadata_minimal(self):
        """Test creating metadata with only URL"""
        url = "https://www.instagram.com/reel/ABC123/"
        metadata = create_metadata(url)

        assert metadata['url'] == url
        assert metadata['date'] == str(date.today())
        assert metadata['tags'] == []
        assert metadata['comments'] == ""

    def test_create_metadata_with_tags(self):
        """Test creating metadata with tags"""
        url = "https://www.instagram.com/reel/ABC123/"
        tags = ["tutorial", "python", "coding"]
        metadata = create_metadata(url, tags=tags)

        assert metadata['url'] == url
        assert metadata['tags'] == tags
        assert metadata['date'] == str(date.today())
        assert metadata['comments'] == ""

    def test_create_metadata_with_comments(self):
        """Test creating metadata with comments"""
        url = "https://www.instagram.com/reel/ABC123/"
        comments = "Great tutorial on async programming"
        metadata = create_metadata(url, comments=comments)

        assert metadata['url'] == url
        assert metadata['comments'] == comments
        assert metadata['date'] == str(date.today())

    def test_create_metadata_with_all_fields(self):
        """Test creating metadata with all fields"""
        url = "https://www.instagram.com/reel/ABC123/"
        tags = ["tutorial", "python"]
        comments = "Excellent resource"
        metadata = create_metadata(url, tags=tags, comments=comments)

        assert metadata['url'] == url
        assert metadata['tags'] == tags
        assert metadata['comments'] == comments
        assert metadata['date'] == str(date.today())

    def test_create_metadata_empty_url_raises_error(self):
        """Test that empty URL raises ValueError"""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            create_metadata("")

    def test_create_metadata_none_url_raises_error(self):
        """Test that None URL raises ValueError"""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            create_metadata(None)

    def test_create_metadata_whitespace_only_url(self):
        """Test that create_metadata rejects whitespace-only URLs"""
        with pytest.raises(ValueError):
            create_metadata("   ")

    def test_create_metadata_returns_dict(self):
        """Test that create_metadata returns a dictionary"""
        url = "https://www.instagram.com/reel/ABC123/"
        metadata = create_metadata(url)
        assert isinstance(metadata, dict)

    def test_create_metadata_date_format(self):
        """Test that date is in YYYY-MM-DD format"""
        url = "https://www.instagram.com/reel/ABC123/"
        metadata = create_metadata(url)
        date_str = metadata['date']
        # Should match YYYY-MM-DD format
        assert len(date_str) == 10
        assert date_str.count('-') == 2


class TestSaveMetadata:
    """Tests for the save_metadata function"""

    def test_save_metadata_creates_directory(self):
        """Test that save_metadata creates metadata directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"

            # Create a dummy video file
            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            # Check that metadata directory exists
            metadata_dir = os.path.join(tmpdir, "metadata")
            assert os.path.exists(metadata_dir)
            assert os.path.isdir(metadata_dir)

    def test_save_metadata_creates_yaml_file(self):
        """Test that save_metadata creates a YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"

            # Create a dummy video file
            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            assert os.path.exists(metadata_file)
            assert metadata_file.endswith('.yaml')

    def test_save_metadata_correct_filename(self):
        """Test that metadata file has correct name (based on video basename)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "my_video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"

            # Create a dummy video file
            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            # Should be metadata/my_video.yaml
            assert "my_video.yaml" in metadata_file
            assert "metadata" in metadata_file

    def test_save_metadata_yaml_content(self):
        """Test that saved YAML file has correct content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"
            tags = ["tutorial", "python"]
            comments = "Great content"

            # Create a dummy video file
            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url, tags=tags, comments=comments)

            # Read the YAML file and verify content
            with open(metadata_file, 'r') as f:
                loaded_metadata = yaml.safe_load(f)

            assert loaded_metadata['url'] == url
            assert loaded_metadata['tags'] == tags
            assert loaded_metadata['comments'] == comments
            assert loaded_metadata['date'] == str(date.today())

    def test_save_metadata_with_all_fields(self):
        """Test saving metadata with all fields populated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"
            tags = ["tutorial", "python", "coding"]
            comments = "Excellent resource for learning"

            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url, tags=tags, comments=comments)

            with open(metadata_file, 'r') as f:
                loaded_metadata = yaml.safe_load(f)

            assert loaded_metadata['url'] == url
            assert loaded_metadata['tags'] == tags
            assert loaded_metadata['comments'] == comments
            assert isinstance(loaded_metadata['date'], str)

    def test_save_metadata_returns_path_string(self):
        """Test that save_metadata returns a string path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"

            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            assert isinstance(metadata_file, str)

    def test_save_metadata_empty_filename_raises_error(self):
        """Test that empty filename raises ValueError"""
        with pytest.raises(ValueError, match="Filename cannot be empty"):
            save_metadata("", "https://example.com")

    def test_save_metadata_empty_url_raises_error(self):
        """Test that empty URL raises ValueError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            Path(video_path).touch()

            with pytest.raises(ValueError, match="URL cannot be empty"):
                save_metadata(video_path, "")

    def test_save_metadata_with_subdirectories(self):
        """Test saving metadata for video in subdirectory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "downloads", "reels")
            os.makedirs(subdir, exist_ok=True)

            video_path = os.path.join(subdir, "video.mp4")
            url = "https://www.instagram.com/reel/ABC123/"

            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            # Metadata should be in downloads/reels/metadata/
            expected_dir = os.path.join(subdir, "metadata")
            assert os.path.dirname(metadata_file) == expected_dir

    def test_save_metadata_with_multiple_extensions(self):
        """Test saving metadata for different video formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            formats = ["video.mp4", "clip.mov", "reel.avi", "content.webm"]

            for video_file in formats:
                video_path = os.path.join(tmpdir, video_file)
                url = f"https://example.com/{video_file}"

                Path(video_path).touch()

                metadata_file = save_metadata(video_path, url)

                # Verify file exists and has correct basename
                assert os.path.exists(metadata_file)
                basename = os.path.splitext(video_file)[0]
                assert f"{basename}.yaml" in metadata_file

    def test_save_metadata_overwrites_existing(self):
        """Test that save_metadata overwrites existing metadata file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            Path(video_path).touch()

            url1 = "https://example.com/video1"
            url2 = "https://example.com/video2"

            # Save metadata twice with different URLs
            metadata_file1 = save_metadata(video_path, url1)
            metadata_file2 = save_metadata(video_path, url2)

            # Should be the same file
            assert metadata_file1 == metadata_file2

            # Content should reflect the second URL
            with open(metadata_file2, 'r') as f:
                loaded_metadata = yaml.safe_load(f)

            assert loaded_metadata['url'] == url2

    def test_save_metadata_nested_metadata_directory(self):
        """Test that metadata directory is created in correct location"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "downloads", "video.mp4")
            os.makedirs(os.path.dirname(video_path), exist_ok=True)

            url = "https://example.com/video"

            Path(video_path).touch()

            metadata_file = save_metadata(video_path, url)

            # Metadata should be in the same directory as the video
            expected_metadata_dir = os.path.join(tmpdir, "downloads", "metadata")
            assert expected_metadata_dir in metadata_file
