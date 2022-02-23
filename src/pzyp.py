"""
This is a work of our python class, we're implementing a compressor/decompressor using the LZSS method

    Usage:
        pzyp.py [-c [-l LEVEL] | -d] [-sh] [-p PASSWORD] FILE

    Options: (some of the options will be implemented after)
        -h, --help                  show this text
        -c, --compress              compress FILE
        -d, --decompress            decompress FILE
        -l, --comprlevel=LEVEL      compressing LEVEL [default: 2]
        -s, --sumary                meta-info of compressed FILE
        -p, --password=PASSWORD     establishes a PASSWORD for FILE encription

    LEVEL: is an int that ranges between 1 and 4; the
    compression LEVEL affects the window dimension(size of buffer)
    and the maximum size sequence.(to be implemented)

    Level 1: W =  1 KB ⇒10 bits    M = 15 + 2 ⇒4 bits
    Level 2: W =  4 KB⇒12 bits    M = 15 + 3⇒4 bits
    Level 3: W = 16 KB ⇒ 14 bits   M = 32 + 3 ⇒ 5 bits
    Level 4: W = 32 KB ⇒ 15 bits   M = 32 + 3 ⇒ 5 bits


    The output file will have the same name as the FILE with the extension .LZS

    This is only the first part of our work and the deadline is the 13th of february.

    The members of the group are:

    Carlos Mendes,
    Filipe Cavaco,
    Maria João Claro    
"""
LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}

ARGS = docopt(__doc__)

FILE_EXTENTION = 'lzs'

ENCODED_OFFSET_SIZE=LEVEL[int(ARGS['--comprlevel'])][0]


class PzypError(ValueError):
    pass


from collections import deque
import os
import sys
from typing import BinaryIO
from docopt import docopt
import time
import struct
import io
import math
from typing import Union, BinaryIO, Tuple
import bitstruct
from bitarray import bitarray
from cryptography.fernet import Fernet
import base64, hashlib
from curses import window
import sys
from collections import deque
import os
from lzss_io import LZSSWriter, PZYPContext
import io


LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}

ARGS = docopt(__doc__)

FILE_EXTENTION = 'lzs'
ENCODING = "utf-8"

ENCODED_OFFSET_SIZE=LEVEL[int(ARGS['--comprlevel'])][0]
ENCODED_LEN_SIZE=LEVEL[int(ARGS['--comprlevel'])][1]
UNENCODED_STRING_SIZE = 8   # in bits
ENCODED_STRING_SIZE = ENCODED_OFFSET_SIZE + ENCODED_LEN_SIZE  # in bits
WINDOW_SIZE = 2 ** ENCODED_OFFSET_SIZE        # in bytes
BREAK_EVEN_POINT = ENCODED_STRING_SIZE // 8   # in bytes
MIN_STRING_SIZE = BREAK_EVEN_POINT + 1        # in bytes
MAX_STRING_SIZE = 2 ** ENCODED_LEN_SIZE - 1  + MIN_STRING_SIZE 

class Window:
    def __init__(self, ctx=PZYPContext()):
        self._dictionary = deque(maxlen=2 ** ctx.encoded_offset_size)
      
    
    def extendDictionary(self ,data):
        self._dictionary.extend(data)

    def extend(self, data: bytes):
        self._dictionary.append(data)
        if len(self._dictionary) >= self._dictionary.maxlen:
            self._dictionary.popleft()

    def find(self, check_elements):
        i = 0
        offset = 0
        for element in self._dictionary:
            if len(check_elements) <= offset:
                # All of the elements in check_elements are in elements
                return i - len(check_elements)

            if check_elements[offset] == element:
                offset += 1
            else:
                offset = 0

            i += 1
        return -1

def head_writer(self, win_dimention, max_seq, file_name):
        dt = time.time()
        with open(f"{ARGS['FILE']}.{FILE_EXTENTION}", 'wb+') as f:
            f.write(struct.pack('>iid', win_dimention, max_seq, dt))
            f.write(struct.pack('{}s'.format(len(file_name)), bytes(file_name, ENCODING)))
            f.write('\n'.encode(ENCODING))
        print("Header ready")


