# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare

PROCUREMENT_GROUP_KEY_PRIORITY = 32


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_discount_procurement_text(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_delivery_split_free_products.procurement_discount_text",
                "FREE",
            )
        )

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        if self._get_procurement_group_key()[0] == PROCUREMENT_GROUP_KEY_PRIORITY:
            precision = self.env["decimal.precision"].precision_get("Discount")
            if float_compare(self.discount, 100.0, precision_digits=precision) >= 0:
                vals["name"] += f"/{self._get_discount_procurement_text()}"
        return vals

    def _get_procurement_group_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        procurement groups
        """
        key = super()._get_procurement_group_key()
        # Check priority
        if key[0] < PROCUREMENT_GROUP_KEY_PRIORITY:
            precision = self.env["decimal.precision"].precision_get("Discount")
            if float_compare(self.discount, 100.0, precision_digits=precision) >= 0:
                return (
                    PROCUREMENT_GROUP_KEY_PRIORITY,
                    self._get_discount_procurement_text(),
                )
        return key

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        precision = self.env["decimal.precision"].precision_get("Discount")
        if float_compare(self.discount, 100.0, precision_digits=precision) >= 0:
            vals.update({"discount": self.discount})
        return vals
