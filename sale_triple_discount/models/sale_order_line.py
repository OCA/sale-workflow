# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
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

    @api.depends(
        "state",
        "price_reduce",
        "product_id",
        "untaxed_amount_invoiced",
        "qty_delivered",
        "product_uom_qty",
    )
    def _compute_untaxed_amount_to_invoice(self):
        """
        Compute the untaxed amount to invoice with triple discounting fields.
        """
        res = super()._compute_untaxed_amount_to_invoice()
        for line in self.filtered(lambda rec: rec.state in ["sale", "done"]):
            uom_qty_to_consider = (
                line.qty_delivered
                if line.product_id.invoice_policy == "delivery"
                else line.product_uom_qty
            )
            price_reduce = (
                line.price_unit
                * (1 - (line.discount or 0.0) / 100.0)
                * (1 - (line.discount2 or 0.0) / 100.0)
                * (1 - (line.discount3 or 0.0) / 100.0)
            )
            price_subtotal = price_reduce * uom_qty_to_consider

            if line.tax_id.filtered(lambda tax: tax.price_include):
                # Compute subtotal without included taxes
                price_subtotal = line.tax_id.compute_all(
                    price_reduce,
                    currency=line.order_id.currency_id,
                    quantity=uom_qty_to_consider,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )["total_excluded"]

            inv_lines = line._get_invoice_lines()
            if any(
                inv_line.discount != line.discount
                or inv_line.discount2 != line.discount2
                or inv_line.discount3 != line.discount3
                for inv_line in inv_lines
            ):
                # Re-invoicing with different discounts
                amount = sum(
                    inv_line.tax_ids.compute_all(
                        inv_line.currency_id._convert(
                            inv_line.price_unit,
                            line.currency_id,
                            line.company_id,
                            inv_line.date or fields.Date.today(),
                            round=False,
                        )
                        * inv_line.quantity
                    )["total_excluded"]
                    if inv_line.tax_ids.filtered(lambda tax: tax.price_include)
                    else inv_line.currency_id._convert(
                        inv_line.price_unit,
                        line.currency_id,
                        line.company_id,
                        inv_line.date or fields.Date.today(),
                        round=False,
                    )
                    * inv_line.quantity
                    for inv_line in inv_lines
                )
                amount_to_invoice = max(price_subtotal - amount, 0)
            else:
                amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice = amount_to_invoice
        return res

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
        return 100 - final_discount * 100

    def _discount_fields(self):
        return ["discount", "discount2", "discount3"]

    @api.depends("discount2", "discount3", "discounting_type")
    def _compute_amount(self):
        prev_values = self.triple_discount_preprocess()
        res = super()._compute_amount()
        self.triple_discount_postprocess(prev_values)
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
        res.update({"discount2": self.discount2, "discount3": self.discount3})
        return res

    def triple_discount_preprocess(self):
        """Prepare data for post processing.

        Save the values of the discounts in a dictionary,
        to be restored in postprocess.
        Resetting discount2 and discount3 to 0.0 avoids issues if
        this method is called multiple times.
        Updating the cache provides consistency through recomputations."""

        prev_values = dict()
        self.invalidate_cache(
            fnames=["discount", "discount2", "discount3"], ids=self.ids
        )
        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line._cache.update(
                {
                    "discount": line._get_final_discount(),
                    "discount2": 0.0,
                    "discount3": 0.0,
                }
            )
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values.

        Updating the cache provides consistency through recomputations."""

        self.invalidate_cache(
            fnames=["discount", "discount2", "discount3"],
            ids=[line.id for line in list(prev_values.keys())],
        )
        for line, prev_vals_dict in list(prev_values.items()):
            line._cache.update(prev_vals_dict)
