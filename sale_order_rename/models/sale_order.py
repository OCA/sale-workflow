# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from psycopg2 import IntegrityError

from odoo import models, api, _, tools

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _name_company_uniq_constraint = 'name_company_uniq'
    _sql_constraints = [
        (
            _name_company_uniq_constraint,
            'unique(name, company_id)',
            'Sale Order name must be unique within a company!'
        ),
    ]

    @api.model
    def create(self, vals):
        is_name_generated = vals.get('name', _('New')) != _('New')
        duplicate_key_msg = 'duplicate key value violates unique constraint'
        while True:
            try:
                with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                    return super().create(vals.copy())
            except IntegrityError as e:
                e_msg = str(e)
                if is_name_generated or duplicate_key_msg not in e_msg or \
                        self._name_company_uniq_constraint not in e_msg:
                    raise e
                _logger.debug('Duplicate sale.order name, retrying creation')
