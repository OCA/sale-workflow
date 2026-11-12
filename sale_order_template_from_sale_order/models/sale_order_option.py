# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    quotation_template_fixed_price = fields.Boolean(copy=True)
    quotation_template_keep_name = fields.Boolean(copy=True)
    quotation_template_product_id = fields.Many2one(
        comodel_name="product.product",
        copy=True,
    )
    quotation_template_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        copy=True,
    )

    def _quotation_template_price_frozen(self):
        """Tell whether this option must keep the template price and discount.

        The freeze holds only while the product and the unit of measure are
        still the ones stored when the template was applied.

        :return: ``True`` when the pricelist must not recompute this option
        :rtype: bool
        """
        self.ensure_one()
        return (
            self.quotation_template_fixed_price
            and self.product_id == self.quotation_template_product_id
            and self.uom_id == self.quotation_template_uom_id
        )

    def _clear_quotation_template_freeze(self):
        """Drop the template freeze when the product or the UoM changed.

        Both markers are cleared together so a later change back to the
        original product uses the pricelist and the product description.

        :return: None
        """
        mismatched = self.filtered(
            lambda option: (
                option.quotation_template_fixed_price
                or option.quotation_template_keep_name
            )
            and (
                option.product_id != option.quotation_template_product_id
                or option.uom_id != option.quotation_template_uom_id
            )
        )
        if mismatched:
            mismatched.quotation_template_fixed_price = False
            mismatched.quotation_template_keep_name = False

    def _compute_name(self):
        """Keep the copied description while the product is still the snapshot.

        ``sale.order.option`` replaces the description from the product
        whenever ``product_id`` is set. A unit-of-measure change does not
        depend on this method. Parent dependencies stay as they are.

        :return: None
        :rtype: None
        """
        to_keep = self.browse()
        to_clear = self.browse()
        for option in self:
            if not option.quotation_template_keep_name:
                continue
            if option.product_id == option.quotation_template_product_id:
                to_keep += option
            else:
                to_clear += option
        to_clear._clear_quotation_template_freeze()
        return super(SaleOrderOption, self - to_keep)._compute_name()

    def _compute_price_unit(self):
        """Keep the template unit price while the option is still frozen.

        The core compute always rebuilds the price from a cached order line.
        A product or unit-of-measure change clears the freeze first. Update
        Prices passes ``pricelist_update`` and recomputes the price.

        :return: None
        :rtype: None
        """
        if self.env.context.get("pricelist_update"):
            return super()._compute_price_unit()
        self._clear_quotation_template_freeze()
        frozen = self.filtered(lambda option: option._quotation_template_price_frozen())
        return super(SaleOrderOption, self - frozen)._compute_price_unit()

    def _compute_discount(self):
        """Keep the template discount while the option is still frozen.

        The core compute always rebuilds the discount from a cached order
        line. Update Prices passes ``pricelist_update`` and recomputes it.

        :return: None
        :rtype: None
        """
        if self.env.context.get("pricelist_update"):
            return super()._compute_discount()
        self._clear_quotation_template_freeze()
        frozen = self.filtered(lambda option: option._quotation_template_price_frozen())
        return super(SaleOrderOption, self - frozen)._compute_discount()
