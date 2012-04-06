#!/usr/bin/env pythonw2.7

from lxml import etree

# constant structure

SIDE = {'buy':unicode(1), 'cover':unicode(1), 'sell':unicode(2), 'short':unicode(5)}
TIME = {'day':unicode(0), 'gtc':unicode(1), 'close':unicode(2)}
TYPE = {'market': unicode(1), 'limit': unicode(2), 'stop': unicode(3), 'slimit': unicode(4),
        'trailing': unicode('P') }



def newOrder(Sym, Acct, SecTyp, Side, TmInForce, Typ, Qty):
    FIXML = etree.Element("FIXML", xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2")
    Order = etree.SubElement(FIXML, "Order", TmInForce=TIME[TmInForce], Typ=TYPE[Typ], Side=SIDE[Side], Acct=Acct)
    etree.SubElement(Order, "Instrmt", SecTyp=SecTyp, Sym=Sym)
    etree.SubElement(Order, "OrdQty", Qty=Qty)
    
    return FIXML
    

if __name__ == '__main__':
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