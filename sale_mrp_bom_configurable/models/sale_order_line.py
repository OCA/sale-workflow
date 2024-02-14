import json

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    input_config_id = fields.Many2one(
        comodel_name="input.config", related="order_id.input_config_id"
    )

    input_line_id = fields.Many2one(
        comodel_name="input.line",
    )
    input_line_domain = fields.Char(
        compute="_compute_input_line_domain",
    )
    bom_id = fields.Many2one(compute="_compute_bom_id")
    allowed_product_id = fields.Char(compute="_compute_allowed_product_id")
    should_filter_product = fields.Boolean(compute="_compute_should_filter_product")

    @api.depends("input_config_id")
    def _compute_input_line_domain(self):
        for rec in self:
            breakpoint()
            allowed_ids = (
                self.env["input.line"]
                .search([("config_id", "=", rec.input_config_id.id)])
                .mapped("id")
            )
            rec.input_line_domain = [("id", "in", allowed_ids)]

    @api.depends("input_line_id")
    def _compute_bom_id(self):
        for rec in self:
            rec.bom_id = rec.input_line_id.bom_id

    @api.depends("input_config_id")
    def _compute_allowed_product_id(self):
        for rec in self:
            if rec.input_config_id:
                product_id = rec.input_config_id.bom_id.product_tmpl_id
                rec.allowed_product_id = product_id.id
            else:
                rec.allowed_product_id = "-1"

    @api.depends("input_config_id")
    def _compute_should_filter_product(self):
        for rec in self:
            rec.should_filter_product = not bool(rec.input_config_id)

    def action_show_input_line(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Input line information",
            "res_model": "input.line",
            "view_mode": "form",
            "target": "new",
            "res_id": self.input_line_id.id,
        }
