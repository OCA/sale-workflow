# Copyright 2017 Tecnativa - Sergio Teruel
# Copyright 2017-2018 Tecnativa - Carlos Dauden
# Copyright 2017 Camptocamp SA
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Invoicing Finished Task",
    "summary": "Control invoice order lines if their related task has been "
    "set to invoiceable",
    "version": "14.0.1.1.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_timesheet"],
    "data": ["views/product_view.xml", "views/project_view.xml"],
}
