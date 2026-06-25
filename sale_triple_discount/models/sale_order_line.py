# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount2 = fields.Float(
        string="Disc. 2 (%)",
        digits="Discount",
        default=0.0,
    )
    discount3 = fields.Float(
        string="Disc. 3 (%)",
        digits="Discount",
        default=0.0,
    )
    discounting_type = fields.Selection(
        selection=[("additive", "Additive"), ("multiplicative", "Multiplicative")],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
        "or multiplicative.\nAdditive discounts are summed first and "
        "then applied.\nMultiplicative discounts are applied sequentially.\n"
        "Multiplicative discounts are default",
    )

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        if self.discounting_type == "multiplicative":
            return self._multiplicative_discount()
        error_msg = self.env._(
            "Sale order line %(name)s has unknown discounting type %(disc_type)s"
        )
        raise ValidationError(error_msg % {
            'name': self.name, 
            'disc_type': self.discounting_type
        })

    def _additive_discount(self):
        self.ensure_one()
        discount = sum(getattr(self, x, 0.0) or 0.0 for x in self._discount_fields())
        if discount <= 0:
            return 0
        if discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [
            1 - (getattr(self, x, 0.0) or 0.0) / 100 for x in self._discount_fields()
        ]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100

    # @api.model
    def _discount_fields(self):
        return ["discount", "discount2", "discount3"]

    @api.depends(
        "price_unit",
        "product_uom_qty",
        "discount",
        "discount2",
        "discount3",
        "discounting_type",
        "tax_ids",
    )
    def _compute_amount(self):
        res = super()._compute_amount()
        for line in self:
            final_discount = line._get_final_discount()
            price = line.price_unit * (1 - final_discount / 100.0)

            if line.tax_ids:
                taxes = line.tax_ids.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id
                    or line.order_id.partner_id,
                )
                line.price_subtotal = taxes["total_excluded"]
                line.price_tax = sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])
                )
                line.price_total = taxes["total_included"]
            else:
                line.price_subtotal = price * line.product_uom_qty
                line.price_tax = 0.0
                line.price_total = line.price_subtotal

        return res

    _sql_constraints = [
        (
            "discount2_limit",
            "CHECK (discount2 <= 100.0)",
            "Discount 2 must be lower or equal than 100%.",
        ),
        (
            "discount3_limit",
            "CHECK (discount3 <= 100.0)",
            "Discount 3 must be lower or equal than 100%.",
        ),
    ]

    def _prepare_invoice_line(self, **kwargs):
        res = super()._prepare_invoice_line(**kwargs)
        res.update(
            {
                "discount": self._get_final_discount(),
                "discount2": 0.0,
                "discount3": 0.0,
            }
        )
        return res

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(**kwargs)
        res["discount"] = self._get_final_discount()
        return res

    def _convert_to_tax_base_line_dict(self):
        """Fallback para compatibilidad con módulos de facturación legacy"""
        res = super()._convert_to_tax_base_line_dict()
        res["discount"] = self._get_final_discount()
        return res
