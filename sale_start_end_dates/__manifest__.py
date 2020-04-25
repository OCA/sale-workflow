# Copyright 2014-2020 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2019 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Start End Dates",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Adds start date and end date on sale order lines",
    "author": "Akretion, Sodexis, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["account_invoice_start_end_dates", "sale"],
    "data": ["views/sale_order.xml"],
    "installable": True,
}
