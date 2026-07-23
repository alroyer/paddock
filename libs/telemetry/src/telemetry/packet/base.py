from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from .header import PacketHeader

T = TypeVar("T", bound="BasePacket")


@dataclass(frozen=True)
class BasePacket(Generic[T]):
    header: PacketHeader

    @classmethod
    def parse(cls, header: PacketHeader, data: bytes) -> tuple[T, bytes]:
        raise NotImplementedError

    @staticmethod
    def _require_bytes(data: bytes, size: int) -> bytes:
        if len(data) < size:
            raise ValueError(f"buffer too small: need {size} bytes, got {len(data)}")
        return data

    @classmethod
    def _take_bytes(cls, data: bytes, size: int) -> tuple[bytes, bytes]:
        payload = cls._require_bytes(data, size)
        return payload[:size], payload[size:]

    @classmethod
    def _parse_items(
        cls, data: bytes, item_size: int, count: int, parser: Callable[[bytes], Any]
    ) -> tuple[list[Any], bytes]:
        payload = cls._require_bytes(data, item_size * count)
        items: list[Any] = []
        for _ in range(count):
            item_bytes, payload = cls._take_bytes(payload, item_size)
            items.append(parser(item_bytes))
        return items, payload
