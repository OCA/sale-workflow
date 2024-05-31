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

    def _compute_name(self):
        """We need to override the method with product_id is set so that the product
        code is not added and add custom code of customerinfo."""
        empty_lines = self.filtered(lambda x: not x.product_id)
        super(SaleOrderLine, empty_lines)._compute_name()
        for item in self - empty_lines:
            customerinfo = item.product_id._select_customerinfo(
                partner=item.order_partner_id
            )
            if customerinfo.product_code:
                # Avoid to put the standard internal reference
                item = item.with_context(display_default_code=False)
            super(SaleOrderLine, item)._compute_name()
            if customerinfo.product_code:
                item.name = f"[{customerinfo.product_code}] {item.name}"
        return

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        """Assign the mininum quantity if set."""
        res = super()._onchange_product_id_warning()
        for line in self:
            if line.product_id:
                customerinfo = line.product_id._select_customerinfo(
                    partner=line.order_partner_id
                )
                if customerinfo.min_qty:
                    line.product_uom_qty = customerinfo.min_qty
        return res
