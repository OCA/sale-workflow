# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        string="Total discount",
        store=True,
        compute="_compute_discount_consolidated",
        compute_sudo=True,
        precompute=True,
        readonly=True,
    )
    discount1 = fields.Float(
        string="Disc. 1 (%)",
        digits="Discount",
        store=True,
        default=0.0,
        compute="_compute_discount",
        compute_sudo=True,
        precompute=True,
        readonly=False,
    )
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
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()
        else:
            raise ValidationError(
                _("Sale order line %(name)s has unknown discounting type %(dic_type)s")
                % {"name": self.name, "disc_type": self.discounting_type}
            )

    def _additive_discount(self):
        self.ensure_one()
        discount = sum(self[x] or 0.0 for x in self._discount_fields())
        if discount <= 0:
            return 0
        elif discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [1 - (self[x] or 0.0) / 100 for x in self._discount_fields()]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        result = 100 - final_discount * 100
        dp = self.env.ref("product.decimal_discount").precision_get("Discount")
        return round(result, dp)

    @api.model
    def _discount_fields(self):
        return ["discount1", "discount2", "discount3"]

    # Copy of Odoo function to change field being assigned from discount to discount1
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_discount(self):
        for line in self:
            if not line.product_id or line.display_type:
                line.discount1 = 0.0

            if not (
                line.order_id.pricelist_id
                and line.order_id.pricelist_id.discount_policy == 'without_discount'
            ):
                continue

            line.discount1 = 0.0

            if not line.pricelist_item_id:
                # No pricelist rule was found for the product
                # therefore, the pricelist didn't apply any discount/change
                # to the existing sales price.
                continue

            line.discount1 = line._calc_discount_from_pricelist()
        
    def _calc_discount_from_pricelist(self):
        self.ensure_one()
        line = self.with_company(self.company_id)
        pricelist_price = self._get_pricelist_price()
        base_price = self._get_pricelist_price_before_discount()

        if base_price != 0:  # Avoid division by zero
            discount = (base_price - pricelist_price) / base_price * 100
            if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                # only show negative discounts if price is negative
                # otherwise it's a surcharge which shouldn't be shown to the customer
                self.discount = discount

    @api.depends("discount1", "discount2", "discount3", "discounting_type")
    def _compute_discount_consolidated(self):
        for line in self:
            line.discount = line._get_final_discount()

    _sql_constraints = [
        (
            "discount1_limit",
            "CHECK (discount1 <= 100.0)",
            "Discount 1 must be lower or equal than 100%.",
        ),
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
        """
        Inherit this method to bring
        more discount fields to the invoice lines
        """
        res = super()._prepare_invoice_line(**kwargs)
        if self.discounting_type == "multiplicative":
            res.update(
                {
                    "discount1": self.discount1,
                    "discount2": self.discount2,
                    "discount3": self.discount3,
                }
            )
        else:
            res.update({"discount1": self.discount})
        return res
