# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_confirmation_mail_template_id = fields.Many2one(
        'mail.template',
        string=u'Sale confirmation email',
        domain=lambda self: [
            ('model_id', '=', self.env.ref('sale.model_sale_order').id),
        ],
        help=(u'If set, this email will be sent to the buyer on sale'
              u' confirmation'),
    )
