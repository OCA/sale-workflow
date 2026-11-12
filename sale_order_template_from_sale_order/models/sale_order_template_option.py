# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderTemplateOption(models.Model):
    _inherit = "sale.order.template.option"

    price_unit = fields.Float(
        string="Unit Price",
        min_display_digits="Product Price",
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
    )
    manual_price = fields.Boolean(
        string="Fixed Price",
        default=False,
        help="Apply this unit price and discount instead of the pricelist.",
    )
    description_from_order = fields.Boolean(
        default=False,
        help="Keep the description copied from the sales order when the "
        "template is applied.",
    )

    def write(self, vals):
        """Block moving an option onto a template the salesman did not create.

        The record rule checks the option's current template, not the
        template written in ``sale_order_template_id``.

        :param dict vals: values to write
        :raise AccessError: ``sale_order_template_id`` points at someone
            else's template
        :return: ``True`` when the write succeeds
        :rtype: bool
        """
        template_id = vals.get("sale_order_template_id")
        if template_id:
            self.env["sale.order.template"].browse(
                template_id
            )._check_salesman_can_modify()
        return super().write(vals)

    @api.onchange("price_unit", "discount")
    def _onchange_price_unit(self):
        """Mark the price as fixed when the user edits it on the template.

        The flag is not derived from the number. Zero is a real price, and
        the user can clear Fixed Price to use the pricelist again.

        :return: None
        """
        self.manual_price = True

    def _prepare_option_line_values(self):
        """Pass the stored price and the copied description to the option.

        ``manual_price`` is the only signal that the stored numbers must be
        applied. Without it, the option is priced from the pricelist.

        :return: ``sale.order.option`` create values
        :rtype: dict
        """
        self.ensure_one()
        vals = super()._prepare_option_line_values()
        if self.description_from_order or self.manual_price:
            vals["quotation_template_product_id"] = self.product_id.id
            vals["quotation_template_uom_id"] = self.uom_id.id
        if self.description_from_order:
            vals["name"] = self.name
            vals["quotation_template_keep_name"] = True
        if self.manual_price:
            vals.update(
                {
                    "price_unit": self.price_unit,
                    "discount": self.discount,
                    "quotation_template_fixed_price": True,
                }
            )
        return vals
