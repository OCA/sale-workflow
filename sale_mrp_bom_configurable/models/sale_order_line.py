from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    input_config_id = fields.Many2one(
        comodel_name="input.config", related="order_id.input_config_id"
    )

    input_line_ids = fields.One2many(
        comodel_name="input.line",
        string="Input lines",
        inverse_name="order_line_id",
    )

    input_line_id = fields.Many2one(
        comodel_name="input.line",
        string="Input line",
        compute="_compute_input_line_id",
        store=True,
        precompute=True,
    )

    input_line_id_name = fields.Char(related="input_line_id.name", readonly=False)
    input_line_domain = fields.Char()

    bom_id = fields.Many2one(compute="_compute_bom_id")
    allowed_product_id = fields.Char(
        compute="_compute_allowed_product_id", store=True, precompute=True
    )
    should_filter_product = fields.Boolean(compute="_compute_should_filter_product")

    should_compute_price = fields.Boolean(
        compute="_compute_should_compute_price", store=True, precompute=True
    )

    def _compute_should_compute_price(self):
        "_compute_should_compute_price must be overriden.  It should set should_compute_price to True and depend on all relevant field in input_line"

    @api.model
    def _get_default_product_template_id(self):
        input_config_id = self.env["input.config"].browse(
            self.env.context.get("input_config_id")
        )
        if input_config_id:
            return input_config_id.bom_id.product_tmpl_id
        return False

    product_template_id = fields.Many2one(
        default=_get_default_product_template_id,
        compute="_compute_product_template_id",
        inverse="_inverse_product_template_id",
        store=True,
        precompute=False,
    )

    @api.model
    def _get_default_product_id(self):
        input_config_id = self.env["input.config"].browse(
            self.env.context.get("input_config_id")
        )
        if input_config_id:
            return input_config_id.bom_id.product_tmpl_id.product_variant_id
        return False

    product_id = fields.Many2one(
        default=_get_default_product_id,
    )

    @api.depends("input_config_id")
    def _compute_product_template_id(self):
        if self.env.context.get("configurable_quotation", False):
            for rec in self:
                rec.product_template_id = (
                    rec.order_id.input_config_id.bom_id.product_tmpl_id
                )
        else:
            for rec in self:
                rec.product_template_id = rec.product_template_id

    def _inverse_product_template_id(self):
        pass

    def _prepare_default_input_line_vals(self):
        vals = {"config_id": self.input_config_id.id, "name": "A1"}
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            vals = rec._prepare_default_input_line_vals()
            input_line = self.env["input.line"].create(vals)
            rec.input_line_ids = [(4, input_line.id, 0)]

        return res

    @api.depends("input_line_ids")
    def _compute_input_line_id(self):
        for rec in self:
            if len(rec.input_line_ids) > 0:
                rec.input_line_id = rec.input_line_ids[0]
                rec.input_line_id.config_id = self.input_config_id
            else:
                rec.input_line_id = False

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

    @api.depends("should_compute_price")
    def _compute_price_unit(self):
        for rec in self:
            rec = rec.with_context(
                price_config=rec.product_id.product_tmpl_id._find_price_config(),
                input_line=rec.input_line_id,
            )
            super(SaleOrderLine, rec)._compute_price_unit()
            rec.should_compute_price = False
        return True

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
