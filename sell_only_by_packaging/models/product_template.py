# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sell_only_by_packaging = fields.Boolean(
        string="Only sell by packaging",
        company_dependent=True,
        default=False,
        help="Restrict the usage of this product on sale order lines to its "
        "packaging units",
        copy=False,
    )

    min_sellable_qty = fields.Float(
        compute="_compute_min_sellable_qty",
        help=(
            "Minimum sellable quantity, expressed in the product unit, according "
            "to the available packaging units, if Only Sell by Packaging is set."
        ),
    )

    @api.depends(
        "sell_only_by_packaging",
        "uom_id",
        "uom_ids",
        "uom_ids.factor",
    )
    def _compute_min_sellable_qty(self):
        for record in self:
            packaging_uom = record._get_min_sellable_uom()
            record.min_sellable_qty = (
                packaging_uom._compute_quantity(1.0, record.uom_id)
                if packaging_uom
                else 0.0
            )

    def _get_min_sellable_uom(self):
        """Return the smallest packaging unit this product can be sold by.

        Packaging units are the additional units of measure set on the product
        (``uom_ids``), which replaced the ``product.packaging`` records removed
        from Odoo in 19.0. Units that cannot be converted to the product unit
        are ignored, as they could not be used on a sale order line anyway.

        :return: a ``uom.uom`` recordset, empty if the product is not sold only
            by packaging or has no usable packaging unit.
        """
        self.ensure_one()
        if not self.sell_only_by_packaging or not self.uom_id:
            return self.env["uom.uom"].browse()
        sellable_uoms = self.uom_ids.filtered(
            lambda uom: uom._has_common_reference(self.uom_id)
        )
        return sellable_uoms.sorted(lambda uom: uom.factor)[:1]

    @api.constrains("sell_only_by_packaging", "sale_ok")
    def _check_sell_only_by_packaging_sale_ok(self):
        for product in self:
            if product.sell_only_by_packaging and not product.sale_ok:
                raise ValidationError(
                    self.env._(
                        "Product %s cannot be defined to be sold only by "
                        "packaging if it cannot be sold.",
                        product.name,
                    ),
                )

    @api.constrains("sell_only_by_packaging", "uom_id", "uom_ids")
    def _check_sell_only_by_packaging_uom_ids(self):
        for product in self:
            if product.sell_only_by_packaging and not product._get_min_sellable_uom():
                raise ValidationError(
                    self.env._(
                        "Product %s cannot be defined to be sold only by "
                        "packaging if it does not have any packaging unit "
                        "defined.",
                        product.name,
                    ),
                )

    @api.depends("sale_ok")
    def _compute_expense_policy(self):
        self.filtered(
            lambda t: not t.sale_ok and t.sell_only_by_packaging
        ).sell_only_by_packaging = False
        return super()._compute_expense_policy()
