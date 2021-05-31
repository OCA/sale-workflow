# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _name = "sale.order.type"
    _description = "Type of sale order"
    _check_company_auto = True

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("sale.seq_sale_order")
        return [("code", "=", seq_type.code)]

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=_get_domain_sequence_id,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Billing Journal",
        domain="[('type', '=', 'sale'), '|', ('company_id', '=', False), "
        "('company_id', '=', company_id)]",
        check_company=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", string="Warehouse", check_company=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company, store=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Payment Term",
        sale_order_field="payment_term_id",
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        strint="Pricelist",
        sale_order_field="pricelist_id",
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic account",
        check_company=True,
        sale_order_field="analytic_account_id",
    )
    active = fields.Boolean(default=True)
    quotation_validity_days = fields.Integer(string="Quotation Validity (Days)")
