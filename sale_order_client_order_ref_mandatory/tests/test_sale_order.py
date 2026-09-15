# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderClientOrderRef(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def test_client_order_ref_required(self):
        """No se puede crear un pedido sin client_order_ref."""
        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": self.partner.id,
                }
            )

    def test_client_order_ref_required_on_write(self):
        """Tampoco se puede vaciar el campo en un write() posterior."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "client_order_ref": "PO-INICIAL",
            }
        )
        with self.assertRaises(ValidationError):
            order.write({"client_order_ref": False})

    def test_client_order_ref_ok(self):
        """Con client_order_ref informado, se crea sin problemas."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "client_order_ref": "PO-12345",
            }
        )
        self.assertEqual(order.client_order_ref, "PO-12345")

    def test_client_order_ref_in_report(self):
        """El campo aparece en el informe (report_saleorder_document)."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "client_order_ref": "PO-98765",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        report = self.env.ref("sale.action_report_saleorder")

        html_content = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, order.ids
        )
        if isinstance(html_content, bytes):
            html_content = html_content.decode("utf-8")
        self.assertIn("PO-98765", html_content)
