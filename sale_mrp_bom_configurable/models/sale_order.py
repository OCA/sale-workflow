from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_default_input_config(self):
        if (
            self.env.context.get("configurable_quotation")
            and len(self.input_config_ids) == 0
        ):
            input_config = self.env["input.config"].create({})
            return [(4, input_config.id, 0)]
        return []

    input_config_ids = fields.One2many(
        comodel_name="input.config",
        inverse_name="order_id",
        string="Input configs",
        default=_get_default_input_config,
    )

    input_config_id = fields.Many2one(
        comodel_name="input.config",
        compute="_compute_input_config_id",
        store=True,
    )

    input_config_id_name = fields.Char(
        related="input_config_id.name",
        readonly=False,
    )

    bom_id = fields.Many2one(
        related="input_config_id.bom_id",
        readonly=False,
    )

    order_line_count = fields.Integer(
        string="Order lines count", compute="_compute_order_line_count"
    )

    @api.depends("order_line")
    def _compute_order_line_count(self):
        for rec in self:
            rec.order_line_count = len(rec.order_line)

    @api.depends("input_config_ids")
    def _compute_input_config_id(self):
        for rec in self:
            if len(rec.input_config_ids) > 0:
                rec.input_config_id = rec.input_config_ids[0]
            else:
                rec.input_config_id = False

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.input_config_id:
                rec.input_config_id_name = f"config {rec.name}"
        return res

    def show_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lines",
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "view_id": self.env.ref(
                "sale_mrp_bom_configurable.sale_order_line_tree_multi_edit"
            ).id,
            "domain": [("order_id", "=", self.id), ("is_static_product", "=", False)],
        }
