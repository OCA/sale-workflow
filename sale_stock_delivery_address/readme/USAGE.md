1. Activate the developer mode
2. Add different addresses to one partner
![partner_locations](../static/description/partner_locations.gif)
3. The rules associated with those destination locations should have
the "Destination location origin from rule" set to True. When set to True the destination location of the stock.move will be the
rule. Otherwise, it takes it from the picking type.
![rule](../static/description/img_rule.png)

4. When entering a sales order line specify a *Destination Address*.
![sale order destination address](../static/description/sale_order_destination_address.gif)
The deliveries will be split with two different destination locations:
![Transfers](../static/description/img_transfers_01.png)
5. Specify different stock locations associated to those addresses
![Source Location](../static/description/source_location.png)
The sales order procurements will be run from this location
![Transfers 2](../static/description/img_transfers_02.png)
