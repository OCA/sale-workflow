# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
    )

    @api.depends("product_id")
    def _compute_product_customer_code(self):
        for line in self:
            if line.product_id:
                supplierinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
                code = supplierinfo.product_code
            else:
                code = ""
            line.product_customer_code = code

    def _update_description(self):
        """Add the customer code in the description when applicable.

        This also takes from context the possible customerinfo already searched in
        product_id_change for avoiding duplicated searches.
        """
        # We need to repeat the search here, as passing the value by context or any
        # other trick makes the ORM to do ugly things in "onchange" mode
        customerinfo = self.env["product.customerinfo"]
        if self.product_id:
            customerinfo = self.product_id._select_customerinfo(
                partner=self.order_partner_id
            )
            if customerinfo.product_code:
                # Avoid to put the standard internal reference
                self = self.with_context(display_default_code=False)
        res = super()._update_description()
        if customerinfo.product_code:
            self.name = f"[{customerinfo.product_code}] {self.name}"
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        """Inject the customerinfo in the context for not repeating the search in
        _update_description + assign the mininum quantity if set.
        """
        res = super().product_id_change()
        for line in self:
            if line.product_id:
                customerinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
                if customerinfo.min_qty:
                    line.product_uom_qty = customerinfo.min_qty
        return res
