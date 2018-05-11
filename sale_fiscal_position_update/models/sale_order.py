# © 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# © 2014 Akretion (http://www.akretion.com)
# © 2018 Roel Adriaans <roel@road-support.nl>
# @author Mathieu Vatel <mathieu _at_ julius.fr>
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# @author Roel Adriaans <roel@road-support.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_shipping_id(self):
        fiscal_position = self.fiscal_position_id
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        if fiscal_position != self.fiscal_position_id:
            self.fiscal_position_change()
        return res

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        fiscal_position = self.fiscal_position_id
        res = super(SaleOrder, self).onchange_partner_id()
        if fiscal_position != self.fiscal_position_id:
            self.fiscal_position_change()
        return res

    @api.onchange('fiscal_position_id')
    def fiscal_position_change(self):
        """Updates taxes and accounts on all sale order lines"""
        self.ensure_one()
        res = {}
        lines_without_product = []
        fp = self.fiscal_position_id
        for line in self.order_line:
            if line.product_id:
                product = line.product_id
                account = (
                    product.property_account_income_id or
                    product.categ_id.property_account_income_categ_id)
                # M2M fields don't have an option 'company_dependent=True'
                # so we need per-company post-filtering
                taxes = product.taxes_id.filtered(
                    lambda tax: tax.company_id == self.company_id)
                taxes = taxes or account.tax_ids.filtered(
                    lambda tax: tax.company_id == self.company_id)
                if fp:
                    account = fp.map_account(account)
                    taxes = fp.map_tax(taxes)

                line.tax_id = [(6, 0, taxes.ids)]
                line.account_id = account.id
            else:
                lines_without_product.append(line.name)

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(self.order_line):
                res['warning']['message'] = _(
                    "The sale order lines were not updated to the new "
                    "Fiscal Position because they don't have products.\n"
                    "You should update the Account and the Taxes of each "
                    "Sale Order line manually.")
            else:
                res['warning']['message'] = _(
                    "The following sale order lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n- %s\nYou should update the Account and the "
                    "Taxes of these sale order lines manually."
                ) % ('\n- '.join(lines_without_product))
        return res
