from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestQuickBlanketSale(SavepointCase):
    @classmethod
    def _setUpBlanketSaleOrder(cls):
        cls.sbo = cls.env["sale.blanket.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
            }
        )
        with Form(cls.sbo, "sale_blanket_order.view_blanket_order_form") as sbo_form:
            sbo_form.partner_id = cls.partner
            sbo_form.validity_date = fields.Date.today()
        ctx = {
            "order_id": cls.sbo.id,
            "parent_id": cls.sbo.id,
            "parent_model": "sale.blanket.order",
        }
        cls.product_1 = cls.product_1.with_context(ctx)
        cls.product_2 = cls.product_2.with_context(ctx)
        cls.SaleBlanketOrderLine.create(
            {
                "order_id": cls.sbo.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.uom_dozen.id,
                "price_unit": cls.product_1.list_price,
            }
        )
        cls.SaleBlanketOrderLine.create(
            {
                "order_id": cls.sbo.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.uom_unit.id,
                "price_unit": cls.product_2.list_price,
            }
        )
        cls.product_1.qty_to_process = 5.0
        cls.product_2.qty_to_process = 6.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleBlanketOrderLine = cls.env["sale.blanket.order.line"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.pricelist = cls.env.ref("product.list0")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.user = cls.env.ref("base.user_demo")
        cls.user.write(
            {
                "groups_id": [
                    (4, cls.env.ref("sales_team.group_sale_salesman_all_leads").id)
                ]
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_8")
        cls.product_2 = cls.env.ref("product.product_product_11")
        cls._setUpBlanketSaleOrder()

    def test_quick_line_add(self):
        """
        set non-null quantity to any product with no PO line:
          -> a new PO line is created with that quantity
        """
        line_1, line_2 = self.sbo.line_ids
        self.assertAlmostEqual(line_1.original_uom_qty, 5.0)
        self.assertAlmostEqual(line_2.original_uom_qty, 6.0)

    def test_quick_line_update(self):
        """
        set non-null quantity to any product with an already existing PO line:
          -> same PO line is updated with that quantity
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        line_1, line_2 = self.sbo.line_ids
        self.assertAlmostEqual(line_1.original_uom_qty, 7.0)
        self.assertAlmostEqual(line_2.original_uom_qty, 13.0)

    def test_quick_line_delete(self):
        """
        set null quantity to any product with existing PO line:
          -> PO line is deleted
        """
        self.product_1.qty_to_process = 0.0
        self.product_2.qty_to_process = 0.0
        self.assertEqual(len(self.sbo.line_ids), 0)

    def test_open_quick_view(self):
        """
        Test that the "Add" button opens the right action
        """
        product_act_from_so = self.sbo.add_product()
        self.assertEqual(product_act_from_so["type"], "ir.actions.act_window")
        self.assertEqual(product_act_from_so["res_model"], "product.product")
        self.assertEqual(product_act_from_so["view_mode"], "tree")
        self.assertEqual(product_act_from_so["target"], "current")
        self.assertEqual(
            product_act_from_so["view_id"][0],
            self.env.ref("sale_quick.product_tree_view4sale").id,
        )
        self.assertEqual(product_act_from_so["context"]["parent_id"], self.sbo.id)

    def test_several_so_for_one_product(self):
        """
        Test that when we try to mass add a product that already has
        several lines with the same product we get a raise
        """
        # add default value for 'order_id' as field is defined as copy=False
        self.sbo.line_ids[0].copy({"order_id": self.sbo.id})

        with self.assertRaises(ValidationError):
            self.product_1.qty_to_process = 3.0

    def test_saler_can_edit_products(self):
        """
        While in the quick sale interface, a saler with no edit rights
        on product.product can still edit product.product quick quantities
        """
        sbo = self.env["sale.blanket.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        ctx = {
            "order_id": sbo.id,
            "parent_model": "sale.blanket.order",
            "quick_access_rights_sale": 1,
        }
        product = self.env.ref("product.product_product_8")
        with self.assertRaises(AccessError):
            product.with_user(self.user).write(
                {"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id}
            )
        product_in_quick_edit = product.with_context(ctx).with_user(self.user)
        product_in_quick_edit.write(
            {"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id}
        )
