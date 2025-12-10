# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleRequirePODoc(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "test-custom"})
        cls.product = cls.env["product.product"].create({"name": "test-product"})

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom_id": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.company = cls.env.company

    def test_require_customer_need_po(self):
        self.partner.customer_need_po = True

        messsage = "You can not confirm sale order without Customer reference."
        with self.assertRaises(ValidationError, msg=messsage):
            self.sale.action_confirm()

    def test_require_sale_document_option(self):
        self.partner.sale_doc = True

        messsage = "You can not confirm sale order without Sale Documentation."
        with self.assertRaises(ValidationError, msg=messsage):
            self.sale.action_confirm()

    def test_confirm_successfully(self):
        self.partner.customer_need_po = True
        self.partner.sale_doc = True

        self.sale.client_order_ref = "Test"
        self.sale.sale_document_option = "done"

        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")

    def test_customer_need_po_default(self):
        self.company.customer_need_po_default = True
        partner = (
            self.env["res.partner"]
            .with_context(default_customer_rank=1)
            .create(
                {
                    "name": "Partner With PO Required",
                }
            )
        )
        self.assertTrue(partner.customer_need_po)
        self.company.customer_need_po_default = False
        partner = (
            self.env["res.partner"]
            .with_context(default_customer_rank=1)
            .create(
                {
                    "name": "Partner Without PO Required",
                }
            )
        )
        self.assertFalse(partner.customer_need_po)

    def test_customer_need_po_default_not_contact(self):
        self.company.customer_need_po_default = True
        partner = self.env["res.partner"].create(
            {
                "name": "Contact Without PO Required",
            }
        )
        self.assertFalse(partner.customer_need_po)
