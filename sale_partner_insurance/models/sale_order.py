# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for record in self:
            partner_insurance = record.commercial_partner_id.coefficient_sale_insurance
            coefficient_sale_insurance = (
                partner_insurance
                if partner_insurance
                else record.company_id.coefficient_sale_insurance
            )
            insurance_product = record.company_id.insurance_product
            subtotal = sum(
                record.order_line.filtered(
                    lambda r: r.product_id != insurance_product
                ).mapped("price_subtotal")
            )
            if coefficient_sale_insurance and insurance_product:
                record.write(
                    {
                        "order_line": [
                            (
                                0,
                                0,
                                {
                                    "product_id": insurance_product.id,
                                    "product_uom_qty": 1,
                                    "price_unit": subtotal * coefficient_sale_insurance,
                                    "insurance_line": True,
                                },
                            )
                        ]
                    }
                )
        return super().action_confirm()

    def action_cancel(self):
        res = super().action_cancel()
        for record in self:
            insurance_product = record.company_id.insurance_product
            insurance_line = record.order_line.filtered(
                lambda r: r.product_id == insurance_product
            )
            if insurance_line:
                record.write({"order_line": [(3, insurance_line.id)]})
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    insurance_line = fields.Boolean()

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            insurance_product = record.company_id.insurance_product
            partner_insurance = (
                record.order_id.commercial_partner_id.coefficient_sale_insurance
            )
            coefficient_sale_insurance = (
                partner_insurance
                if partner_insurance
                else record.order_id.company_id.coefficient_sale_insurance
            )
            order_line_ids = record.order_id.order_line
            if record.product_id != insurance_product:
                insurance_line = order_line_ids.filtered(
                    lambda r: r.product_id == insurance_product
                )
                if insurance_line:
                    subtotal = sum(
                        order_line_ids.filtered(
                            lambda r: r.product_id != insurance_product
                        ).mapped("price_subtotal")
                    )
                    insurance_line.price_unit = subtotal * coefficient_sale_insurance
        return res
