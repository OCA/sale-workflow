# -*- coding: utf-8 -*-
{
    "name": "Analytic Accounts / Contracts Department Categorization",
    "version": "1.0",
    "author": "Camptocamp, Daniel Reis",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "description": """\
Add Department to Timesheets (hr.analytic.timesheet) and to corresponding tree,
search and form  views.
""",
    "website": "http://camptocamp.com",
    "depends": ["hr_timesheet", "analytic_department"],
    "data": ["hr_timesheet_view.xml"],
    "auto_install": True,
    "installable": False,
}
