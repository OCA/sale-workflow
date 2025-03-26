# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleRequirePODoc(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_6")

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
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )

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
