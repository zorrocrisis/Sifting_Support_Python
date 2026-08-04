"""
compression_algorithms.py
-----------
Compression algorithms to support compression-based hierarchical clustering and 
filtering.

Add more data compression algorithms here as needed. Each algorithm should have a function
that takes a string and returns the size of the compressed output in bytes.
"""

import zlib

def compress_with_algorithm(text: str,
                            algorithm: str = "deflate",
                            compress_factor: int = 9) -> int:
    algorithm = algorithm.lower()

    if algorithm == "deflate":
        return compress_deflate(text, compress_level=compress_factor)

    raise ValueError(f"Unsupported compression algorithm: {algorithm}")

def compress_deflate(text: str, compress_level: int = 9) -> int:
    """
    Compress a string using Deflate (zlib) and return the compressed size in bytes.

    Args:
        text (str): The input string to compress.
        compress_level (int): Compression level (0-9, 9 = best compression).

    Returns:
        int: Size of the compressed output in bytes.
    """
    # Encode text to bytes
    input_bytes = text.encode('utf-8')

    # Compress using zlib (Deflate)
    compressed_bytes = zlib.compress(input_bytes, level=compress_level)

    # Return size in bytes
    return len(compressed_bytes)
