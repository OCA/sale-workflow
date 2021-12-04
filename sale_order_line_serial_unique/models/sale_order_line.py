# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    product_tracking = fields.Selection(
        related="product_id.tracking",
        store=True,
    )

    @api.constrains("product_uom_qty", "product_tracking")
    def _check_product_serial_unique(self):
        if any(
                float_compare(
                    line.product_uom_qty,
                    1.0,
                    precision_rounding=line.product_uom.rounding) != 0 for line in self
                if line.product_tracking == "serial"):
            raise ValidationError(
                _("You cannot sell more than one product quantity per line "
                  "if product is managed by serial number!"))
