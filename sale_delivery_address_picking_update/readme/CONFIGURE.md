Go to *Inventory > Configuration > Operation Types* and open an operation
type of type *Delivery* or *Internal Transfer*. The *Auto-update Delivery
Address* option, enabled by default on these operation types, enables or
disables the automatic update for the transfers of that operation type.

Internal transfers are only affected when they belong to the sale order, i.e.
the pick and pack steps of a multi-step delivery route. Keep it enabled on
those steps: the delivery step is created from them when they are validated, so
it takes the address they have at that time.

Receipts (e.g. returns) and dropship transfers are never updated, as their
partner is not the delivery address of the sale order.

Transfers of operation types where the option is disabled keep the standard
behaviour: a warning activity is scheduled on them asking to update the
address manually.
