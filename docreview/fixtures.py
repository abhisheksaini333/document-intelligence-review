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

def render(record,path):
    from PIL import Image,ImageDraw,ImageFont
    from pathlib import Path
    paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/Library/Fonts/Arial.ttf','/System/Library/Fonts/Supplemental/Arial.ttf']
    font_path=next((p for p in paths if Path(p).exists()),None)
    if not font_path: raise RuntimeError('Install DejaVu Sans or Arial for raster fixtures')
    image=Image.new('RGB',(1500,1000),'white');draw=ImageDraw.Draw(image);font=ImageFont.truetype(font_path,28)
    for i,line in enumerate(record['text'].splitlines()): draw.text((70,70+i*95),line,fill='black',font=font)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);image.save(path,dpi=(150,150));return path

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
