import re
from decimal import Decimal
from .domain import Field,Box
from .normalize import amount,document_date

def lines(tokens):
    groups=[]
    for token in sorted(tokens,key=lambda t:(t.page,t.box.y,t.box.x)):
        group=next((g for g in reversed(groups) if g[0].page==token.page and abs(g[0].box.y-token.box.y)<=max(g[0].box.height,token.box.height)*.5),None)
        if group is None: groups.append([token])
        else: group.append(token)
    result=[]
    for group in groups:
        group.sort(key=lambda t:t.box.x);x=min(t.box.x for t in group);y=min(t.box.y for t in group)
        box=Box(x,y,max(t.box.x+t.box.width for t in group)-x,max(t.box.y+t.box.height for t in group)-y)
        result.append({'text':' '.join(t.text for t in group),'page':group[0].page,'box':box,'confidence':sum(t.confidence for t in group)/len(group)/100})
    return result
