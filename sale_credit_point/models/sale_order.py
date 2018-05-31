# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo import tools


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def credit_point_check(self):
        """Verify order amount against credit point budget."""
        self.ensure_one()
        if not self.partner_id.credit_point_bypass_check():
            if self.amount_total > self.partner_id.credit_point:
                raise UserError(self.credit_point_check_failed_msg)

    @property
    def credit_point_check_failed_msg(self):
        return _(
            "Sale Order amount total (%s) "
            "is higher than your available credit (%s)."
        ) % (self.amount_total, self.partner_id.credit_point)

    @property
    def credit_point_decrease_msg(self):
        return _('SO %s') % self.name

    @api.multi
    def action_confirm(self):
        """Check credit before confirmation, update credit if check passed."""
        install_module = tools.config.get('init')
        # At installation, odoo core demo data is calling  on SO.
        # It was leading to an error related to this module, as the demo
        # partner didn't had any credit point

        if 'sale_credit_point' not in install_module:
            for sale in self:
                sale.credit_point_check()
                sale.partner_id.credit_point_decrease(
                    sale.amount_total, comment=self.credit_point_decrease_msg)
        return super().action_confirm()

    @api.multi
    def action_cancel(self):
        for sale in self:
            if sale.state == 'sale':
                sale.partner_id.credit_point_increase(
                    sale.amount_total, _("Sale Order canceled"))
                sale.partner_id.update_history(
                    sale.amount_total, "increase", _("Sale Order canceled"))
            super(SaleOrder, sale).action_cancel()
