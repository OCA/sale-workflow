# Copyright 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestQuickSale(SavepointCase):
    @classmethod
    def _setUpBasicSaleOrder(cls):
        cls.so = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        with Form(cls.so, "sale.view_order_form") as so_form:
            so_form.partner_id = cls.partner
        ctx = {"parent_id": cls.so.id, "parent_model": "sale.order"}
        cls.product_1 = cls.product_1.with_context(ctx)
        cls.product_2 = cls.product_2.with_context(ctx)
        cls.product_1.qty_to_process = 5.0
        cls.product_2.qty_to_process = 6.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.user = cls.env.ref("base.user_demo")
        # make demo user member of "Sales / User: All Documents" group
        cls.user.write(
            {
                "groups_id": [
                    (4, cls.env.ref("sales_team.group_sale_salesman_all_leads").id)
                ]
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_8")
        cls.product_2 = cls.env.ref("product.product_product_11")
        cls._setUpBasicSaleOrder()

    def test_quick_line_add_1(self):
        """
        set non-null quantity to any product with no PO line:
          -> a new PO line is created with that quantity
        """
        line_1, line_2 = self.so.order_line
        self.assertAlmostEqual(line_1.product_uom_qty, 5.0)
        self.assertAlmostEqual(line_2.product_uom_qty, 6.0)

    def test_quick_line_add_2(self):
        """
        same as previous, but include a different UoM as well
        We duplicate _setUpBasicSaleOrder except we ~simultaneously~
        write on qty_to_process as well as quick_uom_id
        (we want to make sure to test _inverse function when it is triggered twice)
        """
        so = self.env["sale.order"].create({"partner_id": self.partner.id})
        with Form(so, "sale.view_order_form") as so_form:
            so_form.partner_id = self.partner
        ctx = {"parent_id": so.id, "parent_model": "sale.order"}
        self.product_1 = self.product_1.with_context(ctx)
        self.product_2 = self.product_2.with_context(ctx)
        self.product_1.write({"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id})
        self.product_2.write({"qty_to_process": 6.0, "quick_uom_id": self.uom_dozen.id})

        line_1, line_2 = so.order_line
        self.assertAlmostEqual(line_1.product_uom_qty, 5.0)
        self.assertEqual(line_1.product_uom, self.uom_unit)

        self.assertAlmostEqual(line_2.product_uom_qty, 6.0)
        self.assertEqual(line_2.product_uom, self.uom_dozen)

    def test_quick_line_update_1(self):
        """
        set non-null quantity to any product with an already existing PO line:
          -> same PO line is updated with that quantity
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        line_1, line_2 = self.so.order_line
        self.assertAlmostEqual(line_1.product_uom_qty, 7.0)
        self.assertAlmostEqual(line_2.product_uom_qty, 13.0)

    def test_quick_line_update_2(self):
        """
        same as previous update only UoM in isolation, not qty
        """
        self.product_1.quick_uom_id = self.uom_dozen
        self.product_2.quick_uom_id = self.uom_unit
        line_1, line_2 = self.so.order_line

        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertAlmostEqual(line_1.product_uom_qty, 5.0)

        self.assertEqual(line_2.product_uom, self.uom_unit)
        self.assertAlmostEqual(line_2.product_uom_qty, 6.0)

    def test_quick_line_update_3(self):
        """
        same as previous 2 tests combined: we do simultaneous qty + uom updates
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        self.product_1.quick_uom_id = self.uom_dozen
        self.product_2.quick_uom_id = self.uom_unit

        line_1, line_2 = self.so.order_line
        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertEqual(line_2.product_uom, self.uom_unit)

        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertAlmostEqual(line_1.product_uom_qty, 7.0)

        self.assertEqual(line_2.product_uom, self.uom_unit)
        self.assertAlmostEqual(line_2.product_uom_qty, 13.0)

    def test_quick_line_delete(self):
        """
        set null quantity to any product with existing PO line:
          -> PO line is deleted
        """
        self.product_1.qty_to_process = 0.0
        self.product_2.qty_to_process = 0.0
        self.assertEqual(len(self.so.order_line), 0)

    def test_open_quick_view(self):
        """
        Test that the "Add" button opens the right action
        """
        product_act_from_so = self.so.add_product()
        self.assertEqual(product_act_from_so["type"], "ir.actions.act_window")
        self.assertEqual(product_act_from_so["res_model"], "product.product")
        self.assertEqual(product_act_from_so["view_mode"], "tree")
        self.assertEqual(product_act_from_so["target"], "current")
        self.assertEqual(
            product_act_from_so["view_id"][0],
            self.env.ref("sale_quick.product_tree_view4sale").id,
        )
        self.assertEqual(product_act_from_so["context"]["parent_id"], self.so.id)

    def test_several_so_for_one_product(self):
        """
        Test that when we try to mass add a product that already has
        several lines with the same product we get a raise
        """
        # add default value for 'order_id' as field is defined as copy=False
        self.so.order_line[0].copy({"order_id": self.so.id})

        with self.assertRaises(ValidationError):
            self.product_1.qty_to_process = 3.0

    def test_saler_can_edit_products(self):
        """
        While in the quick sale interface, a saler with no edit rights
        on product.product can still edit product.product quick quantities
        """
        so = self.env["sale.order"].create({"partner_id": self.partner.id})
        ctx = {
            "parent_id": so.id,
            "parent_model": "sale.order",
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
