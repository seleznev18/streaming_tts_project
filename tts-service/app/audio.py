from typing import Iterable


def chunk_pcm_bytes(pcm_bytes: bytes, chunk_size_bytes: int) -> Iterable[bytes]:
    """
    Разделить байты PCM на чанки фиксированного размера.
    """
    for i in range(0, len(pcm_bytes), chunk_size_bytes):
        yield pcm_bytes[i : i + chunk_size_bytes]
