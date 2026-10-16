# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_update_prices_lines(self):
        """Keep template prices unless the user asked to update them.

        ``sale`` sets ``discount`` to 0 on the lines returned here and then
        recomputes it. Lines still frozen from a quotation template stay out
        of that set. Update Prices passes ``pricelist_update`` and must
        refresh them.

        :return: order lines whose price and discount may be recomputed
        :rtype: sale.order.line
        """
        lines = super()._get_update_prices_lines()
        if self.env.context.get("pricelist_update"):
            return lines
        return lines.filtered(lambda line: not line._quotation_template_price_frozen())

    def _recompute_prices(self):
        """Restore optional products that ``sale_management`` would reprice.

        That override sets ``discount`` to 0 on every optional product and
        recomputes it. Snapshot the ones still frozen by a template and put
        the numbers back. Update Prices (``pricelist_update``) refreshes them
        on purpose.

        :return: whatever ``super`` returns
        :rtype: None
        """
        restore = []
        if not self.env.context.get("pricelist_update"):
            frozen = self.sale_order_option_ids.filtered(
                lambda option: option._quotation_template_price_frozen()
            )
            restore = [
                (option, option.price_unit, option.discount) for option in frozen
            ]
        res = super()._recompute_prices()
        for option, price_unit, discount in restore:
            option.write({"price_unit": price_unit, "discount": discount})
        return res

    def _prepare_sale_order_template_vals(self, name):
        """Build create values for a quotation template taken from this order.

        Header fields such as notes, validity and payment terms are left
        unset so another module can add them by overriding this method.
        Down payment lines, combo products and combo component lines are
        skipped: a template cannot store them as independent lines.

        :param str name: template name entered by the user
        :return: ``sale.order.template`` create values
        :rtype: dict
        """
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: not line.is_downpayment
            and not line.combo_item_id
            and (not line.product_id or line.product_id.type != "combo")
        )
        return {
            "name": name,
            "company_id": self.company_id.id,
            "sale_order_template_line_ids": [
                Command.create(self._prepare_sale_order_template_line_vals(line))
                for line in lines
            ],
            "sale_order_template_option_ids": [
                Command.create(self._prepare_sale_order_template_option_vals(option))
                for option in self.sale_order_option_ids
            ],
        }

    def _prepare_sale_order_template_line_vals(self, line):
        """Build create values for one template line copied from an order line.

        Product lines store the unit price and discount and mark them as
        fixed, including when both numbers are zero. Section and note lines
        keep only the description. Every copied line keeps the description
        that was on the order.

        :param sale.order.line line: order line to copy
        :return: ``sale.order.template.line`` create values
        :rtype: dict
        """
        self.ensure_one()
        vals = {
            "display_type": line.display_type,
            "name": line.name,
            "sequence": line.sequence,
            "description_from_order": True,
        }
        if line.display_type:
            return vals
        vals.update(
            {
                "product_id": line.product_id.id,
                "product_uom_qty": line.product_uom_qty,
                "product_uom_id": line.product_uom.id,
                "price_unit": line.price_unit,
                "discount": line.discount,
                "manual_price": True,
            }
        )
        return vals

    def _prepare_sale_order_template_option_vals(self, option):
        """Build create values for one template option copied from an order.

        The unit price and discount are stored and marked as fixed, including
        when both numbers are zero. The description is the one from the order.
        Template options have no sequence; creation follows the order of the
        optional products.

        :param sale.order.option option: optional product to copy
        :return: ``sale.order.template.option`` create values
        :rtype: dict
        """
        self.ensure_one()
        return {
            "product_id": option.product_id.id,
            "name": option.name,
            "quantity": option.quantity,
            "uom_id": option.uom_id.id,
            "price_unit": option.price_unit,
            "discount": option.discount,
            "manual_price": True,
            "description_from_order": True,
        }
