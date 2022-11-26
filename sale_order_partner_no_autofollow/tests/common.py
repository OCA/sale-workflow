from odoo.tests.common import TransactionCase


class NoAutofollowCommon(TransactionCase):
    def setUp(self, *args, **kwargs):
        """
        Test for orders, to check autofollow when the
        'customer no autofollow' mode is enabled in settings
        """
        super(NoAutofollowCommon, self).setUp(*args, **kwargs)

        self.partner1 = self.env["res.partner"].create(
            {"name": "Test1", "email": "test1@test.com"}
        )

        self.product1 = self.env["product.product"].create({"name": "desktop"})
