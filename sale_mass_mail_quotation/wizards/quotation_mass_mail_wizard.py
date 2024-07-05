# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class QuotationMassMailWizard(models.TransientModel):

    _name = "quotation.mass.mail.wizard"
    _description = "Quotation mass mail wizard"

    sale_order_ids = fields.Many2many("sale.order")
    mail_template_id = fields.Many2one(
        "mail.template",
        required=True,
        default=lambda s: s.env.ref("sale.email_template_edi_sale"),
    )

    def _finalize_composer(self, composer):
        """Hook to further customize your text, attachments, etc"""
        return composer

    def send_mass_mail(self):
        self.ensure_one()
        for sale_order in self.sale_order_ids:
            ctx = sale_order.with_context(
                mass_so_mail_template=self.mail_template_id
            ).action_quotation_send()["context"]
            composer = self.env["mail.compose.message"].with_context(**ctx).create({})
            composer.template_id = self.mail_template_id.id
            vals = composer._onchange_template_id(
                self.mail_template_id.id,
                ctx.get("composition_mode"),
                "sale.order",
                sale_order.id,
            )["value"]
            composer.write(vals)
            composer = self._finalize_composer(composer)
            composer.action_send_mail()
