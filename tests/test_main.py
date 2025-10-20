import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch
from PIL import Image

# Import functions from main.py
from main import setup_logging, create_directory, is_valid_url, generate_qr_code


def test_setup_logging():
    """Test that setup_logging configures logging correctly"""
    # Clear any existing logging configuration
    logging.getLogger().handlers.clear()

    # Call setup_logging
    setup_logging()

    # Check that a handler was added
    assert len(logging.getLogger().handlers) > 0

    # Check that the log level is INFO
    assert logging.getLogger().level == logging.INFO


def test_create_directory_success():
    """Test create_directory creates directory successfully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr_codes"

        # Directory should not exist initially
        assert not test_path.exists()

        # Create directory
        create_directory(test_path)

        # Directory should now exist
        assert test_path.exists()
        assert test_path.is_dir()


def test_create_directory_already_exists():
    """Test create_directory handles existing directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "existing_dir"
        test_path.mkdir()  # Create directory first

        # Should not raise exception
        create_directory(test_path)

        # Directory should still exist
        assert test_path.exists()
        assert test_path.is_dir()


def test_create_directory_nested():
    """Test create_directory creates nested directories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "nested" / "qr_codes"

        # Nested path should not exist initially
        assert not test_path.exists()
        assert not test_path.parent.exists()

        # Create nested directory
        create_directory(test_path)

        # Both parent and target should exist
        assert test_path.parent.exists()
        assert test_path.exists()
        assert test_path.is_dir()


def test_create_directory_exception():
    """Test create_directory handles exceptions gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            # Configure the mock to raise an exception
            mock_mkdir.side_effect = PermissionError("Permission denied")

            test_path = Path(temp_dir) / "qr_codes"

            # Capture logging output and expect SystemExit
            with pytest.raises(SystemExit) as excinfo:
                create_directory(test_path)

            # Ensure the function exits with code 1
            assert excinfo.value.code == 1


def test_is_valid_url_valid_urls():
    """Test is_valid_url with valid URLs"""
    valid_urls = [
        "https://github.com/JaMugen",
        "http://example.com",
        "https://www.google.com",
        "https://hub.docker.com/repository/docker/pitou500/module7_project/general",
    ]

    for url in valid_urls:
        assert is_valid_url(url), f"URL should be valid: {url}"


def test_is_valid_url_invalid_urls():
    """Test is_valid_url with invalid URLs"""
    invalid_urls = [
        "not_a_url",
        "github.com",  # Missing protocol
        "",  # Empty string
        "   ",  # Whitespace
        "http://",  # Incomplete
        "https://",  # Incomplete
    ]

    for url in invalid_urls:
        assert not is_valid_url(url), f"URL should be invalid: {url}"


def test_generate_qr_code_with_valid_url():
    """Test generate_qr_code creates QR code file with valid URL"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr.png"
        url = "https://github.com/JaMugen"

        # Generate QR code
        generate_qr_code(url, test_path, "black", "white")

        # File should be created
        assert test_path.exists()
        assert test_path.is_file()

        # File should be a valid image
        img = Image.open(test_path)
        assert img.format == "PNG"
        assert img.size[0] > 0 and img.size[1] > 0


def test_generate_qr_code_with_custom_colors():
    """Test generate_qr_code with custom colors"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr_custom.png"
        url = "https://example.com"

        # Generate QR code with custom colors
        generate_qr_code(url, test_path, "red", "yellow")

        # File should be created
        assert test_path.exists()
        assert test_path.is_file()

        # File should be a valid image
        img = Image.open(test_path)
        assert img.format == "PNG"


def test_generate_qr_code_with_invalid_url():
    """Test generate_qr_code does not create file with invalid URL"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr_invalid.png"
        invalid_url = "not_a_valid_url"

        # Generate QR code with invalid URL
        generate_qr_code(invalid_url, test_path)

        # File should not be created
        assert not test_path.exists()


@patch("main.Path.open")
def test_generate_qr_code_handles_file_error(mock_open):
    """Test generate_qr_code handles file write errors gracefully"""
    # Mock file open to raise an exception
    mock_open.side_effect = PermissionError("Permission denied")

    test_path = Path("/fake/path/test_qr.png")
    url = "https://github.com/JaMugen"

    # Should not raise exception, should handle gracefully
    try:
        generate_qr_code(url, test_path)
        # If we get here, the function handled the error gracefully
        assert True
    except Exception as e:
        pytest.fail(
            f"generate_qr_code should handle file errors gracefully, but raised: {e}"
        )


def test_generate_qr_code_default_colors():
    """Test generate_qr_code uses default colors when not specified"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr_default.png"
        url = "https://github.com/JaMugen"

        # Generate QR code with default colors (red fill, white background)
        generate_qr_code(url, test_path)

        # File should be created
        assert test_path.exists()
        assert test_path.is_file()


