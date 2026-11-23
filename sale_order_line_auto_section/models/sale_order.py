# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    auto_section_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Auto Section Category",
        help="Product category that generated this automatic section. "
        "Used to identify and update auto-generated sections.",
        copy=False,
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_organize_lines_by_category(self):
        """Reorganize sale order lines into sections based on product categories.

        This method:
        - Groups product lines by their category
        - Removes only auto-generated sections (preserves manual sections/notes)
        - Creates new section headers for each category
        - Preserves the relative order of manual sections and notes
        """
        self.ensure_one()

        # Get product lines (lines with products, no display type)
        product_lines = self.order_line.filtered(
            lambda line: not line.display_type and line.product_id
        )
        if not product_lines:
            return

        # Remove auto-generated sections for categories no longer used
        categories_used = set(product_lines.mapped("product_id.categ_id"))
        sections_to_delete = self.order_line.filtered(
            lambda line: line.display_type == "line_section"
            and line.auto_section_category_id
            and line.auto_section_category_id not in categories_used
        )
        sections_to_delete.unlink()

        # Create missing sections
        existing_sections = self.order_line.filtered("auto_section_category_id")
        existing_categories = set(existing_sections.mapped("auto_section_category_id"))
        missing_categories = categories_used - existing_categories
        for category in missing_categories:
            self.env["sale.order.line"].create(
                {
                    "order_id": self.id,
                    "display_type": "line_section",
                    "name": category.section_title or category.name,
                    "auto_section_category_id": category.id,
                }
            )

        # Resequence product lines under their sections
        # Get all auto-generated sections first
        all_auto_sections = self.order_line.filtered("auto_section_category_id").sorted(
            key=lambda s: (
                s.auto_section_category_id.section_sequence or 9,
                s.auto_section_category_id.name,
            )
        )
        for i, section in enumerate(all_auto_sections, 1):
            section.sequence = i * 10000
            category = section.auto_section_category_id
            section_lines = self.order_line.filtered(
                lambda line, cat=category: line.product_id.categ_id == cat
            )

            # Sort lines based on the category's sorting preference
            if category.section_sort_by == "default_code":
                section_lines = section_lines.sorted(
                    lambda line: line.product_id.default_code or ""
                )

            for j, line in enumerate(section_lines, 1):
                line.sequence = section.sequence + j

        # Move manual sections/notes to the end
        manual_lines = self.order_line.filtered(
            lambda line: line.display_type in ["line_section", "line_note"]
            and not line.auto_section_category_id
        )
        if manual_lines:
            max_sequence = max(self.order_line.mapped("sequence") or [100])
            for i, line in enumerate(manual_lines, 1):
                line.sequence = max_sequence + i

        return {
            "type": "ir.actions.client",
            "tag": "reload_context",
        }
