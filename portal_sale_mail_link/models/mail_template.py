# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields=None):
        """We only want to inject the code for the standar sale template"""
        self.ensure_one()
        if self == self.env.ref("sale.email_template_edi_sale"):
            self_ctx = self.with_context(portal_sale_button=True)
            return super(
                MailTemplate, self_ctx).generate_email(res_ids, fields=fields)
        return super().generate_email(res_ids, fields=fields)

    @api.model
    def _get_sale_portal_html(self):
        """Mako code to inject the button"""
        return _("""
        % set quotation = object.state not in ('sale', 'done', 'cancel')
        % set require_signature = object.require_signature and quotation
        % set require_payment = object.require_payment and quotation
        % set pay_sign_name = (
            'Sign' if require_signature and not require_payment else (
                'Pay' if require_payment else 'View'))
        <div style="margin: 0px; padding: 0px;">
            <p/>
            <p>
                <a href="${object.get_portal_url()}"
                   style="
                    background-color: #875A7B;
                    padding: 8px 16px 8px 16px;
                    text-decoration: none;
                    color: #fff;
                    border-radius: 5px;
                    font-size:13px;"
                >${'{} {}'.format(pay_sign_name, object.name)}
                </a>
            </p>
        </div>
        """)

    @api.model
    def _render_template(
            self, template_txt, model, res_ids, post_process=False):
        """Renders the proper button for every sale order"""
        res = super()._render_template(
            template_txt, model, res_ids, post_process=post_process)
        if not self.env.context.get("portal_sale_button") or not post_process:
            return res
        for order in res.keys():
            template_txt = self._get_sale_portal_html()
            rendered_link = self.env["mail.template"]._render_template(
                template_txt, "sale.order", order, post_process=False)
            res[order] += rendered_link
        return res
