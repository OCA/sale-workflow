Use Queue Jobs to process the Sales Automatic Workflow actions.

The default behavior of the automatic workflow module is to use a
scheduled action that searches all the record that need a workflow
action and sequentially process all of them.

It can hit some limits when the number of records is too high.

This module keeps the scheduled action to search the records, but
instead of directly executing the actions (confirm a sales order,
create invoices for a sales order, validate invoices, ...), it
creates one job per operation to do.

It uses an identity key on the jobs so it will not create the same
job for the same record and same operation twice.
