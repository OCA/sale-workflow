from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    input_config_ids = fields.One2many(
        comodel_name="input.config", inverse_name="sale_id"
    )
    input_config_id = fields.Many2one(
        comodel_name="input.config",
        search="_search_input_config_id",
        recursive="True",
        compute="_compute_input_config",
        inverse="_inverse_input_config",
    )

    @api.depends("input_config_ids")
    def _compute_input_config(self):
        for rec in self:
            if len(rec.input_config_ids) > 0:
                rec.input_config_id = rec.input_config_ids[0]

    def _search_input_config_id(self, operator, value):
        return [("input_config_id", operator, value)]

    def _inverse_input_config(self):
        self.ensure_one()
        if len(self.input_config_ids) > 0:
            config = self.env["input.config"].browse(self.input_config_ids[0].id)
            config.sale_id = False
        self.input_config_id.sale_id = self

    def open_input_line_wizard(self):
        self.ensure_one()
        return self.input_config_id.open_input_line_wizard()
