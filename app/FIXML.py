#!/usr/bin/env pythonw2.7

from lxml import etree

# constant structure

SIDE = {'buy':unicode(1), 'cover':unicode(1), 'sell':unicode(2), 'short':unicode(5)}
TIME = {'day':unicode(0), 'gtc':unicode(1), 'close':unicode(2)}
TYPE = {'market': unicode(1), 'limit': unicode(2), 'stop': unicode(3), 'slimit': unicode(4),
        'trailing': unicode('P') }

def Order(  Action = 'new',
            SecTyp = 'CS' , 
            ID     = None, 
            Sym    = 'spy', 
            Acct   = '60918935' , 
            Side   = 'buy', 
            TmInForce = 'day', 
            Typ   = 'market,',
            Px    = '0.0',
            Qty   = '1',
            CFG   = 'OC',
            PosEfct = 'O',
            ):
    # order constructor
    # Action: new, modify or cancle 
    # ID: Order ID if want modify/cancle order
    # Sym: Symbol 
    # Acct: account no.
    # SecTyp : options or stock
    # Side: buy or sell 
    # TmInForce: Order Duration 
    # Typ : Market or Limit
    # Qty : # of shares
    # 
    params = {}
    params['Action'] = Action 
    params['SecTyp'] = SecTyp
    params['ID'] = ID
    params['Sym'] = Sym
    params['Acct'] = Acct
    params['Side'] = Side
    params['TmInForce'] = TmInForce
    params['Typ'] = Typ
    params['Qty'] = Qty
    params['Px'] = Px
    params['AcctTyp'] = '5'
    params['CFI'] = CFI
    params['PosEfct'] = PosEfct
    params['MatDt'] = MatDt
    params['StrkPx']= StrkPx
    
def newOrder(Sym, Acct, SecTyp, Side, TmInForce, Typ, Qty):
    FIXML = etree.Element("FIXML", xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2")
    Order = etree.SubElement(FIXML, "Order", TmInForce=TIME[TmInForce], Typ=TYPE[Typ], Side=SIDE[Side], Acct=Acct)
    etree.SubElement(Order, "Instrmt", SecTyp=SecTyp, Sym=Sym)
    etree.SubElement(Order, "OrdQty", Qty=Qty)
    
    return FIXML
    

def changeOrder(ID, Sym, Acct, SecTyp, Side, TmInForce, Typ, Qty):
    FIXML = etree.Element("FIXML", xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2")
    Order = etree.SubElement(FIXML, "OrdCxlRplcReq", 
        TmInForce=TIME[TmInForce], Typ=TYPE[Typ], Side=SIDE[Side], Acct=Acct,
        OrigID=ID)
    etree.SubElement(Order, "Instrmt", SecTyp=SecTyp, Sym=Sym)
    etree.SubElement(Order, "OrdQty", Qty=Qty)
    
    return FIXML
    
if __name__ == '__main__':
    Order('None')
    sym = 'IBM'
    acct = '12345678'
    secTyp = 'CS'
    side = 'buy'  
    tmInForce = 'day'  
    typ = 'limit'
    qty = '1'
    fixml = newOrder(sym, acct, secTyp, side, tmInForce, typ, qty)
    xml = etree.tostring(fixml, pretty_print=True)
    print xml