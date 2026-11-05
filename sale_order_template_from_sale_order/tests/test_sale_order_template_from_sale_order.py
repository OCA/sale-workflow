# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.fields import Command
from odoo.tests import Form
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderTemplateFromSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(cls.env.ref("sale.group_discount_per_so_line").id),
                    Command.link(
                        cls.env.ref("sale_management.group_sale_order_template").id
                    ),
                    Command.link(cls.env.ref("product.group_product_pricelist").id),
                    Command.link(cls.env.ref("uom.group_uom").id),
                    Command.link(
                        cls.env.ref(
                            "sale_order_template_from_sale_order."
                            "group_template_from_order"
                        ).id
                    ),
                ]
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product_a = cls.env["product.product"].create(
            {"name": "Template Product A", "list_price": 100.0, "type": "consu"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Template Product B", "list_price": 80.0, "type": "consu"}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Template percentage",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                        }
                    )
                ],
            }
        )

    def _create_template(self, order, name):
        """Create a template through the wizard and return it.

        :param sale.order order: source order
        :param str name: template name
        :return: created quotation template
        :rtype: sale.order.template
        """
        wizard = self.env["sale.order.create.template"].create(
            {"sale_order_id": order.id, "name": name}
        )
        wizard.action_create_template()
        return self.env["sale.order.template"].search([("name", "=", name)])

    def _pricelist_values(self, product, uom, qty=1.0):
        """Return the description, price and discount the pricelist would set.

        :param product.product product: product to price
        :param uom.uom uom: unit of measure
        :param float qty: quantity
        :return: name, unit price and discount
        :rtype: tuple
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": uom.id,
                            "product_uom_qty": qty,
                        }
                    )
                ],
            }
        )
        line = order.order_line
        return line.name, line.price_unit, line.discount

    def _apply_template(self, template):
        """Apply a template through the form onchange and save the quotation.

        :param sale.order.template template: template to apply
        :return: saved sales order
        :rtype: sale.order
        """
        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner
            order_form.pricelist_id = self.pricelist
            order_form.sale_order_template_id = template
        return order_form.record

    def _source_order(self):
        """Build a draft order with sections, products and an option.

        :return: sales order
        :rtype: sale.order
        """
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Section",
                            "sequence": 10,
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_note",
                            "name": "Note",
                            "sequence": 20,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Product A custom",
                            "sequence": 30,
                            "product_uom_qty": 2,
                            "product_uom": self.uom_unit.id,
                            "price_unit": 42.0,
                            "discount": 25.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_b.id,
                            "name": "Product B custom",
                            "sequence": 40,
                            "product_uom_qty": 3,
                            "product_uom": self.uom_dozen.id,
                            "price_unit": 17.0,
                            "discount": 5.0,
                        }
                    ),
                ],
                "sale_order_option_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Option custom",
                            "quantity": 4,
                            "uom_id": self.uom_unit.id,
                            "price_unit": 33.0,
                            "discount": 8.0,
                            "sequence": 10,
                        }
                    )
                ],
            }
        )

    def test_wizard_creates_template(self):
        order = self._source_order()
        before = (
            order.state,
            order.order_line.ids,
            order.order_line.mapped("price_unit"),
            order.order_line.mapped("discount"),
            order.order_line.mapped("name"),
            order.sale_order_option_ids.price_unit,
            order.sale_order_option_ids.discount,
            order.sale_order_option_ids.name,
        )
        wizard = self.env["sale.order.create.template"].create(
            {"sale_order_id": order.id, "name": "From quotation"}
        )
        action = wizard.action_create_template()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "success")
        self.assertEqual(
            action["params"]["message"], "Template From quotation is created"
        )
        self.assertEqual(
            action["params"]["next"], {"type": "ir.actions.act_window_close"}
        )
        template = self.env["sale.order.template"].search(
            [("name", "=", "From quotation")]
        )
        self.assertEqual(len(template), 1)
        self.assertEqual(template.company_id, order.company_id)
        lines = template.sale_order_template_line_ids
        self.assertEqual(
            lines.mapped("display_type"),
            ["line_section", "line_note", False, False],
        )
        self.assertEqual(
            lines.mapped("name"),
            ["Section", "Note", "Product A custom", "Product B custom"],
        )
        self.assertEqual(lines.mapped("sequence"), [10, 20, 30, 40])
        self.assertFalse(lines[0].product_id)
        self.assertFalse(lines[0].manual_price)
        self.assertTrue(lines[0].description_from_order)
        self.assertTrue(lines[1].description_from_order)
        self.assertEqual(lines[2].product_id, self.product_a)
        self.assertEqual(lines[2].product_uom_qty, 2)
        self.assertEqual(lines[2].product_uom_id, self.uom_unit)
        self.assertEqual(lines[2].price_unit, 42.0)
        self.assertEqual(lines[2].discount, 25.0)
        self.assertTrue(lines[2].manual_price)
        self.assertTrue(lines[2].description_from_order)
        self.assertEqual(lines[3].product_id, self.product_b)
        self.assertEqual(lines[3].product_uom_id, self.uom_dozen)
        self.assertEqual(lines[3].price_unit, 17.0)
        self.assertEqual(lines[3].discount, 5.0)
        self.assertTrue(lines[3].manual_price)
        option = template.sale_order_template_option_ids
        self.assertEqual(len(option), 1)
        self.assertEqual(option.product_id, self.product_a)
        self.assertEqual(option.name, "Option custom")
        self.assertEqual(option.quantity, 4)
        self.assertEqual(option.uom_id, self.uom_unit)
        self.assertEqual(option.price_unit, 33.0)
        self.assertEqual(option.discount, 8.0)
        self.assertTrue(option.manual_price)
        self.assertTrue(option.description_from_order)
        self.assertEqual(
            before,
            (
                order.state,
                order.order_line.ids,
                order.order_line.mapped("price_unit"),
                order.order_line.mapped("discount"),
                order.order_line.mapped("name"),
                order.sale_order_option_ids.price_unit,
                order.sale_order_option_ids.discount,
                order.sale_order_option_ids.name,
            ),
        )

    def test_create_template_every_state(self):
        for state in ("sent", "sale", "cancel", "locked"):
            order = self.env["sale.order"].create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product_a.id,
                                "price_unit": 42.0,
                                "discount": 25.0,
                            }
                        )
                    ],
                }
            )
            if state == "sent":
                order.action_quotation_sent()
            elif state == "sale":
                order.action_confirm()
            elif state == "cancel":
                order.action_confirm()
                order._action_cancel()
            else:
                order.action_confirm()
                order.action_lock()
                self.assertTrue(order.locked)
            template = self._create_template(order, f"Template {state}")
            self.assertEqual(len(template), 1)
            self.assertEqual(template.sale_order_template_line_ids.price_unit, 42.0)
            self.assertTrue(template.sale_order_template_line_ids.manual_price)
            self.assertEqual(order.order_line.price_unit, 42.0)

    def test_apply_restores_prices(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Product A extra",
                            "product_uom_qty": 2,
                            "product_uom": self.uom_unit.id,
                            "price_unit": 42.0,
                            "discount": 25.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_b.id,
                            "name": "Product B extra",
                            "product_uom_qty": 1,
                            "product_uom": self.uom_unit.id,
                            "price_unit": 17.0,
                            "discount": 5.0,
                        }
                    ),
                ],
                "sale_order_option_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Option extra",
                            "quantity": 1,
                            "uom_id": self.uom_unit.id,
                            "price_unit": 33.0,
                            "discount": 8.0,
                        }
                    )
                ],
            }
        )
        template = self._create_template(order, "Priced template")
        applied = self._apply_template(template)
        line_a = applied.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        line_b = applied.order_line.filtered(
            lambda line: line.product_id == self.product_b
        )
        option = applied.sale_order_option_ids
        self.assertEqual(line_a.price_unit, 42.0)
        self.assertEqual(line_a.discount, 25.0)
        self.assertEqual(line_a.name, "Product A extra")
        self.assertTrue(line_a.quotation_template_fixed_price)
        self.assertTrue(line_a.quotation_template_keep_name)
        self.assertEqual(line_b.price_unit, 17.0)
        self.assertEqual(line_b.discount, 5.0)
        self.assertEqual(line_b.name, "Product B extra")
        self.assertEqual(option.price_unit, 33.0)
        self.assertEqual(option.discount, 8.0)
        self.assertEqual(option.name, "Option extra")
        self.assertTrue(option.quotation_template_fixed_price)
        self.assertTrue(option.quotation_template_keep_name)

        _list_name, list_price, list_discount = self._pricelist_values(
            self.product_a, self.uom_unit, qty=2
        )
        self.assertAlmostEqual(list_price, 100.0, places=2)
        # sale_order_general_discount, installed with the rest of this repo,
        # replaces a pricelist discount with 0 when no general discount is set.
        self.assertNotEqual(list_discount, 25.0)
        applied._recompute_prices()
        self.assertEqual(line_a.price_unit, 42.0)
        self.assertEqual(line_a.discount, 25.0)
        self.assertEqual(option.price_unit, 33.0)
        self.assertEqual(option.discount, 8.0)

        copied = applied.copy()
        copied_line = copied.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertEqual(copied_line.price_unit, 42.0)
        self.assertEqual(copied_line.discount, 25.0)
        self.assertEqual(copied_line.name, "Product A extra")
        self.assertEqual(copied.sale_order_option_ids.price_unit, 33.0)
        self.assertEqual(copied.sale_order_option_ids.discount, 8.0)
        self.assertEqual(copied.sale_order_option_ids.name, "Option extra")

        with Form(applied) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.product_uom_qty = 5
        self.assertEqual(line_a.price_unit, 42.0)
        self.assertEqual(line_a.discount, 25.0)
        self.assertEqual(line_a.name, "Product A extra")

        with Form(applied) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.product_id = self.product_b
        self.assertEqual(line_a.product_id, self.product_b)
        other_name, other_price, other_discount = self._pricelist_values(
            self.product_b, self.uom_unit, qty=5
        )
        self.assertEqual(line_a.name, other_name)
        self.assertAlmostEqual(line_a.price_unit, other_price, places=2)
        self.assertAlmostEqual(line_a.discount, other_discount, places=2)
        self.assertFalse(line_a.quotation_template_fixed_price)
        self.assertFalse(line_a.quotation_template_keep_name)

        with Form(applied) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.product_id = self.product_a
        back_name, back_price, back_discount = self._pricelist_values(
            self.product_a, self.uom_unit, qty=5
        )
        self.assertEqual(line_a.name, back_name)
        self.assertNotEqual(line_a.name, other_name)
        self.assertNotEqual(line_a.name, "Product A extra")
        self.assertAlmostEqual(line_a.price_unit, back_price, places=2)
        self.assertAlmostEqual(line_a.discount, back_discount, places=2)
        self.assertNotEqual(line_a.price_unit, 42.0)
        self.assertNotEqual(line_a.price_unit, other_price)

        with Form(applied) as order_form:
            with order_form.order_line.edit(1) as line_form:
                line_form.product_uom = self.uom_dozen
        dozen_name, dozen_price, dozen_discount = self._pricelist_values(
            self.product_b, self.uom_dozen, qty=1
        )
        self.assertEqual(line_b.name, "Product B extra")
        self.assertNotEqual(line_b.name, dozen_name)
        self.assertAlmostEqual(line_b.price_unit, dozen_price, places=2)
        self.assertAlmostEqual(line_b.discount, dozen_discount, places=2)
        self.assertNotEqual(line_b.price_unit, 17.0)

        copied.action_update_prices()
        _updated_name, updated_price, updated_discount = self._pricelist_values(
            self.product_a, self.uom_unit, qty=2
        )
        updated_line = copied.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        self.assertEqual(updated_line.name, "Product A extra")
        self.assertAlmostEqual(updated_line.price_unit, updated_price, places=2)
        self.assertAlmostEqual(updated_line.discount, updated_discount, places=2)
        _option_name, option_price, option_discount = self._pricelist_values(
            self.product_a, self.uom_unit, qty=1
        )
        self.assertEqual(copied.sale_order_option_ids.name, "Option extra")
        self.assertAlmostEqual(
            copied.sale_order_option_ids.price_unit, option_price, places=2
        )
        self.assertAlmostEqual(
            copied.sale_order_option_ids.discount, option_discount, places=2
        )

    def test_option_change_releases_freeze(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "sale_order_option_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Option A extra",
                            "quantity": 1,
                            "uom_id": self.uom_unit.id,
                            "price_unit": 33.0,
                            "discount": 8.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_b.id,
                            "name": "Option B extra",
                            "quantity": 1,
                            "uom_id": self.uom_unit.id,
                            "price_unit": 17.0,
                            "discount": 5.0,
                        }
                    ),
                ],
            }
        )
        template = self._create_template(order, "Option freeze")
        applied = self._apply_template(template)
        option_a = applied.sale_order_option_ids.filtered(
            lambda option: option.product_id == self.product_a
        )
        option_b = applied.sale_order_option_ids.filtered(
            lambda option: option.product_id == self.product_b
        )
        with Form(applied) as order_form:
            with order_form.sale_order_option_ids.edit(0) as option_form:
                option_form.product_id = self.product_b
        other_name, other_price, other_discount = self._pricelist_values(
            self.product_b, self.uom_unit
        )
        self.assertEqual(option_a.product_id, self.product_b)
        self.assertEqual(option_a.name, other_name)
        self.assertAlmostEqual(option_a.price_unit, other_price, places=2)
        self.assertAlmostEqual(option_a.discount, other_discount, places=2)
        self.assertFalse(option_a.quotation_template_fixed_price)
        self.assertFalse(option_a.quotation_template_keep_name)
        self.assertNotEqual(option_a.name, "Option A extra")

        with Form(applied) as order_form:
            with order_form.sale_order_option_ids.edit(1) as option_form:
                option_form.uom_id = self.uom_dozen
        _dozen_name, dozen_price, dozen_discount = self._pricelist_values(
            self.product_b, self.uom_dozen
        )
        self.assertEqual(option_b.name, "Option B extra")
        self.assertAlmostEqual(option_b.price_unit, dozen_price, places=2)
        self.assertAlmostEqual(option_b.discount, dozen_discount, places=2)
        self.assertNotEqual(option_b.price_unit, 17.0)
        self.assertFalse(option_b.quotation_template_fixed_price)
        self.assertFalse(option_b.quotation_template_keep_name)

    def test_stored_zero_is_applied(self):
        template = self.env["sale.order.template"].create(
            {
                "name": "Zero price",
                "sale_order_template_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Zero",
                            "product_uom_qty": 1,
                            "price_unit": 0.0,
                            "discount": 0.0,
                            "manual_price": True,
                        }
                    )
                ],
            }
        )
        applied = self._apply_template(template)
        line = applied.order_line
        _name, list_price, list_discount = self._pricelist_values(
            self.product_a, line.product_uom
        )
        self.assertNotEqual(list_price, 0.0)
        self.assertEqual(line.price_unit, 0.0)
        self.assertEqual(line.discount, 0.0)
        # The same addon leaves the pricelist discount at 0, so the stored
        # zero can only be distinguished when this environment shows one.
        if list_discount:
            self.assertNotEqual(line.discount, list_discount)

    def test_hand_built_template_uses_pricelist(self):
        template = self.env["sale.order.template"].create(
            {
                "name": "Hand built",
                "sale_order_template_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        template_line = template.sale_order_template_line_ids
        self.assertFalse(template_line.manual_price)
        self.assertEqual(template_line.price_unit, 0.0)
        applied = self._apply_template(template)
        line = applied.order_line
        _name, list_price, _discount = self._pricelist_values(
            self.product_a, line.product_uom
        )
        self.assertAlmostEqual(line.price_unit, list_price, places=2)
        self.assertNotEqual(line.price_unit, 0.0)
        self.assertFalse(line.quotation_template_fixed_price)

    def test_descriptions_stay_per_line(self):
        description = self.product_a.get_product_multiline_description_sale()
        first_name = description + "\nFirst extra"
        second_name = "Second custom description"
        # Sequences start at 10. Core sets the first applied line to -99, and
        # sale_multi_template_application then turns that -99 into 10 plus the
        # current maximum. A second line below 10 ends up before the first.
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": first_name,
                            "price_unit": 42.0,
                            "discount": 25.0,
                            "sequence": 10,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": second_name,
                            "price_unit": 17.0,
                            "discount": 5.0,
                            "sequence": 20,
                        }
                    ),
                ],
            }
        )
        template = self._create_template(order, "Descriptions")
        applied = self._apply_template(template)
        self.assertEqual(applied.order_line.mapped("name"), [first_name, second_name])

    def test_skips_downpayment_and_combo(self):
        component = self.env["product.product"].create(
            {"name": "Combo component", "list_price": 5.0, "type": "consu"}
        )
        combo = self.env["product.combo"].create(
            {
                "name": "Combo choice",
                "combo_item_ids": [Command.create({"product_id": component.id})],
            }
        )
        combo_product = self.env["product.product"].create(
            {
                "name": "Combo product",
                "list_price": 20.0,
                "type": "combo",
                "combo_ids": [Command.set(combo.ids)],
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "is_downpayment": True,
                            "name": "Down payment",
                            "price_unit": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Kept",
                            "price_unit": 42.0,
                        }
                    ),
                ],
            }
        )
        combo_line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": combo_product.id,
                "name": "Combo parent",
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": component.id,
                "name": "Combo child",
                "combo_item_id": combo.combo_item_ids.id,
                "linked_line_id": combo_line.id,
            }
        )
        template = self._create_template(order, "Skip lines")
        self.assertEqual(template.sale_order_template_line_ids.mapped("name"), ["Kept"])

    def test_salesman_modifies_only_own_template(self):
        salesman = new_test_user(
            self.env,
            login="salesman_template",
            groups=(
                "sales_team.group_sale_salesman,"
                "sale_management.group_sale_order_template,"
                "sale_order_template_from_sale_order.group_template_from_order"
            ),
        )
        description = self.product_a.get_product_multiline_description_sale()
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "user_id": salesman.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": description,
                            "price_unit": 42.0,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.order_line.name, description)
        wizard = (
            self.env["sale.order.create.template"]
            .with_user(salesman)
            .create({"sale_order_id": order.id, "name": "Salesman template"})
        )
        wizard.action_create_template()
        template = self.env["sale.order.template"].search(
            [("name", "=", "Salesman template")]
        )
        self.assertEqual(len(template), 1)
        template.with_user(salesman).write({"name": "Salesman template renamed"})
        template.sale_order_template_line_ids.with_user(salesman).write(
            {"price_unit": 11.0}
        )
        with self.assertRaises(AccessError):
            template.with_user(salesman).unlink()
        foreign = self.env["sale.order.template"].create(
            {
                "name": "Manager template",
                "sale_order_template_line_ids": [
                    Command.create(
                        {"product_id": self.product_a.id, "name": "Manager line"}
                    )
                ],
                "sale_order_template_option_ids": [
                    Command.create(
                        {"product_id": self.product_b.id, "name": "Manager option"}
                    )
                ],
            }
        )
        line_model = self.env["sale.order.template.line"].with_user(salesman)
        option_model = self.env["sale.order.template.option"].with_user(salesman)
        with self.assertRaises(AccessError):
            foreign.with_user(salesman).write({"name": "Taken over"})
        with self.assertRaises(AccessError):
            foreign.sale_order_template_line_ids.with_user(salesman).write(
                {"name": "Changed"}
            )
        with self.assertRaises(AccessError):
            foreign.sale_order_template_option_ids.with_user(salesman).write(
                {"name": "Changed"}
            )
        with self.assertRaises(AccessError):
            line_model.create(
                {
                    "sale_order_template_id": foreign.id,
                    "product_id": self.product_a.id,
                    "name": "Extra line",
                }
            )
        with self.assertRaises(AccessError):
            option_model.create(
                {
                    "sale_order_template_id": foreign.id,
                    "product_id": self.product_b.id,
                    "name": "Extra option",
                }
            )
        with self.assertRaises(AccessError):
            template.sale_order_template_line_ids.with_user(salesman).write(
                {"sale_order_template_id": foreign.id}
            )
        own_option = option_model.create(
            {
                "sale_order_template_id": template.id,
                "product_id": self.product_b.id,
                "name": "Own option",
            }
        )
        with self.assertRaises(AccessError):
            own_option.write({"sale_order_template_id": foreign.id})

    def test_salesman_without_allow_cannot_create_template(self):
        salesman = new_test_user(
            self.env,
            login="salesman_no_template",
            groups=(
                "sales_team.group_sale_salesman,"
                "sale_management.group_sale_order_template"
            ),
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "user_id": salesman.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "name": "Line",
                            "price_unit": 1.0,
                        }
                    )
                ],
            }
        )
        with self.assertRaises(AccessError):
            self.env["sale.order.create.template"].with_user(salesman).create(
                {"sale_order_id": order.id, "name": "Denied"}
            )
        with self.assertRaises(AccessError):
            self.env["sale.order.template"].with_user(salesman).create(
                {"name": "Denied"}
            )

    def test_manager_modifies_any_template(self):
        manager = new_test_user(
            self.env,
            login="manager_template",
            groups=(
                "sales_team.group_sale_manager,"
                "sale_management.group_sale_order_template"
            ),
        )
        foreign = self.env["sale.order.template"].create(
            {
                "name": "Other template",
                "sale_order_template_line_ids": [
                    Command.create({"product_id": self.product_a.id, "name": "Line"})
                ],
                "sale_order_template_option_ids": [
                    Command.create({"product_id": self.product_b.id, "name": "Option"})
                ],
            }
        )
        other = self.env["sale.order.template"].create({"name": "Second template"})
        foreign.with_user(manager).write({"name": "Manager renamed"})
        foreign.sale_order_template_line_ids.with_user(manager).write(
            {"name": "Line renamed"}
        )
        self.env["sale.order.template.line"].with_user(manager).create(
            {
                "sale_order_template_id": foreign.id,
                "product_id": self.product_a.id,
                "name": "Manager line",
            }
        )
        self.env["sale.order.template.option"].with_user(manager).create(
            {
                "sale_order_template_id": foreign.id,
                "product_id": self.product_b.id,
                "name": "Manager option",
            }
        )
        options = foreign.sale_order_template_option_ids
        options.with_user(manager).write({"sale_order_template_id": other.id})
        self.assertEqual(options.sale_order_template_id, other)

    def test_editing_template_price_sets_manual_price(self):
        template = self.env["sale.order.template"].create(
            {
                "name": "Editable",
                "sale_order_template_line_ids": [
                    Command.create({"product_id": self.product_a.id})
                ],
                "sale_order_template_option_ids": [
                    Command.create({"product_id": self.product_b.id})
                ],
            }
        )
        self.assertFalse(template.sale_order_template_line_ids.manual_price)
        self.assertFalse(template.sale_order_template_option_ids.manual_price)
        with Form(template) as template_form:
            with template_form.sale_order_template_line_ids.edit(0) as line_form:
                line_form.price_unit = 15.0
            with template_form.sale_order_template_option_ids.edit(0) as option_form:
                option_form.discount = 4.0
        self.assertTrue(template.sale_order_template_line_ids.manual_price)
        self.assertEqual(template.sale_order_template_line_ids.price_unit, 15.0)
        self.assertTrue(template.sale_order_template_option_ids.manual_price)
        self.assertEqual(template.sale_order_template_option_ids.discount, 4.0)
