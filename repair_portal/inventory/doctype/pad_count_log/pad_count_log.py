from __future__ import annotations

import frappe
from frappe.model.document import Document
from matplotlib.pylab import TYPE_CHECKING


class PadCountLog(Document):
    pass
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
