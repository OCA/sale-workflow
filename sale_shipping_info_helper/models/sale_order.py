# Copyright 2017-To Day Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shipping_amount_total = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Total shipping amount including taxes",
    )
    shipping_amount_untaxed = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Untaxed portion of the shipping amount",
    )
    shipping_amount_tax = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Tax portion of the shipping amount",
    )
    item_amount_total = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Total amount for items excluding shipping",
    )
    item_amount_untaxed = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Untaxed portion of the item amount",
    )
    item_amount_tax = fields.Float(
        compute="_compute_shipping",
        digits="Account",
        store=True,
        help="Tax portion of the item amount",
    )

    @api.depends("amount_total", "amount_untaxed")
    def _compute_shipping(self):
        for record in self:
            # Get delivery lines
            delivery_lines = record.order_line.filtered(lambda x: x._is_delivery())

            # Compute shipping amounts
            shipping_amount_untaxed = sum(delivery_lines.mapped("price_subtotal"))
            shipping_amount_total = sum(delivery_lines.mapped("price_total"))
            shipping_amount_tax = sum(delivery_lines.mapped("price_tax"))
            record.update(
                {
                    "shipping_amount_untaxed": shipping_amount_untaxed,
                    "shipping_amount_total": shipping_amount_total,
                    "shipping_amount_tax": shipping_amount_tax,
                }
            )
            for key in ["amount_total", "amount_untaxed", "amount_tax"]:
                record[f"item_{key}"] = record[key] - record[f"shipping_{key}"]
