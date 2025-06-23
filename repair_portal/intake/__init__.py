# relative path: intake/__init__.py
# updated: 2025-06-20
# version: 1.2
# purpose: expose module-level helpers for Intake
# dev notes: adjusted for renamed OCR import

from .ocr import process_handwritten_intake

__all__ = ["process_handwritten_intake"]
