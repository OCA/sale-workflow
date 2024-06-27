# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from collections import defaultdict

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    split_strategy_id = fields.Many2one("sale.order.split.strategy")

    def action_split(self, silent_errors=False):
        orders_without_split = self.filtered(lambda o: not o.split_strategy_id)
        if not silent_errors and orders_without_split:
            raise UserError(
                _(
                    "Cannot split orders %(order_names)s without any split strategy defined",
                    order_names=", ".join(orders_without_split.mapped("name")),
                )
            )
        new_order_ids = []
        for order in self:
            lines_to_split = order.split_strategy_id._select_lines_to_split(order)
            if order._has_only_lines_to_split(lines_to_split):
                order._handle_only_lines_to_split()
                continue
            if not lines_to_split:
                order._handle_no_lines_to_split(silent_errors=silent_errors)
                continue
            new_order = order.copy(order._prepare_order_split_copy_defaults())
            sections_dict = order._get_lines_grouped_by_sections()
            order._split_lines(sections_dict, lines_to_split, new_order)
            order.message_post(body=order._prepare_message_split_to(new_order))
            new_order.message_post(body=new_order._prepare_message_split_from(order))
            new_order_ids.append(new_order.id)
            order._postprocess_split_from()
            new_order._postprocess_split_to(order)
        return self.browse(new_order_ids)

    def _handle_no_lines_to_split(self, silent_errors=False):
        self.ensure_one()
        msg = _(
            "Cannot split order %(order_name)s according to its strategy"
            " because there are no matching lines",
            order_name=self.name,
        )
        if not silent_errors:
            raise UserError(msg)
        else:
            self.message_post(body=msg)

    def _handle_only_lines_to_split(self):
        self.ensure_one()
        self.message_post(
            body=_(
                "This sale order was not split using strategy %(strategy)s"
                " because there would not be any lines left on this order.",
                strategy=self.split_strategy_id.name,
            )
        )

    def _has_only_lines_to_split(self, lines_to_split):
        self.ensure_one()
        return self.order_line.filtered(lambda l: not l._is_delivery()) == lines_to_split

    def _split_lines(self, sections_dict, lines_to_split, target_order):
        self.ensure_one()
        copy_sections = self.split_strategy_id.copy_sections
        copy_notes = self.split_strategy_id.copy_notes
        for section_id, line_ids in sections_dict.items():
            section_line = self.env["sale.order.line"].browse(section_id)
            section_lines = self.env["sale.order.line"].browse(line_ids)
            for line in section_lines:
                if line in lines_to_split:
                    line.write(target_order._prepare_order_split_line_move_defaults())
                # FIXME: We should consider if the line is part of the section
                if copy_notes and line.display_type == "line_note":
                    line.copy(target_order._prepare_order_split_line_move_defaults())
            lines_in_section_to_split = [
                li in lines_to_split for li in section_lines if not li.display_type
            ]
            # If all lines in section are to split, move the section to split order
            if copy_sections and section_line and all(lines_in_section_to_split):
                section_line.write(
                    target_order._prepare_order_split_line_move_defaults()
                )
            # If any line in section is to split, copy the section to split order
            elif copy_sections and section_line and any(lines_in_section_to_split):
                section_line.copy(
                    target_order._prepare_order_split_line_move_defaults()
                )
        return True

    def _get_lines_grouped_by_sections(self):
        # Prepare a dict from sale order lines and their sections
        self.ensure_one()
        sections_dict = defaultdict(list)
        section_id = None
        for line in self.order_line.sorted():
            if line.display_type == "line_section":
                section_id = line.id
            sections_dict[section_id].append(line.id)
        return sections_dict

    def _prepare_message_split_from(self, order):
        self.ensure_one()
        template = self.env["ir.ui.view"].search(
            [("key", "=", "sale_order_split_strategy.split_from")], limit=1
        )
        if not template:
            return _(
                "This sale order was created after splitting lines from %(order_name)s"
                " using strategy %(strategy)s",
                order_name=order.name,
                strategy=order.split_strategy_id.name,
            )
        else:
            return template._render(values={"from_order": order})

    def _prepare_message_split_to(self, order):
        self.ensure_one()
        template = self.env["ir.ui.view"].search(
            [("key", "=", "sale_order_split_strategy.split_to")], limit=1
        )
        if not template:
            return _(
                "This sale order had some of its lines split to %(order_name)s"
                " using strategy %(strategy)s",
                order_name=order.name,
                strategy=self.split_strategy_id.name,
            )
        else:
            return template._render(values={"from_order": self, "to_order": order})

    def _prepare_order_split_copy_defaults(self):
        """Hook to customize values used on new sale order from split"""
        self.ensure_one()
        return {"order_line": False}

    def _prepare_order_split_line_move_defaults(self):
        """Hook to customize values used on new sale order line from split"""
        self.ensure_one()
        return {"order_id": self.id}

    def _postprocess_split_from(self):
        self.ensure_one()
        # Remove empty sections
        if not self.split_strategy_id.copy_sections and self.split_strategy_id.remove_empty_sections_after_split:
            sections_dict = self._get_lines_grouped_by_sections()
            section_ids_to_unlink = [section_id for section_id, line_ids in sections_dict.items() if len(line_ids) == 1 and section_id == line_ids[0]]
            section_lines = self.env["sale.order.line"].browse(section_ids_to_unlink)
            section_lines.unlink()

    def _postprocess_split_to(self, origin_order):
        self.ensure_one()
