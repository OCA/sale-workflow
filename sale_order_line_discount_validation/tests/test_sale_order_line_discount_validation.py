from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderLineDiscountValidation(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineDiscountValidation, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.partner_model = self.env["res.partner"]

        self.partner = self.partner_model.create({"name": "Test partner"})
        self.sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
            }
        )

        sales_team_var = self.env.ref("sales_team.group_sale_manager")
        # sales_team_var.write({'users': [(4, self.env.uid)]})
        sales_team_var.write({"users": [(4, self.env.user.id)]})

    def test_get_message_body(self):

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        so_url = """<a href="{}/web#model=sale.order&id={}"
                class="o_mail_redirect" data-oe-id="{}"
                data-oe-model="sale.order" target="_blank">{}</a>
                """.format(
            base_url, self.sale_order.id, self.sale_order.id, self.sale_order.name
        )

        html_body1 = self.sale_order._get_message_body(True, None, None)
        self.assertEqual(
            html_body1,
            """
                    <p>Hello,</p>
                    <p>Quotation {} is ready for your approval.</p>
                """.format(
                so_url
            ),
            "Values do not match",
        )

        html_body2 = self.sale_order._get_message_body(None, True, None)
        self.assertEqual(
            html_body2,
            """<![CDATA[]]>
                    <p>Hello,</p>
                    <p>Quotation {} is refused.</p>
                """.format(
                so_url
            ),
            "Values do not match",
        )

        html_body3 = self.sale_order._get_message_body(None, None, True)
        self.assertEqual(
            html_body3,
            """<![CDATA[]]>
                    <p>Hello,</p>
                    <p>Quotation {} is approved.</p>
                """.format(
                so_url
            ),
            "Values do not match",
        )

    def test_request_approval(self):
        self.sale_order._request_approval()
        self.assertEqual(self.sale_order.state, "waiting_approval")

    def test_action_approve(self):
        self.sale_order.action_approve()
        for rec in self.sale_order:
            if self.env.user.has_group("sales_team.group_sale_manager") and rec.user_id:
                self.assertEqual(rec.state, "approved")
                self.assertEqual(rec.approver_user_id.id, self.env.user.id)
                self.assertEqual(rec.approve_date, fields.Date.today())

    def test_action_refuse(self):
        self.sale_order.action_refuse()
        for rec in self.sale_order:
            if self.env.user.has_group("sales_team.group_sale_manager") and rec.user_id:
                self.assertEqual(rec.state, "draft")
                self.assertEqual(rec.approver_user_id.id, False)
                self.assertEqual(rec.approve_date, False)
