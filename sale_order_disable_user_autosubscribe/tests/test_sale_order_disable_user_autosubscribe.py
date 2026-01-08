from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderDisableUserAutosubscribe(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "testuser",
                "email": "testuser@example.com",
            }
        )
        cls.partner = cls.user.partner_id
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "name": "SO001",
                "user_id": cls.user.id,
            }
        )

    def test_message_auto_subscribe_followers_removes_user(self):
        updated_values = {"user_id": self.user.id}
        default_subtype_ids = []
        followers = self.sale_order._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
        assert all(follower[0] != self.partner.id for follower in followers)
