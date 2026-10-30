# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
        """Tell whether this line must keep the template price and discount.

        The freeze holds only while the product and the unit of measure are
        still the ones stored when the template was applied.

        :return: ``True`` when the pricelist must not recompute this line
        :rtype: bool
        """
        self.ensure_one()
        return (
            self.quotation_template_fixed_price
            and self.product_id == self.quotation_template_product_id
            and self.product_uom == self.quotation_template_uom_id
        )

    def _clear_quotation_template_freeze(self):
        """Drop the template freeze when the product or the UoM changed.

        Both markers are cleared together. Leaving either one set would make
        a later change back to the original product skip the computes and
        keep the other product's description, price and discount.

        The template writes ``price_unit`` without ``technical_price_unit``,
        so core treats that price as manual and a later unit-of-measure
        change would keep it. Aligning the two lets the pricelist compute
        run. The markers stay the freeze; this field is not.

        :return: None
        """
        mismatched = self.filtered(
            lambda line: (
                line.quotation_template_fixed_price or line.quotation_template_keep_name
            )
            and (
                line.product_id != line.quotation_template_product_id
                or line.product_uom != line.quotation_template_uom_id
            )
        )
        if mismatched:
            mismatched.quotation_template_fixed_price = False
            mismatched.quotation_template_keep_name = False
            for line in mismatched:
                line.technical_price_unit = line.price_unit

    def _compute_name(self):
        """Keep the order description while the product is still the snapshot.

        A unit-of-measure change does not depend on this method, so the
        description stays. A product change clears the freeze and uses the
        normal description. Parent dependencies are unchanged on purpose:
        ``product_uom`` must not recompute the name.

        :return: None
        :rtype: None
        """
        to_keep = self.browse()
        to_clear = self.browse()
        for line in self:
            if not line.quotation_template_keep_name:
                continue
            if line.product_id == line.quotation_template_product_id:
                to_keep += line
            else:
                to_clear += line
        to_clear._clear_quotation_template_freeze()
        return super(SaleOrderLine, self - to_keep)._compute_name()

    def _use_template_name(self):
        """Skip template descriptions after this line has left the freeze.

        ``sale_management`` copies the first template line of the same
        product. Once the product or the unit of measure no longer matches
        the snapshot, both markers are cleared and the description must come
        from the product. Using the template again would put another line's
        text here, and changing the product back would restore the template
        text. A line that is still frozen, or that only carries a fixed
        price, keeps the core behaviour.

        :return: whether the template line description replaces the name
        :rtype: bool
        """
        self.ensure_one()
        if (
            self.quotation_template_product_id
            and not self.quotation_template_keep_name
            and not self.quotation_template_fixed_price
        ):
            return False
        return super()._use_template_name()

    def _compute_price_unit(self):
        """Skip the pricelist while the template price is still frozen.

        A product or unit-of-measure change clears the freeze first, then
        the normal compute runs. Update Prices passes ``pricelist_update``
        and recomputes the price. In both cases ``technical_price_unit`` is
        aligned with ``price_unit`` first: the template price was stored
        without it, and core would otherwise keep that price as manual.

        :return: None
        :rtype: None
        """
        if self.env.context.get("pricelist_update"):
            for line in self.filtered("quotation_template_fixed_price"):
                line.technical_price_unit = line.price_unit
        else:
            self._clear_quotation_template_freeze()
        return super()._compute_price_unit()

    def _lines_without_price_recomputation(self):
        """Add template-frozen lines to the ones ``sale_management`` already skips.

        :return: lines whose unit price must stay as it is
        :rtype: sale.order.line
        """
        lines = super()._lines_without_price_recomputation()
        if self.env.context.get("pricelist_update"):
            return lines
        frozen = self.filtered(lambda line: line._quotation_template_price_frozen())
        return lines | frozen

    def _compute_discount(self):
        """Keep the template discount while the line is still frozen.

        ``_compute_discount`` has no manual-price guard of its own and would
        replace the discount with the pricelist one. Update Prices passes
        ``pricelist_update`` and recomputes it.

        :return: None
        :rtype: None
        """
        if self.env.context.get("pricelist_update"):
            return super()._compute_discount()
        self._clear_quotation_template_freeze()
        frozen = self.filtered(lambda line: line._quotation_template_price_frozen())
        return super(SaleOrderLine, self - frozen)._compute_discount()
