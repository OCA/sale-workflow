from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    input_line_id_name = fields.Char(
        related="input_line_id.name", readonly=False, store=True
    )
    input_line_domain = fields.Char()

    should_compute_price = fields.Boolean(
        compute="_compute_should_compute_price", store=True, precompute=True
    )
    is_static_product = fields.Boolean(compute="_compute_is_static_product", store=True)

    @api.depends("product_template_id", "input_line_id")
    def _compute_is_static_product(self):
        for rec in self:
            rec.is_static_product = not bool(rec.input_line_id)

    def _compute_should_compute_price(self):
        return (
            "_compute_should_compute_price must be overriden."
            + "It should set should_compute_price to True and "
            + "depend on all relevant field in input_line"
        )

    def _prepare_default_input_line_vals(self):
        vals = {"name": "A1"}
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            template_boms = rec.product_template_id.bom_ids
            is_static = True
            template_variable_bom = False
            # sale_order_line product_template_id is not static
            # if the product template has a only one bom and that bom
            # is variable
            if (
                len(template_boms) == 1
                and template_boms[0].configuration_type == "variable"
            ):
                is_static = False
                template_variable_bom = template_boms[0]

            if not is_static:
                # Search if sale_order already has the config_id for this
                # product template
                input_config_filtered = list(
                    filter(
                        lambda x: x.bom_id.id == template_variable_bom.id,
                        rec.order_id.input_config_ids,
                    )
                )
                input_config = False
                if len(input_config_filtered) == 0:
                    # create a new input_config
                    input_config = self.env["input.config"].create(
                        {"bom_id": template_variable_bom.id}
                    )
                    rec.order_id.input_config_ids = [(4, input_config.id, 0)]
                else:
                    input_config = input_config_filtered[0]

                vals = rec._prepare_default_input_line_vals()
                vals["config_id"] = input_config.id
                input_line = (
                    self.env["input.line"]
                    .with_context(active_id=input_config.id)
                    .create(vals)
                )
                rec.input_line_ids = [(4, input_line.id, 0)]

        return res

    @api.depends("input_line_ids")
    def _compute_input_line_id(self):
        for rec in self:
            if len(rec.input_line_ids) > 0:
                rec.input_line_id = rec.input_line_ids[0]
            else:
                rec.input_line_id = False

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

    def action_run_copy_data_wizard(self):
        wizard_id = self.env["wizard.copy.input.line.data"].create(
            {
                "input_line_id": self.input_line_id.id,
                "input_config_id": self.input_line_id.config_id.id,
            }
        )

        return {
            "type": "ir.actions.act_window",
            "name": "Copy input line data",
            "res_model": "wizard.copy.input.line.data",
            "view_mode": "form",
            "target": "new",
            "res_id": wizard_id.id,
        }
