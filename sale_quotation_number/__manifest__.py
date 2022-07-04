# Copyright 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale Quotation Numeration",
    "summary": "Different sequence for sale quotations",
    "version": "15.0.1.0.1",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Elico Corp, "
    "Agile Business Group, "
    "Qubiq, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management"],
    "data": ["data/ir_sequence_data.xml", "views/sales_config.xml"],
}
