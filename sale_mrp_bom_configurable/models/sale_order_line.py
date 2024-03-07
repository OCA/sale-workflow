from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    input_config_id = fields.Many2one(
        comodel_name="input.config", related="order_id.input_config_id"
    )

    input_line_id = fields.Many2one(
        comodel_name="input.line",
        compute="_compute_input_line_id",
        inverse="_inverse_input_line_id",
        store=True,
    )
    input_line_domain = fields.Binary(
        compute="_compute_input_line_domain",
    )
    bom_id = fields.Many2one(compute="_compute_bom_id")
    allowed_product_id = fields.Char(compute="_compute_allowed_product_id")
    should_filter_product = fields.Boolean(compute="_compute_should_filter_product")

    @api.depends("input_config_id")
    def _compute_input_line_id(self):
        for rec in self:
            if rec.input_line_id.id in rec.input_config_id.line_ids.mapped("id"):
                rec.input_line_id = rec.input_line_id
            else:
                rec.input_line_id = False

    def _inverse_input_line_id(self):
        pass

    @api.depends("input_config_id")
    def _compute_input_line_domain(self):
        for rec in self:
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

    @api.depends("product_id", "product_uom", "product_uom_qty", "input_line_id")
    def _compute_price_unit(self):
        for rec in self:
            rec = rec.with_context(
                price_config=rec.product_id.product_tmpl_id._find_price_config(),
                input_line=rec.input_line_id,
            )
            super(SaleOrderLine, rec)._compute_price_unit()

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
