#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleGenerator(models.Model):
    _name = "sale.generator"
    _description = "Sale order generator"

    name = fields.Char(string="Generator", default="/")
    partner_ids = fields.Many2many(
        comodel_name="res.partner", string="Partner"
    )
    sale_ids = fields.One2many(
        comodel_name="sale.order", inverse_name="generator_id", string="Sales"
    )
    tmpl_sale_id = fields.Many2one(
        comodel_name="sale.order", string="Sale Template", required=True,
    )
    date_order = fields.Datetime(string="Date", default=fields.Datetime.now())
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", required=True, string="Warehouse"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generating", "Generating Order"),
            ("done", "Done"),
        ],
        string="State",
        readonly=True,
        default="draft",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="warehouse_id.company_id",
        store=True,
    )

    def _prepare_copy_vals(self, partner):
        self.ensure_one()
        vals = {
            "partner_id": partner.id,
            "generator_id": self.id,
            "warehouse_id": self.warehouse_id.id,
            "company_id": self.warehouse_id.company_id.id,
        }
        return vals

    def _create_order_for_partner(self, partner):
        self.ensure_one()
        vals = self._prepare_copy_vals(partner)
        vals["active"] = True
        vals["is_template"] = False
        self.tmpl_sale_id.copy(vals)

    def button_generate_sale_orders(self):
        for res in self:
            if not res.partner_ids:
                raise UserError(
                    _(
                        "Can't generate sale order without selecting any "
                        "customer"
                    )
                )
            else:
                res.write({"state": "generating"})
                res._sync_orders_with_partners()

    def _sync_orders_with_partners(self):
        self.ensure_one()
        partners_with_order = self.sale_ids.mapped("partner_id")
        for partner in self.partner_ids.filtered(
            lambda record: record not in partners_with_order
        ):
            self._create_order_for_partner(partner)
        for sale in self.sale_ids.filtered(
            lambda record: record.partner_id not in self.partner_ids
        ):
            sale.unlink()

    def action_confirm(self):
        for rec in self:
            rec.write({"state": "done"})
            # need single record action_confirm or else it crashes with
            # sale_timesheet: sale_order.py:54 see self.company_id
            for sale in rec.sale_ids:
                sale.action_confirm()

    def write(self, vals):
        res = super().write(vals)
        if "partner_ids" in vals and self.state == "generating":
            self._sync_orders_with_partners()
        return res

    def add_generated_partner(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "name": u"New Customer",
            "view_mode": "form",
            "target": "new",
        }

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("sale.order.generator")
                or "/"
            )
        return super().create(vals)
