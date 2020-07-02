# © 2014-2016 Akretion (http://www.akretion.com)
# © 2020 Opener B.V. (https://opener.amsterdam)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.osv.expression import AND
from odoo import api, models


class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    @api.model
    def _validate_sale_orders(self, order_filter):
        """ Add a clause to exclude orders with exceptions, unless such
        a clause was already added in the configured filter. """
        if 'exception_ids' not in str(order_filter):
            order_filter = AND([
                order_filter,
                ['|', ('exception_ids', '=', False),
                 ('ignore_exception', '=', True)],
            ])
        return super(AutomaticWorkflowJob, self)._validate_sale_orders(
            order_filter)
