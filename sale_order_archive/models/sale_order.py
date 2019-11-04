# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    active = fields.Boolean(default=True)

    def toggle_active(self):
        if self.filtered(lambda so: so.state not in ["done", "cancel"] and so.active):
            raise UserError(_("Only 'Locked' or 'Canceled' orders can be archived"))
        return super(SaleOrder, self).toggle_active()
