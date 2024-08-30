# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        params = self._context.get('params')
        if params:
            if (params['model'] == 'sale.order' or params['model'] == 'account.move') and \
                (self._context.get('active_model') == 'sale.order'
                    or
                    not self._context.get('active_model')):
                updated_values['user_id'] = False

        res = super()._message_auto_subscribe_followers(updated_values, default_subtype_ids)
        return res
