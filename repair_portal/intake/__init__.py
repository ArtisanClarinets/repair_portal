# relative path: intake/__init__.py
# updated: 2025-08-31
# version: 1.1
# purpose: expose module-level helpers for Intake
# dev notes: import OCR function for external access

from .ocr import import_handwritten_intake

__all__ = ["import_handwritten_intake"]
