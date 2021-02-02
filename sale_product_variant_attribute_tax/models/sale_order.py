# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_attribute_ids")
    def _onchange_product_attribute_ids_configurator(self):
        res = super()._onchange_product_attribute_ids_configurator()
        # if there's a product set, taxes on that product have priority
        if self.product_id or not self.product_tmpl_id:
            return res
        values = self.mapped("product_attribute_ids.value_id")
        taxes = values.mapped("tax_ids")
        # Filter taxes not belonging to the current company
        taxes = taxes.filtered(lambda x: x.company_id == self.order_id.company_id)
        fiscal_pos = self.order_id.fiscal_position_id
        # We can call this method although the fiscal position is not set
        taxes = fiscal_pos.map_tax(taxes)
        template_taxes = fiscal_pos.map_tax(self.product_tmpl_id.taxes_id)
        self.tax_id = template_taxes + taxes
        return res
