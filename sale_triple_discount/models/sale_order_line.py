# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

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

    @api.model
    def _discount_fields(self):
        return ["discount", "discount2", "discount3"]

    @api.depends("discount2", "discount3", "discounting_type")
    def _compute_amount(self):
        with self._aggregated_discount() as lines:
            res = super(SaleOrderLine, lines)._compute_amount()
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
        """
        Inherit this method to bring
        more discount fields to the invoice lines
        """
        res = super()._prepare_invoice_line(**kwargs)
        res.update({"discount2": self.discount2, "discount3": self.discount3})
        return res

    @contextmanager
    def _aggregated_discount(self):
        """A context manager to temporarily change the discount value on the
        records and restore it after the context is exited. It temporarily
        changes the discount value to the aggregated discount value so that
        methods that depend on the discount value will use the aggregated
        discount value instead of the original one.
        """
        discount_field = self._fields["discount"]
        # Protect discount field from triggering recompute of totals. We don't want
        # to invalidate the cache to avoid to flush the records to the database.
        # This is safe because we are going to restore the original value at the end
        # of the method.
        with self.env.protecting([discount_field], self):
            old_values = {}
            for line in self:
                old_values[line.id] = line.discount
                aggregated_discount = line._get_final_discount()
                line.update({"discount": aggregated_discount})
            yield self.with_context(discount_is_aggregated=True)
            for line in self:
                if line.id not in old_values:
                    continue
                line.with_context(
                    restoring_triple_discount=True,
                ).update({"discount": old_values[line.id]})

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        discount = (
            self.discount
            if self.env.context.get("discount_is_aggregated")
            else self._get_final_discount()
        )
        return self.env["account.tax"]._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            discount=discount,
            price_subtotal=self.price_subtotal,
        )
