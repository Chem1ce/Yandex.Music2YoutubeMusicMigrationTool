from dataclasses import dataclass

@dataclass(frozen=True)
class Track:
    """Universal data structure for music tracks across different platforms."""
    __slots__ = ['artist', 'name', 'duration_ms']
    artist: str
    name: str
    duration_ms: int