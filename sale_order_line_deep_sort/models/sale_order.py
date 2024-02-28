# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

import logging

from odoo import api, fields, models

from .res_company import SORTING_DIRECTION

_logger = logging.getLogger(__name__)

string_types = ["char", "text", "date", "datetime", "selection"]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'sale.order.line')]",
        default=lambda self: self.env.user.company_id.default_so_line_order,
    )
    line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'sale.order.line')]",
        default=lambda self: self.env.user.company_id.default_so_line_order_2,
    )
    line_direction = fields.Selection(
        selection=SORTING_DIRECTION,
        string="Sort Direction",
        default=lambda self: self.env.user.company_id.default_so_line_direction,
    )

    @api.onchange("line_order")
    def onchange_line_order(self):
        if not self.line_order and not self.line_order_2:
            self.line_direction = False

    def _sort_sale_line(self):
        def resolve_subfields(obj, line_order):
            if not line_order:
                return None
            val = getattr(obj, line_order.name)
            # Odoo object
            if isinstance(val, models.BaseModel):
                if not val:
                    val = ""
                elif hasattr(val[0], "name"):
                    val = ",".join(val.mapped("name"))
                else:
                    val = ",".join([str(id) for id in val.mapped("id")])
            elif line_order.ttype in string_types:
                if not val:
                    val = ""
                elif not isinstance(val, str):
                    try:
                        val = str(val)
                    except Exception:
                        val = ""
            return val

        if (
            not self.line_order and not self.line_order_2 and not self.line_direction
        ) or self.order_line.filtered(lambda p: p.display_type == "line_section"):
            return
        reverse = self.line_direction == "desc"
        sequence = 0
        try:
            sorted_lines = self.order_line.sorted(
                key=lambda p: (
                    p.display_type is False,
                    resolve_subfields(p, self.line_order),
                    resolve_subfields(p, self.line_order_2),
                ),
                reverse=reverse,
            )
            for line in sorted_lines:
                sequence += 10
                if line.sequence == sequence:
                    continue
                line.sequence = sequence
        except Exception:
            _logger.warning("Could not sort sale order!")

    def write(self, values):
        res = super().write(values)
        if (
            "order_line" in values
            or "line_order" in values
            or "line_order_2" in values
            or "line_direction" in values
        ):
            for record in self:
                record._sort_sale_line()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for order_id in lines.mapped("order_id"):
            order_id._sort_sale_line()
        return lines
