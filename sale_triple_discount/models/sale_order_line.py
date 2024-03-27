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
        this method is called multiple times."""

        prev_values = dict()
        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line.update(
                {
                    "discount": line._get_final_discount(),
                    "discount2": 0.0,
                    "discount3": 0.0,
                }
            )
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values."""
        for line, prev_vals_dict in list(prev_values.items()):
            line.update(prev_vals_dict)

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env["account.tax"]._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            discount=self._get_final_discount(),
            price_subtotal=self.price_subtotal,
        )

    @api.depends("discount2", "discount3", "discounting_type")
    def _compute_untaxed_amount_to_invoice(self):
        to_recompute = self.filtered(lambda r: r.discount2 or r.discount3)
        res = super(
            SaleOrderLine, self - to_recompute
        )._compute_untaxed_amount_to_invoice()
        if to_recompute:
            to_recompute._compute_untaxed_amount_to_invoice_process()
        return res

    def _compute_untaxed_amount_to_invoice_process(self):
        """Total of remaining amount to invoice on the sale order line (taxes excl.) as
            total_sol - amount already invoiced
        where Total_sol depends on the invoice policy of the product.
        Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
        come only from the SO lines.
        """
        # Code copied from Odoo sale.order.line._compute_untaxed_amount_to_invoice
        #  in order to consider triple discount fields (cf Adjustment comments)
        # FIXME: Module would need a refactor to use dedicated fields for triple discount
        #  so that sale.order.line.discount field can be used to aggregate the triple discount
        #  fields as suggested in https://github.com/odoo/odoo/pull/145513#pullrequestreview-1774865804  # noqa
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ["sale", "done"]:
                # Note: do not use price_subtotal field as it returns zero when
                # the ordered quantity is zero. It causes problem for expense
                # line (e.i.: ordered qty = 0, deli qty = 4, price_unit = 20 ;
                # subtotal is zero), but when you can invoice the line,
                # you see an amount and not zero. Since we compute untaxed
                # amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                uom_qty_to_consider = (
                    line.qty_delivered
                    if line.product_id.invoice_policy == "delivery"
                    else line.product_uom_qty
                )

                # Adjustment: Get the discount from line._get_final_discount()
                # instead of line.discount
                price_reduce = line.price_unit * (
                    1 - (line._get_final_discount() or 0.0) / 100.0
                )
                price_subtotal = price_reduce * uom_qty_to_consider
                if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                    # As included taxes are not excluded from the computed subtotal,
                    # `compute_all()` method has to be called to retrieve
                    # the subtotal without them.
                    # `price_reduce_taxexcl` cannot be used as it is computed
                    # from `price_subtotal` field. (see upper Note)
                    price_subtotal = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )["total_excluded"]
                inv_lines = line._get_invoice_lines()
                if any(
                    inv_lines.mapped(
                        lambda inv_l: inv_l.discount != line.discount
                        # Adjustment: Check discount2 and discount3 as well.
                        or inv_l.discount2 != line.discount2
                        or inv_l.discount3 != line.discount3
                    )
                ):
                    # In case of re-invoicing with different discount we try to
                    # calculate manually the remaining amount to invoice
                    amount = 0
                    for inv_line in inv_lines:
                        if (
                            len(
                                inv_line.tax_ids.filtered(lambda tax: tax.price_include)
                            )
                            > 0
                        ):
                            amount += inv_line.tax_ids.compute_all(
                                inv_line.currency_id._convert(
                                    inv_line.price_unit,
                                    line.currency_id,
                                    line.company_id,
                                    inv_line.date or fields.Date.today(),
                                    round=False,
                                )
                                * inv_line.quantity
                            )["total_excluded"]
                        else:
                            amount += (
                                inv_line.currency_id._convert(
                                    inv_line.price_unit,
                                    line.currency_id,
                                    line.company_id,
                                    inv_line.date or fields.Date.today(),
                                    round=False,
                                )
                                * inv_line.quantity
                            )

                    amount_to_invoice = max(price_subtotal - amount, 0)
                else:
                    amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice = amount_to_invoice
