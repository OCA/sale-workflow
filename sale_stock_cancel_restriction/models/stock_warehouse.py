# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

HELP_RESTRICT = """
    If set, will block cancellation of sale orders if any delivery is done.
    Otherwise, it will block cancellation when any transfer is done.
"""


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    restrict_sale_cancel_after_delivery = fields.Boolean(
        help=HELP_RESTRICT, default=False
    )
