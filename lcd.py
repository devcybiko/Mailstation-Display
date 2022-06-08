import RPi.GPIO as GPIO
import time
import dotmat5x7

__all__=["setup", "teardown", "clear_screen", "write_byte", "read_byte", "set_pixel", "select_column", "display_image", "print_at", "defer"]

_DELAY=0
_DISP_EN=19
_LEFT_SEL_=23
_COL_ADD_SEL_=21
_WRITE_=22
_RIGHT_SEL_=20
_READY_IN=27
_A=[2,3,4,5,6,7,8,9]
_D=[11,12,13,14,15,16,17,18]
_zeroes = [0] * 8
_left_bit = 0
_right_bit = 0
_buffered_read = False

_buffer=[]
_row=0
_col=0
_defer = False

def defer(b):
    global _defer
    _defer = b
    if not _defer: _display_buffer()

def _byte_to_arr(byte):
    arr = [byte & 0x01, byte & 0x02, byte & 0x04, byte & 0x08, byte & 0x10, byte & 0x20, byte & 0x040, byte & 0x80]
    return arr

def _usleep(us):
    if us == 0: return
    time.sleep(us/1000000.0)

def setup(delay=0, double_buffer=True):
    global _DELAY, _buffered_read
    _DELAY = delay
    _buffered_read=double_buffer
    for i in range(0, 256):
        _buffer.append([0]*40)
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM) ### or GPIO.BOARD
    for i in range(0, 28):
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)
    GPIO.output(_DISP_EN, 1)

def teardown():
    GPIO.output(_DISP_EN, 0)
    GPIO.cleanup()

def write_byte(byte, row, col=None):
    global _DELAY, _row, _col, _buffer
    if col != None: select_column(col)
    _row = row
    _buffer[_row][_col] = byte
    # if byte: print("write", _row, _col, byte)
    if _defer: return
    row_arr = _byte_to_arr(row)
    byte_arr = _byte_to_arr(byte)
    GPIO.output(_A, row_arr)
    GPIO.output(_D, byte_arr)
    GPIO.output(_LEFT_SEL_, not _left_bit)
    GPIO.output(_RIGHT_SEL_, not _right_bit)
    GPIO.output(_WRITE_, 0)
    _usleep(_DELAY)
    GPIO.output(_WRITE_, 1)
    GPIO.output(_LEFT_SEL_, 1)
    GPIO.output(_RIGHT_SEL_, 1)

def clear_screen(byte=0, byte2=None):
    if byte2 == None: byte2 = byte
    for col in range(0, 40, 1):
        select_column(col)
        start = 0x0
        end = 0xff
        for row in range(start, end):
            if row % 2 == 0: write_byte(byte, row)
            else: write_byte(byte2, row)

def select_column(col):
    global _right_bit, _left_bit, _DELAY, _row, _col, _defer
    _col=col
    if _defer: return
    if col < 20:
        _left_bit = 1
        _right_bit = 0
    else:
        _left_bit = 0
        _right_bit = 1
    col = col % 20
    col_arr=_byte_to_arr(col)
    GPIO.output(_A, _zeroes)
    GPIO.output(_D, col_arr)
    GPIO.output(_LEFT_SEL_, not _left_bit)
    GPIO.output(_RIGHT_SEL_, not _right_bit)
    GPIO.output(_WRITE_, 0)
    GPIO.output(_COL_ADD_SEL_, 0)
    _usleep(_DELAY)
    GPIO.output(_COL_ADD_SEL_, 1)
    GPIO.output(_WRITE_, 1)
    GPIO.output(_LEFT_SEL_, 1)
    GPIO.output(_RIGHT_SEL_, 1)

def _display_buffer():
    ### image is an array of bytes in row-major form
    ### image[128][40]
   for col in range(0,40):
      select_column(col)
      for row in range(0x38,0xb8):
        write_byte(_buffer[row][col], row)
        pass

def display_image(image):
    ### image is an array of bytes in row-major form
    ### image[128][40]
   for col in range(0,40):
      select_column(col)
      for row in range(0,128):
         write_byte(image[row][col], row+0x38)

def _set_inputs():
    for i in _D:
        GPIO.setup(i, GPIO.IN)
    _usleep(_DELAY)

def _set_outputs():
    for i in _D:
        GPIO.setup(i, GPIO.OUT)
    _usleep(_DELAY)
    
def read_byte(row, col=None):
    global _DELAY, _row, _col, _buffer, _buffered_read
    if _buffered_read:
        _col = col
        _row = row
        # print("buffered_read", _row, _col, _buffer[_row][_col])
        return _buffer[_row][_col]
    if col != None: select_column(col)
    row_arr = _byte_to_arr(row)
    GPIO.output(_A, row_arr)
    GPIO.output(_LEFT_SEL_, not _left_bit)
    GPIO.output(_RIGHT_SEL_, not _right_bit)
    _set_inputs()
    byte = GPIO.input(_D[0])
    byte += GPIO.input(_D[1]) << 1
    byte += GPIO.input(_D[2]) << 2
    byte += GPIO.input(_D[3]) << 3
    byte += GPIO.input(_D[4]) << 4
    byte += GPIO.input(_D[5]) << 5
    byte += GPIO.input(_D[6]) << 6
    byte += GPIO.input(_D[7]) << 7
    GPIO.output(_LEFT_SEL_, 1)
    GPIO.output(_RIGHT_SEL_, 1)
    _set_outputs()
    return byte


_mask = [0x7f, 0xbf, 0xdf, 0xef, 0xf7, 0xfb, 0xfd, 0xfe]
_bit = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

def set_pixel(x, y, bit):
    row = y + 0x38
    col = x >> 3
    offset = x & 0x07
    byte = read_byte(row, col)
    if bit: byte = byte | _bit[offset]
    else: byte = byte & _mask[offset]
    write_byte(byte, row, col)

def get_pixel(x, y, bit):
    row = y + 0x38
    col = x >> 3
    offset = x & 0x07
    byte = read_byte(row, col)
    return 1 if byte & _mask[offset] else 0

def print_at(x, y, s, width=None):
    if width != None: return print_at_proportional(x, y, s, width)
    r = int (y / 8) * 8
    c = int (x / 8)
    for i in range(0, len(s)):
        col = c + i
        if col >= 40: break
        select_column(col)
        dots = dotmat5x7.dots[ord(s[i:i+1])-32]
        for j in range(0, len(dots)):
            row = r + 8 - j
            write_byte(dots[j], row+0x38)

def print_at_proportional(x, y, s, _width=None):
    for i in range(0, len(s)):
        col = int(x / 8)
        shift = x % 8
        if col >= 40: break
        select_column(col)
        c = ord(s[i:i+1])-32
        dots = dotmat5x7.dots[c]
        width = dotmat5x7.widths[c] if _width==0 else _width
        for j in range(0, len(dots)):
            row = y + 7 - j + dotmat5x7.descenders[c]
            screen_byte = read_byte(row+0x38, col)
            dot_byte = (dots[j] << (8-width)) >> shift
            new_screen_byte = (screen_byte | dot_byte) & 0xff
            # print(row, col, hex(new_screen_byte), hex(screen_byte), hex(dots[j]), hex(dot_byte), width, shift)
            write_byte(new_screen_byte, row+0x38, col)
            if col == 39: continue
            screen_byte = read_byte(row+0x38, col+1)
            dot_byte = (dots[j] <<  (8-width)) << (8 - shift)
            screen_byte = screen_byte | dot_byte
            write_byte(screen_byte, row+0x38, col+1)
        x += width + 1
