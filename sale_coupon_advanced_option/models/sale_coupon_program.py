# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    # Add possibility to use discount only on first order of a customer
    first_order_only = fields.Boolean(
        string="Apply only first",
        default=False,
        help="Apply only on the first order of each client matching the conditions",
    )

    def _check_promo_code(self, order, coupon_code):
        if (
            self.first_order_only
            and len(
                self.env["sale.order"].search(
                    [("partner_id", "=", order.partner_id.id),("state","!=","cancel")]
                )
            )
            > 1
        ):
            return {"error": _("Coupon can be used only for the first sale order!")}
        else:
            return super()._check_promo_code(order,coupon_code)

    def _filter_programs_by_sale_order_count(self, order):
        if (
            self.env["sale.order"].search_count(
                [
                    ("partner_id", "=", order.partner_id.id),
                    ("state","!=", "cancel")
                ]
            )
            <= 1
        ):
            return self.filtered(lambda program: program.first_order_only is True)
        else:
            return self.filtered(lambda program: not program.first_order_only)

    @api.model
    def _filter_programs_from_common_rules(self, order, next_order=False):
        """ Return the programs if every conditions is met
            :param bool next_order: is the reward given from a previous order
        """
        programs = super()._filter_programs_from_common_rules(order, next_order)
        programs = programs and programs._filter_programs_by_sale_order_count(order)
        return programs
