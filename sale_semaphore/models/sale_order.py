# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOderLine(models.Model):
    _inherit = "sale.order"

    price_below_semaphore = fields.Boolean(compute="_compute_price_below_semaphore")

    def _compute_price_below_semaphore(self):
        self.price_below_semaphore = False
        for record in self:
            record.price_below_semaphore = any(
                record.order_line.mapped("price_below_semaphore")
            )

    def action_confirm(self):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        if not self.env.user.has_group("sales_team.group_sale_manager") and any(
            so.price_below_semaphore for so in self
        ):
            lines_price_below_pricelist = self.order_line.filtered(
                lambda line: line.price_below_semaphore
                and float_compare(
                    line.price_reduce_taxinc
                    if line.company_id.account_price_include == "tax_included"
                    else line.price_reduce_taxexcl,
                    line.order_id.pricelist_id._get_product_price(
                        line.product_id, line.product_uom_qty
                    ),
                    precision_digits=dp,
                )
                < 0
            )
            if lines_price_below_pricelist:
                raise UserError(
                    _(
                        "There's a line with price below semaphore's accepted.\n\n"
                        "Please set the prices in a way that they are accepted by the "
                        "semaphore, or contact the purchasing administrators."
                    )
                )
        return super().action_confirm()
