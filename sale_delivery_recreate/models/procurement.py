# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name, origin,
            values):
        if self.env.context.get('delivery_create_only', False):
            values.setdefault(
                'company_id', self.env['res.company']._company_default_get(
                    'procurement.group'))
            values.setdefault('priority', '1')
            values.setdefault('date_planned', fields.Datetime.now())
            rule = self._get_rule(product_id, location_id, values)
            if rule:
                action = 'pull' if rule.action == 'pull_push' else rule.action
                if action == 'pull' and rule.picking_type_id.code == 'outgoing':
                    if hasattr(rule, '_run_%s' % action):
                        getattr(rule, '_run_%s' % action)(
                            product_id, product_qty, product_uom, location_id, name,
                            origin, values)
                    else:
                        _logger.error("The method _run_%s doesn't exist on the "
                                      "procument rules" % action)
            return True
        return super().run(
            product_id, product_qty, product_uom, location_id, name, origin, values)
