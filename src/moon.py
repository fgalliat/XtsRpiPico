"""
 Moonlight python version
 Xtase - fgalliat @ Aug 2021
"""

from machine import SPI,Pin
import uos
from random import random, seed
from utime import sleep, sleep_us, ticks_cpu, ticks_us, ticks_diff

from sdcard import SDCard
from ili9341 import Display, color565
from fb_v200 import FB_V200
from joypad import Joypad
from buzzer import Buzzer

# ===== Pins =====
SD_CHANNEL = const(1)
SD_SCK  = const(10)
SD_MOSI = const(11)
SD_MISO = const(12)
SD_CS   = const(13)

TFT_CHANNEL = const(0)
TFT_SCK  = const(18)
TFT_MOSI = const(19)
TFT_CS   = const(21)
TFT_DC   = const(17)
TFT_RST  = const(16)

PIN_LED = const(25)

# ===== Symbols =====

WHITE = color565(255,255,255)
LGRAY = color565(128,128,128)
DGRAY = color565(78,78,78)
BLACK = color565(0,0,0)
RED   = color565(255,0,0)

F_LEFT  = const(0)
F_RIGHT = const(1)
F_UP    = const(2)
F_DOWN  = const(3)

I_WEAPON = const(1)
I_POTION = const(2)

# ===== Hardware =====
seed(ticks_cpu())

spiSD = SPI(SD_CHANNEL, mosi=Pin(SD_MOSI), miso=Pin(SD_MISO), sck=Pin(SD_SCK))
sd = SDCard(spiSD,Pin(SD_CS, Pin.OUT))

vfs = uos.VfsFat(sd)
uos.mount(vfs,"/sd")
# print( uos.listdir("/sd/images") )

# ===

spiTFT = SPI(TFT_CHANNEL, baudrate=40000000, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI))
display = Display(spiTFT, dc=Pin(TFT_DC), cs=Pin(TFT_CS), rst=Pin(TFT_RST),
                  width=320, height=240, rotation = 90)

led = Pin(PIN_LED, Pin.OUT)
buzzer = Buzzer()
joy = Joypad()

display.clear()

# ===== Software =====

def openSprite(path, offset, width, height):
    with open(path, "rb") as f:
      f.seek( offset )
      sprt = f.read( width * height * 2 )
      f.close()
    return sprt

fb = FB_V200(display)

font = fb.load_uFont('fonts/mono58.bin')


#  - cars is  16x64   -- each sprite is 16x16 inside
#  - sumo is  16x128
#  - tiles is 16x112
# display.draw_image('/sd/images/sumo.raw', 130, 0, 16, 128)

SPRITE_SIZE = const(16)

def spriteOffset(spriteNum):
    return ( SPRITE_SIZE * SPRITE_SIZE * spriteNum * 2 )

led.value(1)
start = ticks_us()
sumo = openSprite( '/sd/images/sumo.raw', 0, SPRITE_SIZE, 8 * SPRITE_SIZE )
tiles = openSprite( '/sd/images/tiles.raw', 0, SPRITE_SIZE, 7 * SPRITE_SIZE )
cars = openSprite( '/sd/images/cars.raw', 0, SPRITE_SIZE, 4 * SPRITE_SIZE )
end = ticks_us()
print('Total time: {:4d} reading files'.format(end - start))
led.value(0)

def shakeScreen():
    start = ticks_us()
    x = int( (display.width - fb.width) / 2 )
    y = int( (display.height - fb.height) / 2 )
    for i in range(5):
        fb.render(x,y)
        display.fill_rectangle(x, y, 240+4, 4, BLACK)
        display.fill_rectangle(x, y, 4, 128+4, BLACK)
        fb.render(x+4,y+4)
        display.fill_rectangle(x, y+128, 240+4, 4, BLACK)
        display.fill_rectangle(x+240, y, 4, 128+4, BLACK)
        
        #display.fill_rectangle(0, 0, 250, 20, BLACK)
        #fb.render(4,4)
    end = ticks_us()
    print('Total time: {:4d} to shake screen'.format(end - start))

