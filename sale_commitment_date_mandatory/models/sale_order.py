# © 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(
        required=True, default=fields.Datetime.now, copy=True
    )
