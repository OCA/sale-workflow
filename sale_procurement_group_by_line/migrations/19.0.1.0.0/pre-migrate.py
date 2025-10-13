from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(
        cr,
        "sale.order.line",
        "procurement_group_id",
        "stock_reference_id",
        update_references=True,
        domain_adapter=None,
        skip_inherit=(),
    )
