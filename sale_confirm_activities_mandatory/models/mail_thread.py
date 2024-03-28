# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        # OVERRIDE to be able to skip followers subscribtion
        # when create several mail activities
        # otherwise mail_followers_res_partner_res_model_id_uniq is raised in test
        # it has no impact on standard flow till context key is used
        if self._context.get("mail_create_nosubscribe"):
            return True
        return super()._message_subscribe(partner_ids, subtype_ids, customer_ids)
