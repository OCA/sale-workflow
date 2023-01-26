# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 - 2019 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Triple Discount",
    "version": "16.0.1.0.1",
    "category": "Sales",
    "author": "ADHOC SA, Agile Business Group, Tecnativa, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "summary": "Manage triple discount on sale order lines",
    "depends": ["sale_management", "account_invoice_triple_discount"],
    "data": ["views/sale_order_report.xml", "views/sale_order_view.xml"],
    "installable": True,
}
