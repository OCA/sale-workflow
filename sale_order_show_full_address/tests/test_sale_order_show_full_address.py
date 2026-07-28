# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from lxml import etree

from odoo.tests.common import TransactionCase, new_test_user
from odoo.tools.safe_eval import safe_eval


class TestSaleOrderShowFullAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="sale_order_show_full_address_user",
            groups="sales_team.group_sale_salesman,"
            "account.group_delivery_invoice_address",
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Address Test Partner",
                "street": "Test Street 1",
                "city": "Test City",
            }
        )

    def test_addresses_show_the_complete_address(self):
        """Both address fields must ask for the address in their context, and
        that context must render the address in the partner display name.
        """
        arch = etree.fromstring(
            self.env["sale.order"]
            .with_user(self.user)
            .get_view(self.env.ref("sale.view_order_form").id, "form")["arch"]
        )
        for field_name in ("partner_invoice_id", "partner_shipping_id"):
            nodes = arch.xpath(f"//field[@name='{field_name}']")
            self.assertTrue(nodes, f"{field_name} is not in the sale order form.")
            context = safe_eval(nodes[0].get("context") or "{}", {"partner_id": False})
            self.assertTrue(
                context.get("show_address"),
                f"{field_name} must show the address of the contact.",
            )
            self.assertIn(
                self.partner.street,
                self.partner.with_context(**context).display_name,
            )
