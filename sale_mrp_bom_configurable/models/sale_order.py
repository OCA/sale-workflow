from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_default_input_config(self):
        if self.env.context.get("configurable_quotation"):
            input_config = self.env["input.config"].create({})
            return [(4, 0, input_config.id)]
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
