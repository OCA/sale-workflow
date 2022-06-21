# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 ForgeFlow S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super()._prepare_procurement_group_by_line(line)
        # for compatibility with sale_quotation_sourcing
        if line._get_procurement_group_key()[0] == 10:
            if line.warehouse_id:
                vals["name"] += "/" + line.warehouse_id.name
        return vals

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Default Warehouse",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="If no source warehouse is selected on line, "
        "this warehouse is used as default. ",
    )
