Split the automatic workflows in several independent crons.
Allow different intervals. Validating invoices takes a lot of time for instance 
but does not need to be done very fast. Confirming sales orders has to wait on 
validation on invoices, but we want this operation to be fast.
