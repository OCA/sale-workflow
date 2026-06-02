# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_custom_compute_tax_cache_key(self):
        template = self.product_id.product_tmpl_id
        fiscal_position = self.order_id.fiscal_position_id
        return tuple(
            fiscal_position.tax_ids.filtered(
                lambda line: line._is_applicable_to_product_template(template)
            ).ids
        )

    def _compute_tax_id(self):
        lines_by_fp_id = defaultdict(lambda: self.env["sale.order.line"])
        domain_by_fp_id = {}
        processed_lines = self.browse()

        for line in self:
            fp = line.order_id.fiscal_position_id
            if not fp:
                continue
            domain = domain_by_fp_id.setdefault(
                fp.id, safe_eval(fp.product_domain or "[]")
            )
            if domain:
                lines_by_fp_id[fp.id] |= line

        if not lines_by_fp_id:
            return super()._compute_tax_id()

        for fp_id, lines in lines_by_fp_id.items():
            domain = domain_by_fp_id[fp_id]
            matched_templates = lines.product_id.product_tmpl_id.filtered_domain(domain)
            matched_template_ids = frozenset(matched_templates.ids)

            def line_matches_domain(line, template_ids=matched_template_ids):
                return line.product_id.product_tmpl_id.id in template_ids

            matched_lines = lines.filtered(line_matches_domain)

            for domain_lines in (matched_lines, lines - matched_lines):
                if not domain_lines:
                    continue
                domain_lines = domain_lines.with_context(
                    fp_template=domain_lines.product_id.product_tmpl_id
                )
                super(SaleOrderLine, domain_lines)._compute_tax_id()
                processed_lines |= domain_lines

        remaining_lines = self - processed_lines
        if remaining_lines:
            return super(SaleOrderLine, remaining_lines)._compute_tax_id()
        return None
