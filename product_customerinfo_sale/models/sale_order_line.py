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

    @api.depends("product_id", "order_partner_id")
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

    def _get_product_display_name(self):
        """Show the customer product code instead of the internal reference."""
        self.ensure_one()
        # Without partner_id the core does not show vendor codes and names
        line = self.with_context(partner_id=False)
        if not line.product_customer_code:
            return super(SaleOrderLine, line)._get_product_display_name()
        product = line.product_id.with_context(display_default_code=False)
        return f"[{line.product_customer_code}] {product.display_name}"

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        # The invoice label uses the plain product name: keep the customer code
        if (
            self.product_customer_code
            and res.get("display_type") == "product"
            and "name" not in optional_values
        ):
            res["name"] = self.label
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Assign the mininum quantity if set."""
        res = super()._onchange_product_id()
        for line in self:
            if line.product_id:
                customerinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
                if customerinfo.min_qty:
                    line.product_uom_qty = customerinfo.min_qty
        return res

    def _get_product_price_context(self):
        # Include partner in the context to ensure correct computation
        # of the price based on product customerinfo.
        res = super()._get_product_price_context()
        if not self.order_id.partner_id:
            return res
        return dict(
            res,
            partner_id=self.order_id.partner_id.id,
        )