def head_reader(file_name, size):
        with open(file_name, 'rb') as f:
            s_list=list(struct.unpack(f'>iid {size}s', f.readline()))
        dt_sec = s_list[2]
        dt = time.ctime(dt_sec)
        print(f'File name: {str(s_list[3])}')
        print(f'Compression date/time:  {dt}')
        print(f'Compression parameters : Buffer -> {2**s_list[0]} ({s_list[0]} bits),')
        if s_list[0] == 10:
            print('Max Seq. Len. -> 17 (4 bits)')
        elif s_list[0] == 12:
            print('Max Seq. Len. -> 18 (4 bits)')
        else:
            print('Max Seq. Len. -> 35 (5 bits)')

def genwrite_key(file, password):
    hexadecimalPassword = hashlib.md5(password.encode()).hexdigest()
    key_64 = base64.urlsafe_b64encode(hexadecimalPassword.encode())
    with open(f'{file}.key', "wb") as key_file:
        key_file.write(key_64)
        
def call_key(file):
    return open(f'{file}.key', "rb").read()

def openFile(location):
    file = open(location, 'rb')
    content = file.read()
    file.close()
    return content


def encode(in_: BinaryIO, out: BinaryIO, lzss_writer=None, ctx=PZYPContext()):
    with (lzss_writer or LZSSWriter(out, ctx)) as lzss_out:
        window = Window(ctx)
        check_characters = []
        text = in_.read()
        i = 0
        for char in text:
            check_characters.append(char)
            index = window.find(check_characters)

            if index == -1 or i == len(text) - 1:
                if len(check_characters) > 1:
                    index = window.find(check_characters[:-1])
                    if index <= MAX_STRING_SIZE:
                        offset = i - index - len(check_characters) + 1 
                        length = len(check_characters) 
                        token = f"<{offset},{length}>" 

                    if len(token) > length:
                        for byte_ in check_characters:
                            lzss_out.write(bytes((byte_,)))
                    else:
                        lzss_out.write((offset, length))
                else:
                    lzss_out.write(bytes((char,)))

                check_characters = []

            window.extend(char)

            i += 1


def decode(in_: BinaryIO, out: BinaryIO, lzss_reader=None, ctx=PZYPContext()):
    with (lzss_reader or LZSSReader(in_, ctx)) as lzss_in:
        pass
    #faltam coisas aqui


def get_fileName():
    head, tail = os.path.split(ARGS['FILE'])
    fileName=tail
    result=fileName.split('.')
    return result[0]

def encryptFile():
    pass
 #falta por coisas aqui

def main():
    ctx = PZYPContext(
        encoded_offset_size=LEVEL[int(ARGS['--comprlevel'])][0],
        encoded_len_size=LEVEL[int(ARGS['--comprlevel'])][1]  
    )
   
    if ARGS['--compress']:
        fileN = get_fileName()
        with open(ARGS['FILE'], 'rb') as in_:
            with open(f"{fileN}.{FILE_EXTENTION}", 'ab') as out:
                compressLevel = int(ARGS['--comprlevel'])
                if compressLevel != 2:
                    encode(in_, out, None, ctx)
                else:
                    encode(in_, out)
                if(ARGS['--password']):                    
                    password = ARGS['--password']
                    fileToEncrypt = openFile(f"{fileN}.{FILE_EXTENTION}")
                    genwrite_key(fileN, password)
                    key = call_key(fileN)
                    encripter = Fernet(key)
                    encriptedFile = encripter.encrypt(fileToEncrypt)
                    #para apagar o conteudo antigo
                    out.truncate(0)
                    #guardar conteudo encriptado
                    out.write(encriptedFile)
    elif ARGS['--decompress']:
            with open(ARGS['FILE'], 'rb') as in_:
                next(in_)
                #faltam coisas aqui
    if ARGS['--sumary']:
        fileName = ARGS['FILE']
        size = len(fileName)
        if '.lzs' not in fileName:
            print("File is not compressed, please try again")
            sys.exit()
        else:
            head_reader(fileName, size) # nao esta a dar: erro(struct.error: unpack requires a buffer of 29 bytes)
            #mas calculando com o struct.calcsize da certo...
        

if __name__ == '__main__':
    main()