def drawTile(xb, yb, tileNum):
    fb.drawSprite( tiles, spriteOffset(tileNum), int(xb*SPRITE_SIZE), int(yb*SPRITE_SIZE), SPRITE_SIZE, SPRITE_SIZE )

def drawPlayer(xb, yb, faceNum):
    xb -= 0.5
    yb -= 0.5
    fb.drawSprite( sumo, spriteOffset(faceNum * 2), int(xb*SPRITE_SIZE), int(yb*SPRITE_SIZE), SPRITE_SIZE, SPRITE_SIZE )

def drawEnemy(xb, yb, faceNum):
    xb -= 0.5
    yb -= 0.5
    fb.drawSprite( cars, spriteOffset(faceNum), int(xb*SPRITE_SIZE), int(yb*SPRITE_SIZE), SPRITE_SIZE, SPRITE_SIZE )


def fPart(x):
    return ( x - int(x) )

def renderPlayer(xbf, ybf, faceNum):
    #if ( fPart(xbf) == 0 and fPart(ybf) == 0 ):
    #    drawTile(xbf, ybf, getGround( xbf, ybf ) )
    #else:
    if True:
        left = int(xbf-.5)
        top = int(ybf-.5)
        """
        # bottom face
        if ( faceNum == F_DOWN ):
            top -= 1
        # up face
        if ( faceNum == F_UP ):
            left += 1
        # right face
        if ( faceNum == F_RIGHT ):
            left -= 1
        """
        right = left+1
        bottom = top+1
        

        if ( left < 0 ) :
            left = 0
        if ( top < 0 ) :
            top = 0
        drawTile(left, top, getGround( left, top ) )
        drawTile(right, top, getGround( right, top ) )
        drawTile(left, bottom, getGround( left, bottom ) )
        drawTile(right, bottom, getGround( right, bottom ) )
    drawPlayer(xbf, ybf, faceNum)


def renderEnemy(xbf, ybf, faceNum):
    if True:
        left = int(xbf-.5)
        top = int(ybf-.5)
        right = left+1
        bottom = top+1

        if ( left < 0 ) :
            left = 0
        if ( top < 0 ) :
            top = 0
        drawTile(left, top, getGround( left, top ) )
        drawTile(right, top, getGround( right, top ) )
        drawTile(left, bottom, getGround( left, bottom ) )
        drawTile(right, bottom, getGround( right, bottom ) )
    drawEnemy(xbf, ybf, faceNum)


#       123456789012345
map  = "111111111111111"
map += "100010000000001"
map += "100010000001001"
map += "100010000100001"
map += "100010000000001"
map += "100010000000001"
map += "100010100001001"
map += "111111111111111"

def buildMap(str):
    result = []
    for i in range(len(str)):
        result.append( int( str[i] ) )
    return result


_mapW = 15
_mapH = 8
_map = buildMap( map )

def getGround(x,y):
    return _map[ (_mapW*y)+x ]

def renderMap():
    for j in range(8):
        for i in range(15):
            fb.drawSprite( tiles, spriteOffset(getGround(i,j)), i*SPRITE_SIZE, j*SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE )

# ==================================

# make player spining
#for i in range (4):
#    drawTile( 8, 5, 0 )
#    drawPlayer( 8, 5, i )
#    fb.render()
#    sleep_us(60000)

sDirty = False



"""
def toBin(a):
    bnr = bin(a).replace('0b','')
    #x = bnr[::-1]
    x=''.join(reversed(bnr))
    while len(x) < 8:
        x += '0'
    #bnr = x[::-1]
    bnr=''.join(reversed(x))
    return bnr
"""

def menu(x, y, w, h, items):
    tlen = len(items)
    if ( h < 0 ):
        h = (tlen + 2) * 8
    sel = 0
    fb.fillRect(x, y, w, h, LGRAY)
    fb.drawRect(x, y, w, h, DGRAY)
    for i in range(tlen):
            fb.drawString( x+8, y+8+(i*8), '  '+items[i], font )
            
    dirt = False
    fb.drawString( x+8, y+8+(sel*8), '>', font )
    fb.render()
    while True:
        joy.poll()
        
        if ( joy.y < -0.5 and sel > 0 ):
            fb.drawString( x+8, y+8+(sel*8), ' ', font, BLACK, LGRAY )
            sel -= 1
            sleep(0.2)
            dirt = True
        if ( joy.y > 0.5 and sel < tlen-1 ):
            fb.drawString( x+8, y+8+(sel*8), ' ', font, BLACK, LGRAY )
            sel += 1
            sleep(0.2)
            dirt = True
        
        if ( dirt == True ):
            fb.drawString( x+8, y+8+(sel*8), '>', font )
            fb.render()
            dirt = False
            
        if (joy.b == True or joy.a == True):
            sleep(0.5)
            break
    
    fb.render()
    return sel
    
# as well Player & Enemy
class Fighter:
    def __init__(self, _hp=20, _att=10, _def=10, _dex=10):
        self.hp = _hp
        self.att = _att
        self.defence = _def
        self.hpMax = 20
        self.dex = _dex

    def isDead(self):
        return self.hp <= 0
    
    def attack(self, defender):
        dex = self.dex
        att = self.att
        ad = int( (dex/2) + (random() * dex/2) )
        aa = int( (att/2) + (random() * att/2) )
        cDef = defender.defence
        
        aStrike = ( ad + aa )
        if ( aStrike <= 0 ):
            return False, 'Miss !'
        dammage = cDef - aStrike
        if ( dammage < 0 ):
            dammage = abs(dammage) * 2

        defender.hp -= dammage
        txt = 'Hit : ['+ str(dammage) +']'
        return True, txt
    
    def runaway(self):
        indice = random() * 100
        if ( indice <= self.dex ):
            return True
        return False

class Item:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.equiped = False
        self.idx = -1
        
    def use(self, player):
        # return true if consume
        if ( self.type == I_POTION ):
            player.incHp(20)
            player.remFromInventory(self)
            return True
        if ( self.type == I_WEAPON ):
            player.incAttack(10)
        self.equiped = True
        return False
    
    def unuse(self, player):
        self.equiped = False
        if ( self.type == I_WEAPON ):
            player.incAttack(-10)
        
    
    def drop(self, player):
        self.unuse(player)
        player.remFromInventory(self)

class Enemy:
    def __init__(self, x=4, y=4):
        # HP, ATT, DEF
        self.fighter = Fighter( int( random()*10)+10, int( random()*7)+7, int( random()*9)+9 )
        self.name = 'Goblin' if (self.fighter.hp < 15) else 'Dragon'
        self.loot = []
        if ( random() > 0.6 ):
            self.loot.append( Item('Healing Potion', I_POTION) )
        self.x = x
        self.y = y
        self.face = F_RIGHT
    def doesMeetPlayer(self, player):
        return ( abs( self.x - player.x ) < 0.4 and abs( self.y - player.y ) < 0.4 )
    def render(self):
        renderEnemy(self.x, self.y, self.face)

class Player:
    def __init__(self, x=5.2, y=5.2):
        self.x = x
        self.y = y
        self.face = 2
        self.inventory = []
        self.name = 'Rolph'
        self.fighter = Fighter()

    def incHp(self, v):
        # print('HP +', v)
        self.fighter.hp += v
    def incAttack(self, v):
        print('ATT +', v)
        self.fighter.att += v

    def render(self):
        renderPlayer(self.x, self.y, self.face)

    def _go(self, deltaX, deltaY, face):
        xx = self.x
        yy = self.y
        self.face = face
        xx += deltaX
        yy += deltaY
        if ( getGround( int(xx), int(yy) ) != 0 ):
            buzzer.beep(440, 50)
        else:
            self.x = xx
            self.y = yy

    def goLeft(self):
        self._go( -0.2, 0, F_LEFT)
    def goRight(self):
        self._go(  0.2, 0, F_RIGHT)
    def goUp(self):
        self._go( 0, -0.2, F_UP)
    def goDown(self):
        self._go( 0,  0.2, F_DOWN)
    
    def _dispInventory(self):
        fb.fillRect(20, 20, 240-40, 128-40, LGRAY)
        fb.drawRect(20, 20, 240-40, 128-40, DGRAY)
        fb.drawString( 22+2, 22, '-= '+self.name+' Inventory =-  [ HP: '+ str(self.fighter.hp) +' ]', font )
        fb.drawSprite( sumo, spriteOffset(F_DOWN * 2), 220-2-16, 22, SPRITE_SIZE, SPRITE_SIZE, WHITE )
        
        tlen = len(self.inventory)
        if tlen == 0:
            fb.drawString( 28, 38+(0*8), '  [ Empty ]', font )
        
        for i in range(tlen):
            eqp = '*' if (self.inventory[i].equiped == True) else ' '
            fb.drawString( 28, 38+(i*8), '  '+self.inventory[i].name+' ('+ eqp +')', font )
    
    def dispInventory(self):
        tlen = len(self.inventory)
        self._dispInventory()
            
        dirt = False
        sel = 0
        fb.drawString( 28, 38+(sel*8), '>', font )
        fb.render()
        while True:
            joy.poll()
            
            if ( joy.y < -0.5 and sel > 0 ):
                fb.drawString( 28, 38+(sel*8), ' ', font, BLACK, LGRAY )
                sel -= 1
                sleep(0.2)
                dirt = True
            if ( joy.y > 0.5 and sel < tlen-1 ):
                fb.drawString( 28, 38+(sel*8), ' ', font, BLACK, LGRAY )
                sel += 1
                sleep(0.2)
                dirt = True
            
            if ( dirt == True ):
                fb.drawString( 28, 38+(sel*8), '>', font )
                fb.render()
                dirt = False
                
            if (joy.a == True):
                # exit game
                sleep(0.2)
                break
            
            if (joy.b == True):
                sleep(0.2)
                if tlen == 0:
                    self.inventory[sel].use()
                    break
                choice = menu(220-2-(10*6), 96-(4*8), 10*6, -1, [ 'Use', 'Drop', 'Return' ] )
                if ( choice == 0 ): # Use / Unuse
                    itm = self.inventory[sel]
                    if (itm.equiped == True):
                        itm.unuse( self )
                    else:
                        rem = itm.use( self )
                if ( choice == 1 ): # Drop
                    itm.drop( self )
                sel = 0
                tlen = len(self.inventory)
                self._dispInventory()
                dirt = True
        
        fb.render()
        
    def reindexInventory(self):
        tlen = len(self.inventory)
        for i in range(tlen):
            self.inventory[i].idx = i

    def addToInventory(self, itm):
        self.inventory.append(itm)
        self.reindexInventory()
        
    def remFromInventory(self, itm):
        self.inventory.pop(itm.idx)
        self.reindexInventory()

player = Player()

healP = Item('Healing Potion', I_POTION)
dagger = Item('Dagger', I_WEAPON)

player.addToInventory(healP)
player.addToInventory(dagger)

enemies = [ Enemy(8, 4) , Enemy(12, 4) ]

# ===============================

renderMap()
player.render()
fb.render()

shakeScreen()
fb.render()
# sleep_us(500000)


def gameLoop(sDirty=sDirty, player=player, enemies=enemies):
    sDirty = True
    while( True ):
        joy.poll()
        
        if ( joy.x < -0.5 and player.x > 0.2 ):
            player.goLeft()
            sDirty = True
        if ( joy.y < -0.5 and player.y > 0.2 ):
            player.goUp()
            sDirty = True
        if ( joy.x > 0.5 and player.x < 13.8 ):
            player.goRight()
            sDirty = True
        if ( joy.y > 0.5 and player.y < 6.8 ):
            player.goDown()
            sDirty = True

        ejectLoop = False
        for i in range(len(enemies)):
            if ( ejectLoop ):
                break
            enem = enemies[i]
            enem.render()
            if ( enem.doesMeetPlayer(player) ):
                fight(enem)
                if ( enem.fighter.isDead() ):
                    print('Will remove #', i, 'on', len(enemies) )
                    enemies.pop(i)
                    ejectLoop = True
                
                renderMap()
                player.render()
                fb.render()
                sleep(0.2)
                joy.poll()
                
        if ( player.fighter.isDead() ):
            break

        if ( sDirty == True ):
            player.render()
            fb.render()
            sDirty = False
            
        if ( joy.a == True ):
            break
        if ( joy.b == True ):
            sleep(0.2)
            player.dispInventory()
            renderMap()
            player.render()
            sDirty = True
            
        
    fb.fill( DGRAY )
    fb.drawString(20, 40, 'Game Over', font)
    fb.render()


def printPlayerStat(player):
    print('('+ player.name +') HP: '+str(player.fighter.hp))

def printEnemyStat(enemy):
    print('('+ enemy.name +') HP: '+str(enemy.fighter.hp))

def fight(enem0):
    #enem0.render()
    #fb.render()
    
    fItems = ['Attack', 'Spell', 'Item', 'Runaway']
    
    fb.fillRect(20, 20, 240-40, 128-40, LGRAY)
    fb.drawRect(20, 20, 240-40, 128-40, DGRAY)
    fb.drawSprite( sumo, spriteOffset(F_DOWN * 2), 220-2-16, 22, SPRITE_SIZE, SPRITE_SIZE, WHITE )
    
    fb.drawString( 22+2, 22, '-= '+player.name+' Battle =-  [ HP: '+ str(player.fighter.hp) +' ]', font, BLACK, LGRAY )
    fb.drawString( 22+2, 22+8, ' Vs '+enem0.name+'  [ HP: '+ str(enem0.fighter.hp) +' ]', font, BLACK, LGRAY )

    fb.render()

    
    printPlayerStat(player)
    printEnemyStat(enem0)

    while not ( player.fighter.isDead() or enem0.fighter.isDead() ):
        choice = menu(160, 70, 11*6, -1, fItems )
        
        if ( choice == 3 ):
            if ( player.fighter.runaway() ):
                print('You escaped !')
                break
            else:
                print('Failed to escape')
                fb.drawString( 22+2, 22+24, 'Failed to escape', font, BLACK, LGRAY )

        elif ( choice == 0 ):
            striked, txt = player.fighter.attack(enem0.fighter)
            print(' Player turn : '+ txt)
            fb.drawString( 22+2, 22+24, ' Player turn : '+ txt, font, BLACK, LGRAY )
            if ( not striked ):
                    print(' Miss !')
                    fb.drawString( 22+2, 22+32, ' Miss !', font, BLACK, LGRAY )
            
            if ( not enem0.fighter.isDead() ):
                striked, txt = enem0.fighter.attack(player.fighter)
                print(' Opponent turn : '+ txt)
                fb.drawString( 22+2, 22+24+24, ' Opponent turn : '+ txt, font, BLACK, LGRAY )
                if ( not striked ):
                    print(' Miss !')
                    fb.drawString( 22+2, 22+32+24, ' Miss !', font, BLACK, LGRAY )

            #printPlayerStat(player)
            #printEnemyStat(enem0)
            fb.drawString( 22+2, 22, '-= '+player.name+' Battle =-  [ HP: '+ str(player.fighter.hp) +' ]   ', font, BLACK, LGRAY )
            fb.drawString( 22+2, 22+8, ' Vs '+enem0.name+'  [ HP: '+ str(enem0.fighter.hp) +' ]   ', font, BLACK, LGRAY )
            fb.render()
                   
    if ( player.fighter.isDead() ):
        print( 'You\'re dead adventure stops here' )
    else:
        print( 'Opponent\'s dead ..' )

if not True:
    enem0 = enemies[0]
    fight(enem0)

if True :
    gameLoop()
