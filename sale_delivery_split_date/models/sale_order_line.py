# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups
        """
        priority = 24
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] < priority:
            if self.commitment_date:
                # group by date instead of datetime
                return (priority, self.commitment_date.date())
        return key
