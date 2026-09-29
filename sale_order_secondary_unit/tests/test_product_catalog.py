# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, HttpCase, tagged


@tagged("post_install", "-at_install")
class TestProductCatalog(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Units of measure, and so the secondary unit fields, shown on the line
        cls.env.user.groups_id += cls.env.ref("uom.group_uom")
        cls.partner = cls.env["res.partner"].create({"name": "Catalog partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Catalog product", "sale_ok": True}
        )
        cls.box = cls.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "name": "Box",
                "factor": 2.0,
                "uom_id": cls.product.uom_id.id,
            }
        )
        cls.pack = cls.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "name": "Pack",
                "factor": 5.0,
                "uom_id": cls.product.uom_id.id,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")

    def _catalog_set_quantity(self, quantity):
        """Set ``quantity`` on the product card of the catalog, as its +/-
        buttons and quantity input do."""
        self.make_jsonrpc_request(
            "/product/catalog/update_order_line_info",
            {
                "res_model": "sale.order",
                "order_id": self.order.id,
                "product_id": self.product.id,
                "quantity": quantity,
            },
        )

    def _catalog_quantity(self):
        """Quantity the product card of the catalog shows."""
        data = self.make_jsonrpc_request(
            "/product/catalog/order_lines_info",
            {
                "res_model": "sale.order",
                "order_id": self.order.id,
                "product_ids": self.product.ids,
            },
        )
        return data[str(self.product.id)]["quantity"]

    def _set_line_secondary_unit(self, secondary_uom, secondary_qty):
        with Form(self.order) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.secondary_uom_id = secondary_uom
                if secondary_uom:
                    line_form.secondary_uom_qty = secondary_qty

    def test_line_secondary_unit_without_product_default(self):
        """The product has no default sale secondary unit, so the catalog adds
        it in its unit of measure; once the secondary unit is set on the line,
        the card shows and changes the secondary quantity."""
        self._catalog_set_quantity(1)
        line = self.order.order_line
        self.assertFalse(line.secondary_uom_id)
        self.assertEqual(line.product_uom_qty, 1)
        self._set_line_secondary_unit(self.box, 3)
        self.assertEqual(line.product_uom_qty, 6)
        self.assertEqual(self._catalog_quantity(), 3)
        self._catalog_set_quantity(4)
        self.assertEqual(line.secondary_uom_id, self.box)
        self.assertEqual(line.secondary_uom_qty, 4)
        self.assertEqual(line.product_uom_qty, 8)
        self.assertEqual(self._catalog_quantity(), 4)

    def test_line_secondary_unit_other_than_product_default(self):
        """The line keeps its own secondary unit instead of taking the
        product default one."""
        self.product.sale_secondary_uom_id = self.box
        self._catalog_set_quantity(1)
        line = self.order.order_line
        self.assertEqual(line.secondary_uom_id, self.box)
        self._set_line_secondary_unit(self.pack, 2)
        self.assertEqual(line.product_uom_qty, 10)
        self.assertEqual(self._catalog_quantity(), 2)
        self._catalog_set_quantity(3)
        self.assertEqual(line.secondary_uom_id, self.pack)
        self.assertEqual(line.secondary_uom_qty, 3)
        self.assertEqual(line.product_uom_qty, 15)

    def test_line_without_secondary_unit_with_product_default(self):
        """Once the secondary unit is removed from the line, the card shows
        and changes its quantity in the line unit of measure."""
        self.product.sale_secondary_uom_id = self.box
        self._catalog_set_quantity(1)
        line = self.order.order_line
        self._set_line_secondary_unit(self.box.browse(), 0)
        self.assertEqual(self._catalog_quantity(), line.product_uom_qty)
        self._catalog_set_quantity(7)
        self.assertFalse(line.secondary_uom_id)
        self.assertEqual(line.product_uom_qty, 7)
