from decimal import Decimal
LABELS=('invoice','purchase_order','receipt')
HEADINGS={
 'invoice':['INVOICE','BILL FOR SERVICES','TAX INVOICE','PAYMENT REQUEST','AMOUNT DUE'],
 'purchase_order':['PURCHASE ORDER','ORDER AUTHORIZATION','PROCUREMENT ORDER','SUPPLIER ORDER','PURCHASE REQUEST'],
 'receipt':['RECEIPT','PAYMENT RECEIVED','SALES RECEIPT','TRANSACTION CONFIRMATION','PROOF OF PAYMENT']}
DESCRIPTIONS={
 'invoice':'Please remit payment. Accounts receivable. Due date. Net 30 terms.',
 'purchase_order':'Ship ordered goods to buyer. Authorized procurement. Delivery instructions.',
 'receipt':'Paid in full. Thank you for your purchase. Card payment approved.'}

def records():
    rows=[]
    for label in LABELS:
      for layout in range(5):
       for sample in range(12):
        number=f'{label[:2].upper()}-{layout+1}{sample+101}'
        subtotal=Decimal(100+sample*13+layout*7)
        tax=subtotal*Decimal('.10'); total=subtotal+tax
        fields={'number':number,'date':f'2022-05-{sample+1:02d}','subtotal':f'{subtotal:.2f}','tax':f'{tax:.2f}','total':f'{total:.2f}','currency':'USD'}
        lines=[HEADINGS[label][layout],f'Vendor: Synthetic Supplier {layout+1}',f'Number: {number}',f'Date: {fields["date"]}',DESCRIPTIONS[label],f'Subtotal: USD {subtotal:.2f}',f'Tax: USD {tax:.2f}',f'Total: USD {total:.2f}']
        if layout%2: lines[2:4]=reversed(lines[2:4])
        rows.append({'id':f'{label}-{layout}-{sample}','family':f'{label}-layout-{layout}','label':label,'text':'\n'.join(lines),'fields':fields,'synthetic':True})
    return rows