@patch("main.validators.url")
def test_is_valid_url_uses_validators_library(mock_validators):
    """Test that is_valid_url properly uses the validators library"""
    mock_validators.return_value = True

    result = is_valid_url("https://example.com")

    # Should call validators.url with the URL
    mock_validators.assert_called_once_with("https://example.com")
    assert result


def test_generate_qr_code_creates_proper_qr_structure():
    """Test that generated QR code has proper QR code structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test_qr_structure.png"
        url = "https://github.com/JaMugen"

        # Generate QR code
        generate_qr_code(url, test_path)

        # Load and verify it's a square image (QR codes are square)
        img = Image.open(test_path)
        width, height = img.size
        assert width == height, "QR code should be square"

        # QR code should have reasonable size (not too small)
        assert width >= 50, "QR code should be reasonably sized"


# Tests for main function
@patch("main.generate_qr_code")
@patch("main.create_directory")
@patch("main.setup_logging")
def test_main_with_default_url(
    mock_setup_logging, mock_create_directory, mock_generate_qr_code
):
    """Test main function with default URL"""
    with patch("sys.argv", ["main.py"]):
        from main import main

        # Call main function
        main()

        # Verify that required functions were called
        mock_setup_logging.assert_called_once()
        mock_create_directory.assert_called_once()
        mock_generate_qr_code.assert_called_once()

        # Check that generate_qr_code was called with default URL
        args, kwargs = mock_generate_qr_code.call_args
        assert args[0] == "https://github.com/JaMugen"


@patch("main.generate_qr_code")
@patch("main.create_directory")
@patch("main.setup_logging")
def test_main_with_custom_url(
    mock_setup_logging, mock_create_directory, mock_generate_qr_code
):
    """Test main function with custom URL"""
    test_url = "https://example.com"
    with patch("sys.argv", ["main.py", "--url", test_url]):
        from main import main

        # Call main function
        main()

        # Verify that required functions were called
        mock_setup_logging.assert_called_once()
        mock_create_directory.assert_called_once()
        mock_generate_qr_code.assert_called_once()

        # Check that generate_qr_code was called with custom URL
        args, kwargs = mock_generate_qr_code.call_args
        assert args[0] == test_url


@patch("main.datetime")
@patch("main.generate_qr_code")
@patch("main.create_directory")
@patch("main.setup_logging")
def test_main_creates_timestamped_filename(
    mock_setup_logging, mock_create_directory, mock_generate_qr_code, mock_datetime
):
    """Test that main function creates a timestamped filename"""
    # Mock datetime to return a fixed time
    mock_datetime.now.return_value.strftime.return_value = "20231016123456"

    with patch("sys.argv", ["main.py"]):
        from main import main

        # Call main function
        main()

        # Check that generate_qr_code was called with correct timestamped filename
        args, kwargs = mock_generate_qr_code.call_args
        path_arg = args[1]  # Second argument is the path
        assert "QRCode_20231016123456.png" in str(path_arg)


@patch("main.generate_qr_code")
@patch("main.create_directory")
@patch("main.setup_logging")
def test_main_uses_environment_variables(
    mock_setup_logging, mock_create_directory, mock_generate_qr_code
):
    """Test that main function uses environment variables for colors"""
    with patch("sys.argv", ["main.py"]):
        from main import main

        # Call main function
        main()

        # Check that generate_qr_code was called with color arguments
        args, kwargs = mock_generate_qr_code.call_args
        # args should be: (url, path, fill_color, back_color)
        assert len(args) >= 4
        # The colors come from FILL_COLOR and BACK_COLOR environment variables


@patch("main.Path.cwd")
@patch("main.generate_qr_code")
@patch("main.create_directory")
@patch("main.setup_logging")
def test_main_uses_correct_directory_path(
    mock_setup_logging, mock_create_directory, mock_generate_qr_code, mock_cwd
):
    """Test that main function uses correct directory path"""
    mock_cwd.return_value = Path("/test/current/dir")

    with patch("sys.argv", ["main.py"]):
        from main import main

        # Call main function
        main()

        # Check that create_directory was called with correct path
        create_dir_args = mock_create_directory.call_args[0]
        expected_path = Path("/test/current/dir") / "qr_codes"
        assert create_dir_args[0] == expected_path

        # Check that generate_qr_code was called with path in correct directory
        gen_qr_args = mock_generate_qr_code.call_args[0]
        path_arg = gen_qr_args[1]
        assert str(expected_path) in str(path_arg)
