# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def send_sold_products_mail(self):
        for order in self:
            for line in order.order_line:
                product_tmpl = line.product_id.product_tmpl_id
                mail_template = product_tmpl.sale_confirmation_mail_template_id
                if mail_template:
                    order.with_context(**{  # Preserve pre-existing context
                        'product_tmpl': product_tmpl,
                        'default_composition_mode': 'comment',
                        'default_partner_ids': order.partner_id.ids,
                        'custom_layout': ('sale.mail_template_data'
                                          '_notification_email_sale_order'),
                    }).message_post_with_template(mail_template.id)
