from odoo.tests import Form, tagged

from .common import NoAutofollowCommon


@tagged("post_install", "-at_install", "standart")
class TestSaleOrderNoAutofollow(NoAutofollowCommon):
    def setUp(self, *args, **kwargs):
        super(TestSaleOrderNoAutofollow, self).setUp(*args, **kwargs)

        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_partner_no_autofollow.partner_disable_autofollow", True
        )
        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.partner1.id}
        )
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            form.save()

    def test_partner_disable_autofollow(self):
        """
        'Customer no autofollow' mode is enabled in settings.
        Test whether the option to disable autofollow is enabled
        or disabled
        """
        self.assertEqual(
            self.sale_order_1._partner_disable_autofollow(),
            "True",
            "Must be equal to True",
        )

    def test_message_subscribe_1(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.sale_order_1.with_context(
            sale_partner_disable_autofollow=self.sale_order_1._partner_disable_autofollow()
        ).message_subscribe(partner_ids=[self.partner1.id])
        self.assertNotIn(
            self.sale_order_1.partner_id.id,
            self.sale_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_2(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.sale_order_1.with_context(
            sale_partner_disable_autofollow=self.sale_order_1._partner_disable_autofollow()
        ).message_subscribe(partner_ids=[])
        self.assertNotIn(
            self.sale_order_1.partner_id.id,
            self.sale_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_3(self):
        """'Customer no autofollow' mode is enabled in settings.
            Test whether the user will be added to the autofollow
        """
        self.sale_order_1.with_context(
            sale_partner_disable_autofollow=self.sale_order_1._partner_disable_autofollow()
        ).message_subscribe()
        self.assertNotIn(
            self.sale_order_1.partner_id.id,
            self.sale_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_sale_order_create(self):
        """
        'Customer no autofollow' mode is enabled in settings.
        Test if there is a client among subscribers when creating
        a record
        """
        self.assertNotIn(
            self.sale_order_1.partner_id.id,
            self.sale_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_sale_order_action_confirm(self):
        """
        'Customer no autofollow' mode is enabled in settings.
        Test if there is a customer among the subscribers
        after confirming the order.
        """
        self.sale_order_1.action_confirm()

        self.assertNotIn(
            self.sale_order_1.partner_id.id,
            self.sale_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )
