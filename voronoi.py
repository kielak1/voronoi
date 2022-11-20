from PIL import Image, ImageDraw
import math

class obraz:
    def __init__(self, minx=0, miny=0, maxx=30, maxy=30):
        self.hor=800
        self.ver=800
        self.minx=minx
        self.miny=miny
        self.maxx=maxx
        self.maxy=maxy
        self.horscale=self.hor/(maxx-minx)
        self.verscale=self.ver/(maxy-miny)
        self.im = Image.new("RGB", (self.hor,self.ver), "blue")
        self.dr = ImageDraw.Draw(self.im)
    def show(self):
        self.im.show()
    def draw( self, ll, kolor="White"):
        x1=ll.a.x * self.horscale
        x2=ll.b.x * self.horscale
        y2=ll.b.y * self.verscale
        y1=ll.a.y * self.verscale
        x1 = x1 - (self.minx * self.horscale)
        x2 = x2 - (self.minx * self.horscale)
        y1 = y1 - (self.minx * self.verscale)
        y2 = y2 - (self.minx * self.verscale)        
        y1=self.ver-y1
        y2=self.ver-y2        
        self.dr.line([(x1,y1),(x2,y2)], fill=kolor)

class point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def pisz(self):
            print( round(self.x,4), round(self.y,4) )
        def rowne( self, a):
            if abs( self.x - a.x ) <= 0.001 and abs(self.y-a.y) <= 0.001:
                return True
            else:
                return False
        def normal( self ):
            dlg = math.sqrt( self.x * self.x + self.y * self.y )
            if dlg == 0:
                self.x = 0
                self.y = 0
            else:
                self.x = self.x / dlg
                self.y = self.y / dlg
        def skala( self, skala ):
            self.x = self.x * skala
            self.y = self.y * skala
        def dodaj( self, p):
            return point( self.x + p.x, self.y + p.y )
        def dlug_vect( self ):
            return math.sqrt( self.x* self.x + self.y * self.y )
        def vector( self, p ):
            return point( p.x-self.x, p.y - self.y)

def midpoint( a,b):
    x = (a.x + b.x) / 2
    y = (a.y + b.y) / 2
    return point( x, y )

def SprawdzZakres(val, min, max):
    if val>=min and val <= max:
        return True
    else:
        return False

def CzyWewnatrz( x1, y1, x2, y2, x3, y3, xp, yp):
    x2 = x2 - x1
    y2 = y2 - y1
    x3 = x3 - x1
    y3 = y3 - y1
    xp = xp - x1
    yp = yp - y1
    d = x2 * y3 - x3 * y2
    w1 = xp * (y2 - y3) + yp * ( x3 - x2) + x2 * y3 - x3 * y2
    w2 = xp * y3 - yp * x3
    w3 = yp * x2 - xp * y2    
    q1 = SprawdzZakres( w1, min(0,d), max(0,d))
    q2 = SprawdzZakres( w2, min(0,d), max(0,d))
    q3 = SprawdzZakres( w3, min(0,d), max(0,d))

    return q1 and q2 and q3

class line:
    def __init__(self, a, b):
        self.a=a
        self.b=b
        self.mid=midpoint( a, b )
        self.pion=False
        self.poziom=False
        self.dlkw = (b.x-a.x) * (b.x-a.x) + (b.y-a.y) * (b.y-a.y)
        if a.x == b.x :
            self.pion=True
            self.aal=0
            self.bbl=self.mid.y      
        else:
            if a.y == b.y :
                self.poziom=True
                self.al=(b.y-a.y) / (b.x-a.x)
                self.bl=b.y-(self.al*b.x)
            else:
                self.al=(b.y-a.y) / (b.x-a.x)
                self.bl=b.y-(self.al*b.x) 
                self.aal=-1.0/(self.al)
                self.bbl=self.mid.y - (self.aal * self.mid.x)
    def czy_tylko_styka( self, l):
        if self.a.rowne(l.a) and not self.b.rowne(l.b):
            return True
        if self.a.rowne(l.b) and not self.b.rowne(l.a):
            return True
        if self.b.rowne(l.b) and not self.a.rowne(l.a):
            return True
        if self.b.rowne(l.a) and not self.a.rowne(l.b):
            return True
        return False
    def rowne( self, l):
        if self.a.rowne( l.a ) and self.b.rowne( l.b ):
            return True
        if self.a.rowne( l.b ) and self.b.rowne( l.a ):
            return True
        return False
    def pisz(self):
        print( "odcinek: (", self.a.x, ",", self.a.y,") (", self.b.x,",", self.b.y,")" )
        print( "srodek: (", self.mid.x,",", self.mid.y, ")")
        if self.pion == False:
            print( "y=",self.al,"* x +", self.bl )
        if self.poziom == False:
            print( "y=",self.aal,"* x +", self.bbl )
    def czy_rownolegle( self, r2):
        if self.pion == True:
            if r2.pion == True:
                return True
            else:
                return False
        else:
            if r2.pion == True:
                return False
        if self.poziom == True:
            if r2.poziom == True:
                return True
            else:
                return False
        else:
            if r2.poziom == True:
                return False
        if self.al==r2.al:
            return True
        else:
            return False

    def czy_zawiera( self, r2):
        if self.czy_rownolegle(r2)==False:
            return False
        else:
            if self.pion == True:
                if self.a.y > min(r2.a.y, r2.b.y) and self.a.y < max(r2.a.y, r2.b.y) and self.a.x==r2.b.x:
                    return True
                if self.b.y > min(r2.a.y, r2.b.y) and self.b.y < max(r2.a.y, r2.b.y) and self.a.x==r2.b.x:
                    return True
                if r2.a.y > min(self.a.y, self.b.y) and r2.a.y < max(self.a.y, self.b.y) and self.a.x==r2.b.x:
                    return True
                if r2.b.y > min(self.a.y, self.b.y) and r2.b.y < max(self.a.y, self.b.y) and self.a.x==r2.b.x:
                    return True
                return False
            if self.poziom == True:
                if self.a.x > min(r2.a.x, r2.b.x) and self.a.x < max(r2.a.x, r2.b.x) and self.a.y==r2.b.y:
                    return True
                if self.b.x > min(r2.a.x, r2.b.x) and self.b.x < max(r2.a.x, r2.b.x) and self.a.y==r2.b.y:
                    return True
                if r2.a.x > min(self.a.x, self.b.x) and r2.a.x < max(self.a.x, self.b.x) and self.a.y==r2.b.y:
                    return True
                if r2.b.x > min(self.a.x, self.b.x) and r2.b.x < max(self.a.x, self.b.x) and self.a.y==r2.b.y:
                    return True
                return False
            if abs( self.bl - r2.bl) >= 0.001:
                return False   
           
            if self.a.x - min(r2.a.x, r2.b.x) > 0.001 and self.a.x - max(r2.a.x, r2.b.x) < -0.001:
                return True
            if self.b.x - min(r2.a.x, r2.b.x) > 0.001 and self.b.x - max(r2.a.x, r2.b.x) < -0.001:
                return True
            if r2.a.x - min(self.a.x, self.b.x) > 0.001 and r2.a.x - max(self.a.x, self.b.x) < -0.001:
                return True
            if r2.b.x - min(self.a.x, self.b.x) > 0.001 and r2.b.x - max(self.a.x, self.b.x) < -0.001:
                return True
            return False

    def czy_przecina( self, r2 ):
        if self.czy_rownolegle( r2 ) == True:
            return False
        if self.pion == True:
            x=self.mid.x
            y=r2.al*x+r2.bl
        else:
            if r2.pion == True:
                x=r2.mid.x
                y=self.al*x+self.bl
            else:
                x = (r2.bl - self.bl) / (self.al- r2.al)
                y = self.al*x + self.bl
                  

        eps = 0.000001

        minxr2=min(r2.a.x, r2.b.x)
        maxxr2=max(r2.a.x, r2.b.x)
        minyr2=min(r2.a.y, r2.b.y)
        maxyr2=max(r2.a.y, r2.b.y)
        minxr1=min(self.a.x, self.b.x)
        maxxr1=max(self.a.x, self.b.x)
        minyr1=min(self.a.y, self.b.y)
        maxyr1=max(self.a.y, self.b.y)

        minx=max(minxr1, minxr2) - eps
        maxx=min(maxxr1, maxxr2) + eps
        miny=max(minyr1, minyr2) - eps
        maxy=min(maxyr1, maxyr2) + eps

        if x>minx and x<maxx and y>miny and y<maxy:
            return True
        return False

    def srodek( self,  r2 ):
        if self.pion == True and r2.pion == True:
            print ("ERROR")
            return point(-100000,-100000)
        if self.poziom==True and r2.poziom == True:
            print ("ERROR")
            return point(-100000,-100000)
        if self.poziom==True:
            x=self.mid.x
            y=x*r2.aal+r2.bbl            
            return point(x,y)
        if r2.poziom==True:
            x=r2.mid.x
            y=x*self.aal+self.bbl
            return point(x,y)
        if self.pion==True:
            y=self.mid.y
            x=(y-r2.bbl)/r2.aal
            return point(x,y)
        if r2.pion==True:
            y=r2.mid.y
            x=(y-self.bbl)/self.aal
            return point( x, y )           
        
        x=-(self.bbl-r2.bbl)/(self.aal-r2.aal)
        y=self.aal*x+self.bbl

        return point( x, y )
    
    def czy_na_linii( self, p ):
       
        if self.a.rowne( p ):
            return False
        if self.b.rowne( p ):
            return False
        if self.pion==True:
            if abs( self.mid.x - p.x ) < 0.001 and p.y > min(self.a.y, self.b.y ) and p.y < max(self.a.y, self.b.y):
                return True
            else:
                return False
        y = self.al*p.x + self.bl
        if abs( y - p.y ) > 0.001:
            return False
        x=p.x
        if y > min(self.a.y, self.b.y ) and y < max(self.a.y, self.b.y)  and  x > min(self.a.x, self.b.x ) and x < max(self.a.x, self.b.x)  :
            return True
        return False

class bok:
    def __init__(self, l):
        self.l = l

class trojkat:
    def __init__(self, p1, p2, p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.boki=[bok(line(p1,p2)), bok(line(p1,p3)), bok(line(p3,p2))]
        self.sboki=[0,0,0]
    def CzyWewnatrz( self, p):
        if self.p1.rowne(p) or self.p2.rowne(p) or self.p3.rowne(p):
            return False
        return CzyWewnatrz(self.p1.x, self.p1.y, self.p2.x, self.p2.y, self.p3.x, self.p3.y, p.x, p.y)
    def rowne( self, t2 ):
        if self.p1.rowne(t2.p1) and self.p2.rowne(t2.p2) and self.p3.rowne(t2.p3):
            return True
        if self.p1.rowne(t2.p1) and self.p2.rowne(t2.p3) and self.p3.rowne(t2.p2):
            return True
        if self.p1.rowne(t2.p2) and self.p2.rowne(t2.p1) and self.p3.rowne(t2.p3):
            return True
        if self.p1.rowne(t2.p2) and self.p2.rowne(t2.p3) and self.p3.rowne(t2.p1):
            return True
        if self.p1.rowne(t2.p3) and self.p2.rowne(t2.p1) and self.p3.rowne(t2.p2):
            return True
        if self.p1.rowne(t2.p3) and self.p2.rowne(t2.p2) and self.p3.rowne(t2.p1):
            return True
        return False
    def czy_wspolny_bok( self, t2):
        wsk = False
        for i in range(0,3):
            for j in range(0,3):
                if self.boki[i].l.rowne(t2.boki[j].l):
                    wsk= True
                    self.sboki[i]=1
        return wsk

    def srodek( self ):
        return self.boki[2].l.srodek(self.boki[1].l)
class trojkaty:
    def __init__(self):
        self.troj=[]
    def dodaj( self, tr):
        wsk = True
        for t in self.troj:
            if t.rowne(tr):
                wsk = False
            for b1 in t.boki:
                for b2 in tr.boki:
                    if not b1.l.rowne(b2.l):
                        if b1.l.czy_zawiera(b2.l) == True:
                            wsk = False
                        else:
                            if b1.l.czy_tylko_styka(b2.l) == False:
                                if b1.l.czy_przecina(b2.l) == True :
                                    wsk = False
        if wsk:
            self.troj.append( tr )

def czy_trojkat( p1,p2,p3):
    if p1.rowne( p2 ) or p1.rowne( p3 ) or p2.rowne(p3):
        return False
    l1=line(p1,p2)
    l2=line(p1,p3)
    if l1.czy_rownolegle(l2):
        return False
    else:
        return True

def czy_pusty_trojkat( tr, pkt ):
    wsk = True
    for p in pkt:
        if tr.CzyWewnatrz(p):
            wsk= False
    return wsk

#punkty = [point(4,10), point(8,9), point(11,4),point(4,5), point(4,2), point(14,8), point( 13,2), point(19,11), point(18,3) ]
#punkty = [point(1,1), point(1,5), point(5,5), point( 5,1), point(3,3), point( 0,2),point(4,3), point(6,3), point(3,4), point( 2,5), point(1,6), point(0,0) ]
#punkty = [point(1,4), point(5,5),   point(3,4), point( 2,5), point(1,6) ]
#punkty = [point(0,3), point(1,1), point(2,0), point( 3,0), point(4,0), point( 5,1),point(6,2)]#, point(7,3), point(1,5), point( 2,6), point(3,6), point(4,6), point(5,5), point(6,3) ]
punkty = [point(2,3), point(1,1),  point( 3,0),  point( 5,1)]#,point(6,2)]#, point(7,3), point(1,5), point( 2,6), point(3,6), point(4,6), point(5,5), point(6,3) ]

#punkty = [point(1,1), point(5,1), point(3,3)]#, point( 0,2)]#,point(4,3), point(6,3), point(3,4), point( 2,5), point(1,6), point(0,0) ]
mxx=-10000
mxy=-10000
mix=10000
miy=10000
for p in punkty:
    if p.x < mix:
        mix=p.x
    if p.x > mxx:
        mxx=p.x
    if p.y < miy:
        miy=p.y
    if p.y > mxy:
        mxy=p.y
szerokosc = mxx-mix
wysokosc = mxy-miy
rozmiar=max(szerokosc,wysokosc)
#print(mix, miy, mxx, mxy )
    
mix = round(mix - (szerokosc / 5),0)
mxx = round(mxx + (szerokosc / 5),0)
miy = round(miy - (wysokosc / 5),0)
mxy = round(mxy + (wysokosc / 5),0) 

pcentr=point( (mix+mxx)/2, (miy+mxy)/2 )
    
#print(mix, miy, mxx, mxy )


obr=obraz(mix, miy, mxx, mxy )


# skokx = ( mxx - mix ) / 600
# skoky = ( mxy - miy ) / 600
# x = mix
# while x< mxx:
#     y=miy
#     x=x+skokx
#     while y < mxy + 10:
#         y=y+skoky
#         px=point(x,y)
#         minp = punkty[0]
#         minl = 1000000000000000
#         for p in punkty:
#             l=line(px,p)
#             if minl>l.dlkw:
#                 minp = p
#                 minl = l.dlkw
#         obr.draw(line(px, px),(minp.x*20,minp.y*20,(minp.y+minp.x)*5))

troj=trojkaty()

for q in punkty:
    for w in punkty:
        for v in punkty:
            if czy_trojkat(q,w,v):
                t=trojkat( q,w,v)
                if czy_pusty_trojkat(t,punkty):
                    p0=t.srodek()
                    wsk2 = True
                    dlk=line(p0,t.boki[0].l.a).dlkw
                    for f in punkty:
                        lx=line( f, p0)
                        if dlk - lx.dlkw > 0.001:
                            wsk2=False
                    if wsk2:
                        troj.dodaj(t)

for q in punkty:
    for w in punkty:
        for v in punkty:
            if czy_trojkat(q,w,v):
                t=trojkat( q,w,v)
                if czy_pusty_trojkat(t,punkty):
                    troj.dodaj(t)

for tt in troj.troj:
    o=tt.srodek()
    tt.sboki=[0,0,0]
    for tr in troj.troj:
        if not tt.rowne(tr):
            if tt.czy_wspolny_bok( tr ):
                obr.draw( line(o, tr.srodek()), "Yellow")
    for i in range(0,3):
        if tt.sboki[ i ] == 0:
           # tt.boki[ i ].l.pisz()
            if tt.CzyWewnatrz( o ):
                print ("wewnatrz")
                px=tt.boki[i].l.mid
                obr.draw( line( o, px), (4,255,4))
                pvec = o.vector( px )
                pvec.normal()
                pvec.skala( rozmiar)
                dlg = pvec.dlug_vect()
                if dlg != 0:
                    obr.draw( line(px,px.dodaj(pvec)), (4,255,4))
                else:
                    if tt.boki[i].l.poziom == False:
                        prawo = point( px.x + 1, (px.x+1 ) * tt.boki[i].l.aal + tt.boki[i].l.bbl )
                        lewo = point( px.x - 1, (px.x-1 ) * tt.boki[i].l.aal + tt.boki[i].l.bbl )

                        prawo = o.vector( prawo )
                        lewo = o.vector( lewo )
                        prawo.normal()
                        prawo.skala(rozmiar)
                        lewo.normal()
                        lewo.skala(rozmiar)

                        prawo2=prawo.dodaj(px)
                        lewo2=lewo.dodaj(px)
                        
                        pra = line( pcentr, prawo2).dlkw
                        lew = line( pcentr, lewo2).dlkw

                        if pra > lew:
                            obr.draw( line(px,prawo2) , (124,124,40)   )
                        else:
                            obr.draw( line(px,lewo2) , (124,124,40)   )
                        


            else:  
                print ("zewnatrz")
    

for tt in troj.troj:
    for i in range(3):
        obr.draw( tt.boki[i].l, (255, 0, 0))  
for p in punkty:
    obr.draw( line( p, p))  

obr.show()
