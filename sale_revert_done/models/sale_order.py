# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_revert_done(self):
        other = self.filtered(lambda o: o.state != 'done')
        if other:
            states = ', '.join(['%s: %s' % (o.name, o.state) for o in other])
            raise ValidationError(
                _('Order(s) are not in state "done" so they cannot be reset '
                  'from "done" back to "sale": %s') % states)
        self.write({'state': 'sale'})
