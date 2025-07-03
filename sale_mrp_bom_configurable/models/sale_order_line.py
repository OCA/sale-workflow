from odoo import api, fields, models
from odoo.fields import Command


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
    )

    input_line_id_name = fields.Char(related="input_line_id.name", readonly=False, store=True)
    input_line_domain = fields.Char()

    should_compute_price = fields.Boolean(
        compute="_compute_should_compute_price",
        store=True,
        precompute=True,
        default=False,
    )
    is_static_product = fields.Boolean(compute="_compute_is_static_product", store=True)

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "input_line_ids" not in default:
            default["input_line_ids"] = [
                Command.create(input_line.copy_data()[0]) for input_line in self.input_line_ids
            ]
        return super().copy_data(default)

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

    @api.onchange("product_template_id")
    def onchange_product_template_id(self):
        to_change = {}
        input_line_to_delete = []
        for rec in self:
            template_variable_boms = rec._get_variable_bom()
            if rec.product_template_id and len(template_variable_boms) > 0:
                input_line = rec.input_line_id
                if not input_line:
                    if len(template_variable_boms) > 0:
                        rec._create_input_line_config_from_line(template_variable_boms[0])
                elif input_line.bom_id.product_tmpl_id != rec.product_template_id:
                    to_change[rec.id] = rec.input_line_id.copy_data()[0]
                    input_line_to_delete = rec.input_line_ids.mapped("id")
                    rec.input_line_ids = [(5, 0, 0)]

        self.env["input.line"].search([("id", "in", input_line_to_delete)]).unlink()

        for rec in self:
            if rec.id in to_change:
                template_variable_boms = rec._get_variable_bom()
                if len(template_variable_boms) > 0:
                    rec._create_input_line_config_from_line(
                        template_variable_boms[0], to_change[rec.id]
                    )

    def _get_variable_bom(self):
        template_boms = self.product_template_id.bom_ids
        template_variable_bom = False
        # sale_order_line product_template_id is not static
        # if the product template has a only one bom and that bom
        # is variable
        if len(template_boms) == 1 and template_boms[0].configuration_type == "variable":
            template_variable_bom = template_boms[0]
            return [template_variable_bom[0]]

        return []

    def _create_input_line_config_from_line(self, template_variable_bom, copy_vals=None):
        self.ensure_one()
        # Search if sale_order already has the config_id for this
        # product template
        order_id = (
            self.env["sale.order"].browse(self.order_id.id.origin)
            if self.order_id.id.origin
            else self.order_id
        )
        input_config_filtered = list(
            filter(
                lambda x: x.bom_id.id == template_variable_bom.id,
                order_id.input_config_ids,
            )
        )
        input_config = False
        if len(input_config_filtered) == 0:
            # create a new input_config
            input_config = self.env["input.config"].create(
                {
                    "bom_id": template_variable_bom.id,
                    "name": f"{order_id.name} - {self.name}",
                }
            )
            order_id.input_config_ids = [(4, input_config.id, 0)]
        else:
            input_config = input_config_filtered[0]

        vals = self._prepare_default_input_line_vals()

        if copy_vals:
            vals.update(copy_vals)

        vals["config_id"] = input_config.id
        input_line = self.env["input.line"].create(vals)
        self.input_line_ids = [(4, input_line.id, 0)]

    @api.onchange("input_line_ids")
    def _onchange_input_line_ids(self):
        for rec in self:
            if len(rec.input_line_ids) > 0:
                rec.input_line_id = rec.input_line_ids[0]
            else:
                rec.input_line_id = False

    @api.depends("should_compute_price")
    def _compute_price_unit(self):
        for rec in self:
            if not rec.is_static_product:
                if rec.should_compute_price:
                    rec = rec.with_context(
                        price_config=rec.product_template_id._find_price_config(),
                        input_line=rec.input_line_id,
                    )
                    rec.should_compute_price = False
                    super(SaleOrderLine, rec)._compute_price_unit()
            else:
                super(SaleOrderLine, rec)._compute_price_unit()
        return True

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            if not self.is_static_product:
                self.lot_id.input_line_id = self.input_line_id.id
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

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
