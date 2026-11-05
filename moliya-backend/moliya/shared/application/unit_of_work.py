"""Bir nechta yozuvni bitta tranzaksiyada bajarish uchun port."""
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class UnitOfWork(ABC):
    @abstractmethod
    def atomic(self) -> AbstractContextManager:
        """Ichidagi barcha yozuvlar birga saqlanadi yoki birga bekor bo'ladi."""
