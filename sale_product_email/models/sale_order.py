# Copyright 2022-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        self.send_sold_products_mail()
        return res

    def send_sold_products_mail(self):
        for order in self:
            for line in order.order_line:
                product_tmpl = line.product_id.product_tmpl_id
                mail_template = product_tmpl.sale_confirmation_mail_template_id
                if mail_template:
                    order.with_context(
                        product_tmpl=product_tmpl,
                        default_composition_mode="comment",
                        default_partner_ids=order.partner_id.ids,
                        custom_layout="sale.email_template_edi_sale",
                    ).message_post_with_template(mail_template.id)
