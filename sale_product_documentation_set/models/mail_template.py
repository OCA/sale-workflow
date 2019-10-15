# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import models


class MailTemplate(models.Model):

    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields=None):
        if self.model == 'sale.order':
            SaleOrder = self.env['sale.order']
            for res_id in res_ids:
                sale_order = SaleOrder.browse(res_id)
                docs = sale_order.mapped('product_doc_set_ids.attachment_ids')
            self.attachment_ids |= docs
        res = super(MailTemplate, self).generate_email(res_ids, fields)
        return res
