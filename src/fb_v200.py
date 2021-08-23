"""
 
 FrameBuffer TiV200 like
 240 x 128 (in color 565)
 
 TODO :
  - drawChar
  - drawLine
  - drawRect
 
"""
import ustruct

# only for tests
import ili9341

class MicroFont:
    def __init__(self, path):
        glyphs, bpl, height = self.load_uFont(path)
        self.glyphs = glyphs # use memoryview ?
        self.bpl = bpl
        self.height = height

    # microFonts support (see fontparser.py)
    def load_uFont(self, path):
        letter_count=96
        with open(path, 'rb') as f:
            bytes_per_letter = f.read(1)[0]
            height = f.read(1)[0]
            glyphs = f.read()
            f.close()
        return glyphs, bytes_per_letter, height
        

class FB_V200:
    def __init__(self, display):
        self.display = display
        self.width = 240
        self.height = 128
        self.fb = bytearray( self.width * self.height * 2 ) # 61440 bytes 0x00 feeded

    def swap16(self, x: int):
        # return int.from_bytes(x.to_bytes(2, byteorder='little'), byteorder='big', signed=False)
        return int( ustruct.unpack("<H", ustruct.pack(">H", x))[0] )


    # Cf speed optim
    @micropython.viper
    def fill(self, color: uint):
        _color = uint( self.swap16( color ) )
        buf = ptr16(self.fb)
        _len = int( self.width * self.height )
        for x in range(_len):
            buf[x] = _color

    @micropython.viper
    def drawSpriteFast(self, bytesA: ptr16, offset: int, x: int, y: int, w: int, h: int, transparency: int=-1):
        _transpa = uint(transparency)
        if (transparency != -1):
            _transpa = uint( self.swap16(transparency) )

        buf = ptr16(self.fb)
        for yy in range(0, h):
            for xx in range(0, w):
                addr = int( (offset >> 1) + ( (w * yy) + xx )  ) # as u16 : div offset by 2
                color = uint( bytesA[addr] )
                if ( color != _transpa ):
                    _addr = ((y+yy) * 240) + (x+xx)
                    buf[ _addr ] = color

    def drawSprite(self, bytesA, offset, x, y, w, h, transparency=-1):
        self.drawSpriteFast(bytesA, offset, x, y, w, h, transparency)


    @micropython.viper
    def fillRectFast(self, x: int, y: int, w: int, h: int, color: int):
        _color = uint(self.swap16(color))
        # ww = self.width
        ww = 240
        buf = ptr16(self.fb)
        
        for yy in range(0, h):
            for xx in range(0, w):
                _addr = ((y+yy) * ww) + (x+xx)
                buf[ _addr ] = _color

    def fillRect(self, x, y, w, h, color):
        self.fillRectFast( x, y, w, h, color)

    def drawRect(self, x, y, w, h, color):
        self.fillRectFast( x, y, w, 1, color)
        self.fillRectFast( x, y+h-1, w, 1, color)
        self.fillRectFast( x, y, 1, h, color)
        self.fillRectFast( x+w-1, y, 1, h, color)



    def drawPx(self, x,y,color):
        addr = (self.width*2*y)+(x*2)
        self.fb[ addr ] = color >> 8
        self.fb[ addr+1 ] = color % 256
        

    def render(self, x=-1, y=-1):
        if ( x < 0 ):
            x = int( (self.display.width - self.width) / 2 )
        if ( y < 0 ):
            y = int( (self.display.height - self.height) / 2 )
        self.display.draw_sprite( self.fb, x, y, self.width, self.height)

    # microFonts support (see fontparser.py)
    def load_uFont(self, path):
        return MicroFont(path)

    def drawString(self, xt, yt, str: string, font, color=0, bgColor=-1):
        for i in range(len(str)):
            ch = str[i]
            charAddr = ( ( ord(ch) - 32 ) * font.bpl )
            if ( charAddr < 0 ):
                continue
            charWidth = bte = font.glyphs[ charAddr+0 ]
            for yy in range(font.height):
                for xx in range(charWidth):
                    pt = ( font.glyphs[ charAddr+1+xx] >> ( yy ) ) & 1
                    if ( pt == 1 ):
                        self.drawPx(xt+xx, yt+yy, color)
                    elif ( bgColor > -1 ):
                        self.drawPx(xt+xx, yt+yy, bgColor)
            xt += charWidth

def test():
    spiTFT = machine.SPI(0, baudrate=40000000, sck=machine.Pin(18), mosi=machine.Pin(19))
    display = ili9341.Display(spiTFT, dc=machine.Pin(17), cs=machine.Pin(21), rst=machine.Pin(16),
                      width=320, height=240, rotation = 90)

    fb = FB_V200(display)
    RED = ili9341.color565(255, 0, 0)
    WHITE = ili9341.color565(255, 255, 255)
    BLUE = ili9341.color565(0, 0, 255)
    GREEN = ili9341.color565(0, 255, 0)
    
    fb.fill( RED )
    font = fb.load_uFont('fonts/mono58.bin')
    fb.drawString( 20, 20, 'Coucou tout le monde', font, WHITE )
    fb.drawString( 20, 20+8, 'Coucou tout le monde', font, WHITE, BLUE )
    fb.fillRect( 20, 40, 150, 40, GREEN )
    fb.drawRect( 20, 40, 150, 40, BLUE )
    fb.render()


if not True:
    test()
