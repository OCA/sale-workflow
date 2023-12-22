# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Exception Public Holidays",
    "summary": """Raise a sale exception if there is a commitment_date on
    the SO and this date is a public holidays for the shipping partner address""",
    "version": "16.0.1.0.1",
    "category": "Generic Modules/Sale",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "maintainers": ["jbaudoux"],
    "depends": ["sale_exception", "hr_holidays_public"],
    "license": "AGPL-3",
    "data": [
        "data/sale_exception_data.xml",
    ],
}
