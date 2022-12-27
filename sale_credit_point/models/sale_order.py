# Copyright 2018-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models, tools
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def credit_point_check(self, user=None):
        """Verify order amount against credit point budget."""
        # Introduced this check as from website sale_orders are created
        # from admin. If admin is in manage_credits group - all users will
        # bypass check. This way, we can check specific user from request
        if not user:
            user = self.env.user
        self.ensure_one()
        if not self.partner_id.with_user(user.id).credit_point_bypass_check():
            if self.amount_total > self.partner_id.credit_point:
                raise UserError(self.credit_point_check_failed_msg)

    @property
    def credit_point_check_failed_msg(self):
        msg = _(
            "Sale Order amount total ({amount}) is higher"
            " than your available credit ({points})."
        )
        return msg.format(amount=self.amount_total, points=self.partner_id.credit_point)

    @property
    def credit_point_decrease_msg(self):
        return _("SO %s") % self.name

    def action_confirm(self):
        """Check credit before confirmation, update credit if check passed."""
        install_module = tools.config.get("init")
        # At installation, odoo core demo data is calling  on SO.
        # It was leading to an error related to this module, as the demo
        # partner didn't had any credit point

        is_running = (
            not tools.config.get("test_enable")
            and "sale_credit_point" not in install_module
        )
        if is_running or self._context.get("test_sale_credit_point"):
            for sale in self:
                sale.credit_point_check()
                sale.partner_id.credit_point_decrease(
                    sale.amount_total, comment=self.credit_point_decrease_msg
                )
        return super().action_confirm()

    def action_cancel(self):
        for sale in self:
            if sale.state == "sale":
                sale.partner_id.credit_point_increase(
                    sale.amount_total, _("Sale Order canceled")
                )
        return super().action_cancel()
