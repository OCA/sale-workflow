# Copyright 2023 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            "price_unit": self.price_unit,
            "currency_id": self.order_id.currency_id,
            "product_qty": self.product_uom_qty,
            "product": self.product_id,
            "partner": self.order_id.partner_id,
        }

    @api.depends("qty_delivered", "price_unit")
    def _compute_subtotal_to_deliver(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            vals["product_qty"] = line.product_uom_qty - line.qty_delivered
            taxes = line.tax_id.compute_all(
                vals["price_unit"],
                vals["currency_id"],
                vals["product_qty"],
                vals["product"],
                vals["partner"],
            )
            line.update({"subtotal_to_deliver": taxes["total_excluded"]})

    @api.depends("qty_delivered", "price_unit")
    def _compute_subtotal_delivered(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            vals["product_qty"] = line.qty_delivered
            taxes = line.tax_id.compute_all(
                vals["price_unit"],
                vals["currency_id"],
                vals["product_qty"],
                vals["product"],
                vals["partner"],
            )
            line.update({"subtotal_delivered": taxes["total_excluded"]})

    subtotal_to_deliver = fields.Monetary(
        compute="_compute_subtotal_to_deliver",
        digits="Product Unit of Measure",
        copy=False,
        string="Subtotal to Deliver",
        store=True,
    )

    subtotal_delivered = fields.Monetary(
        compute="_compute_subtotal_delivered",
        digits="Product Unit of Measure",
        copy=False,
        string="Subtotal Delivered",
        store=True,
    )
