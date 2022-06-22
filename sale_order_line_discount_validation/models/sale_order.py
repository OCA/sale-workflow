# Copyright (c) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approver_user_id = fields.Many2one(
        string="Approved By", comodel_name="res.users", tracking=1
    )
    approve_date = fields.Date(string="Approved On", tracking=1)
    state = fields.Selection(
        selection_add=[
            ("waiting_approval", "Waiting Approval"),
            ("approved", "Approved"),
        ]
    )

    def _get_message_body(self, is_confirm=None, is_refuse=None, is_approve=None):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        so_url = """<a href="{}/web#model=sale.order&id={}"
                class="o_mail_redirect" data-oe-id="{}"
                data-oe-model="sale.order" target="_blank">{}</a>
                """.format(
            base_url, self.id, self.id, self.name
        )
        html_body = ""
        if is_confirm:
            html_body = """
                    <p>Hello,</p>
                    <p>Quotation {} is ready for your approval.</p>
                """.format(
                so_url
            )
        elif is_refuse:
            html_body = """<![CDATA[]]>
                    <p>Hello,</p>
                    <p>Quotation {} is refused.</p>
                """.format(
                so_url
            )
        elif is_approve:
            html_body = """<![CDATA[]]>
                    <p>Hello,</p>
                    <p>Quotation {} is approved.</p>
                """.format(
                so_url
            )

        self.message_post(author_id=self.env.user.partner_id.id, body=html_body)
        return html_body

    def _request_approval(self):
        self.state = "waiting_approval"
        mail_users = self.env.ref("sales_team.group_sale_manager").users
        template = self.env.ref(
            "sale_order_line_discount_validation.email_template_request_approval",
            False,
        )
        msg_body = self._get_message_body(is_confirm=True)
        template.write(
            {
                "subject": "Sales Order: Request Approval",
                "body_html": msg_body,
                "email_from": self.user_id and self.user_id.email,
                "email_to": ",".join([mail.email for mail in mail_users if mail.email]),
            }
        )
        return template.send_mail(self.id, force_send=True)

    def action_quotation_send(self):
        if (
            self.order_line.filtered(
                lambda r: r.discount >= self.env.company.sale_discount_limit
            )
            and self.state != "approved"
        ):
            return self._request_approval()
        else:
            return super().action_quotation_send()

    def action_confirm(self):
        if (
            self.order_line.filtered(
                lambda r: r.discount >= self.env.company.sale_discount_limit
            )
            and self.state != "approved"
        ):
            return self._request_approval()
        else:
            return super(SaleOrder, self).action_confirm()

    def action_approve(self):
        for rec in self:
            if self.env.user.has_group("sales_team.group_sale_manager") and rec.user_id:
                rec.state = "approved"
                template = self.env.ref(
                    "sale_order_line_discount_validation.email_template_request_approval",
                    False,
                )

                msg_body = self._get_message_body(is_approve=True)
                template.write(
                    {
                        "subject": "Sales Order: Discount approved",
                        "body_html": msg_body,
                        "email_from": self.env.user.email,
                        "email_to": rec.user_id and rec.user_id.email,
                    }
                )
                template.send_mail(self.id, force_send=True)
                rec.write(
                    {
                        "approver_user_id": self.env.user.id,
                        "approve_date": fields.Date.today(),
                    }
                )
        return True

    def action_refuse(self):
        for rec in self:
            if self.env.user.has_group("sales_team.group_sale_manager") and rec.user_id:
                rec.write(
                    {"state": "draft", "approver_user_id": False, "approve_date": False}
                )
                template = self.env.ref(
                    "sale_order_line_discount_validation.email_template_request_approval",
                    False,
                )
                msg_body = self._get_message_body(is_refuse=True)
                template.write(
                    {
                        "subject": "Sales Order: Discount refused",
                        "body_html": msg_body,
                        "email_from": self.env.user.email,
                        "email_to": rec.user_id and rec.user_id.email,
                    }
                )
                template.send_mail(self.id, force_send=True)
        return True
