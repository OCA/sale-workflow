# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestSaleOrderLineAutoSection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.category_a = cls.env["product.category"].create(
            {
                "name": "Category A",
                "section_sequence": 10,
                "section_title": "Section A Title",
            }
        )
        cls.category_b = cls.env["product.category"].create(
            {
                "name": "Category B",
                "section_sequence": 20,
            }
        )
        cls.category_c = cls.env["product.category"].create(
            {
                "name": "Category C",
                "section_sequence": 5,
                "section_title": "Section C Title",
            }
        )

        cls.product_a1 = cls.env["product.product"].create(
            {
                "name": "Product A1",
                "categ_id": cls.category_a.id,
                "list_price": 100.0,
            }
        )
        cls.product_a2 = cls.env["product.product"].create(
            {
                "name": "Product A2",
                "categ_id": cls.category_a.id,
                "list_price": 150.0,
            }
        )
        cls.product_b1 = cls.env["product.product"].create(
            {
                "name": "Product B1",
                "categ_id": cls.category_b.id,
                "list_price": 200.0,
            }
        )
        cls.product_c1 = cls.env["product.product"].create(
            {
                "name": "Product C1",
                "categ_id": cls.category_c.id,
                "list_price": 50.0,
            }
        )

    def test_basic_organization(self):
        """Test basic organization of lines by category."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_a1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.product_b1.id, "product_uom_qty": 2}),
                    (0, 0, {"product_id": self.product_a2.id, "product_uom_qty": 3}),
                ],
            }
        )

        self.assertEqual(len(order.order_line), 3)

        order.action_organize_lines_by_category()

        sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertEqual(len(sections), 2)

        section_names = sections.mapped("name")
        self.assertIn("Section A Title", section_names)
        self.assertIn("Category B", section_names)

        lines_with_sections = order.order_line.sorted("sequence")
        self.assertEqual(lines_with_sections[0].name, "Section A Title")
        self.assertEqual(
            lines_with_sections[0].auto_section_category_id, self.category_a
        )
        self.assertEqual(lines_with_sections[1].product_id, self.product_a1)
        self.assertEqual(lines_with_sections[2].product_id, self.product_a2)
        self.assertEqual(lines_with_sections[3].name, "Category B")
        self.assertEqual(
            lines_with_sections[3].auto_section_category_id, self.category_b
        )
        self.assertEqual(lines_with_sections[4].product_id, self.product_b1)

    def test_section_sequence_ordering(self):
        """Test that sections are ordered by section_sequence."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_a1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.product_b1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.product_c1.id, "product_uom_qty": 1}),
                ],
            }
        )

        order.action_organize_lines_by_category()

        sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        ).sorted("sequence")

        self.assertEqual(sections[0].name, "Section C Title")
        self.assertEqual(sections[0].auto_section_category_id, self.category_c)
        self.assertEqual(sections[1].name, "Section A Title")
        self.assertEqual(sections[1].auto_section_category_id, self.category_a)
        self.assertEqual(sections[2].name, "Category B")
        self.assertEqual(sections[2].auto_section_category_id, self.category_b)

    def test_preserve_manual_sections(self):
        """Test that manual sections are preserved when reorganizing."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "display_type": "line_section",
                            "name": "Manual Section 1",
                            "sequence": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a1.id,
                            "product_uom_qty": 1,
                            "sequence": 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "display_type": "line_note",
                            "name": "Important Note",
                            "sequence": 3,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b1.id,
                            "product_uom_qty": 1,
                            "sequence": 4,
                        },
                    ),
                ],
            }
        )

        order.action_organize_lines_by_category()

        manual_section = order.order_line.filtered(
            lambda line: line.name == "Manual Section 1"
        )
        self.assertEqual(len(manual_section), 1)
        self.assertFalse(manual_section.auto_section_category_id)

        note = order.order_line.filtered(lambda line: line.name == "Important Note")
        self.assertEqual(len(note), 1)
        self.assertFalse(note.auto_section_category_id)

        auto_sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
            and line.auto_section_category_id
        )
        self.assertEqual(len(auto_sections), 2)

    def test_no_duplicate_on_rerun(self):
        """Test that running the action multiple times doesn't duplicate sections."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_a1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.product_b1.id, "product_uom_qty": 2}),
                ],
            }
        )

        order.action_organize_lines_by_category()
        first_run_sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        first_run_count = len(first_run_sections)

        order.action_organize_lines_by_category()
        second_run_sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        second_run_count = len(second_run_sections)

        self.assertEqual(first_run_count, second_run_count)
        self.assertEqual(second_run_count, 2)

        order.action_organize_lines_by_category()
        third_run_sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        third_run_count = len(third_run_sections)

        self.assertEqual(third_run_count, 2)

    def test_manual_sections_preserved_on_rerun(self):
        """Test that manual sections remain after multiple runs."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "display_type": "line_section",
                            "name": "Custom Header",
                            "sequence": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a1.id,
                            "product_uom_qty": 1,
                            "sequence": 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b1.id,
                            "product_uom_qty": 1,
                            "sequence": 3,
                        },
                    ),
                ],
            }
        )

        order.action_organize_lines_by_category()

        manual_section_exists = order.order_line.filtered(
            lambda line: line.name == "Custom Header"
        )
        self.assertEqual(len(manual_section_exists), 1)

        order.action_organize_lines_by_category()

        manual_section_still_exists = order.order_line.filtered(
            lambda line: line.name == "Custom Header"
        )
        self.assertEqual(len(manual_section_still_exists), 1)

        auto_sections = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
            and line.auto_section_category_id
        )
        self.assertEqual(len(auto_sections), 2)

    def test_empty_order(self):
        """Test that organizing an empty order doesn't cause errors."""
        order = self.env["sale.order"].create({"partner_id": self.partner.id})

        result = order.action_organize_lines_by_category()

        self.assertIsNone(result)
        self.assertEqual(len(order.order_line), 0)

    def test_order_with_only_sections(self):
        """Test organizing an order with only section/note lines."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"display_type": "line_section", "name": "Section Only"}),
                    (0, 0, {"display_type": "line_note", "name": "Note Only"}),
                ],
            }
        )

        result = order.action_organize_lines_by_category()

        self.assertIsNone(result)
        self.assertEqual(len(order.order_line), 2)
        manual_lines = order.order_line.filtered(
            lambda line: not line.auto_section_category_id
        )
        self.assertEqual(len(manual_lines), 2)

    def test_category_without_section_title(self):
        """Test that category name is used when section_title is not set."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_b1.id, "product_uom_qty": 1}),
                ],
            }
        )

        order.action_organize_lines_by_category()

        section = order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertEqual(len(section), 1)
        self.assertEqual(section.name, "Category B")
        self.assertEqual(section.auto_section_category_id, self.category_b)
