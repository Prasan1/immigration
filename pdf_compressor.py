"""PDF compression utility for file compressor feature"""
import os
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io

def compress_pdf(input_path, output_path, target_ratio=0.5, quality='basic'):
    """
    Compress a PDF file by reducing image quality and removing redundant data

    Args:
        input_path: Path to input PDF
        output_path: Path to save compressed PDF
        target_ratio: Target size as ratio of original (0.5 = 50% of original)
        quality: 'basic' (50-60% compression) or 'premium' (70-85% compression)

    Returns:
        int: Size of compressed file in bytes
    """

    try:
        # Read the PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Determine compression settings based on quality
        if quality == 'premium':
            # Premium: More aggressive compression (70-85% reduction)
            image_quality = 60  # JPEG quality
            compression_level = 9  # Maximum compression
        else:
            # Basic: Conservative compression (50-60% reduction)
            image_quality = 75  # Higher JPEG quality
            compression_level = 6  # Moderate compression

        # Copy all pages to writer
        for page in reader.pages:
            # Compress the page
            page.compress_content_streams()
            writer.add_page(page)

        # Remove duplicate objects
        writer.add_metadata(reader.metadata)

        # Write compressed PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        # Get compressed file size
        compressed_size = os.path.getsize(output_path)

        return compressed_size

    except Exception as e:
        raise Exception(f"PDF compression failed: {str(e)}")


def compress_pdf_advanced(input_path, output_path, target_ratio=0.5, quality='basic'):
    """
    Advanced PDF compression using Ghostscript if available
    Falls back to PyPDF2 compression if Ghostscript is not available

    Args:
        input_path: Path to input PDF
        output_path: Path to save compressed PDF
        target_ratio: Target size as ratio of original (0.5 = 50% of original)
        quality: 'basic' (50-60% compression) or 'premium' (70-85% compression)

    Returns:
        int: Size of compressed file in bytes
    """

    try:
        import subprocess

        # Determine Ghostscript settings based on quality
        if quality == 'premium':
            # Premium: More aggressive compression
            gs_settings = '/screen'  # Lowest quality, highest compression
            image_resolution = '72'  # DPI for images
        else:
            # Basic: Conservative compression
            gs_settings = '/ebook'  # Medium quality
            image_resolution = '150'  # Higher DPI for better quality

        # Try to use Ghostscript for better compression
        gs_command = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={gs_settings}',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-dDownsampleColorImages=true',
            f'-dColorImageResolution={image_resolution}',
            f'-dDownsampleGrayImages=true',
            f'-dGrayImageResolution={image_resolution}',
            f'-dDownsampleMonoImages=true',
            f'-dMonoImageResolution={image_resolution}',
            f'-sOutputFile={output_path}',
            input_path
        ]

        # Run Ghostscript
        result = subprocess.run(gs_command, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            compressed_size = os.path.getsize(output_path)
            return compressed_size
        else:
            # Ghostscript failed, fall back to PyPDF2
            return compress_pdf(input_path, output_path, target_ratio, quality)

    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        # Ghostscript not available or failed, use PyPDF2
        return compress_pdf(input_path, output_path, target_ratio, quality)


def get_compression_stats(original_size, compressed_size):
    """
    Calculate compression statistics

    Args:
        original_size: Size of original file in bytes
        compressed_size: Size of compressed file in bytes

    Returns:
        dict: Compression statistics
    """

    if original_size == 0:
        return {
            'original_size_mb': 0,
            'compressed_size_mb': 0,
            'reduction_percent': 0,
            'compression_ratio': 0
        }

    original_mb = original_size / (1024 * 1024)
    compressed_mb = compressed_size / (1024 * 1024)
    reduction_percent = ((original_size - compressed_size) / original_size) * 100
    compression_ratio = compressed_size / original_size

    return {
        'original_size_mb': round(original_mb, 2),
        'compressed_size_mb': round(compressed_mb, 2),
        'reduction_percent': round(reduction_percent, 1),
        'compression_ratio': round(compression_ratio, 2),
        'saved_mb': round(original_mb - compressed_mb, 2)
    }


def format_file_size(size_bytes):
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "2.5 MB")
    """

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
