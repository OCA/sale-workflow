This module extends module base_sequence_option and allow you to
provide optional sequences for sale.order documents.

To use this module, enable developer mode, and check "Use sequence options"
under Settings -> Technical -> Manage Sequence Options.

If you want to define your sequences in XML, feel free to use
demo/sale_demo_options.xml as a base for your own sequence definitions.

The demo sequences use a continuous numbering scheme, without the current year
in the generated name. To use a scheme that does include the year, set
``use_date_range`` to ``true``, and use ``%(range_year)s`` the represent the
year.
For example, to generate an invoice scheme that will generate "2024SOI00001" in
2024, try::

    <record id="seq_sale_order_individual" model="ir.sequence">
        <field name="name">Sale Order (Individual)</field>
        <field name="padding" eval="5" />
        <field name="prefix">%(range_year)sSOI</field>
        <field name="use_date_range">true</field>
    </record>

Odoo will generate the date ranges automagically when the first quotation of a year is confirmed.
