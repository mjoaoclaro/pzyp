
"""
This is a work of our python class, we're implementing a compressor/decompressor using the LZSS method

    Usage:
        pzyp.py [-c [-l LEVEL] | -d] [-sh] [-p PASSWORD] FILE
        pzyp.py

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


from collections import deque
import os
import sys
from typing import BinaryIO
from docopt import docopt
import time
import struct
from typing import BinaryIO
from cryptography.fernet import Fernet
import base64, hashlib
import lzss_io as lz
import desktop_app1 as mw

LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}

ARGS = docopt(__doc__)

FILE_EXTENTION = 'lzs'
ENCODING = 'utf-8'


class Window:
    def __init__(self, ctx=lz.PZYPContext()):
        self._dictionary = deque(maxlen=2 ** ctx.encoded_offset_size)
        self._values = [ctx.encoded_offset_size, ctx.encoded_len_size]


    def extend(self, data: bytes):
        self._dictionary.append(data)
        if len(self._dictionary) >= self._dictionary.maxlen:
            self._dictionary.popleft()

    def get_dict(self):
        return list(self._dictionary)
    
    def find(self, check_elements):
        i = 0
        offset = 0
        for element in self._dictionary:
            if len(check_elements) <= offset:
                return i - len(check_elements)

            if check_elements[offset] == element:
                offset += 1
            else:
                offset = 0

            i += 1
        return -1

    def ctxValues(self):
        return self._values
        
    def head_writer(self, win_dimention, max_seq, in_, out):
        dt = time.time()                                      
        fl = str(dt)
        newl = '\n'

        with open(out, 'wb+') as f:
            f.write(bytes(str(win_dimention)+' ', ENCODING))
            f.write(bytes(str(max_seq)+' ', ENCODING))
            f.write(struct.pack('{}s'.format(len(fl)),bytes(fl, ENCODING)))
            if len(bytes(f' {in_} {newl}', ENCODING)) < 255:
                f.write(bytes(f' {in_} {newl}', ENCODING))
            else:
               newName=in_.split('/')
               f.write(bytes(' '+ newName[-1] +' '+newl, ENCODING))
               
        
        

def head_reader(file_name): 
        with open(file_name, 'rb') as f:
            header=f.readline().split() 
            off=header[0].decode(ENCODING)
            size_sec=header[2] 
            a = struct.unpack('{}s'.format(len(size_sec)), header[2]) 
            fn=header[3].decode(ENCODING) 
            dt_sec = a[0].decode(ENCODING) 
            dt = time.ctime(float(dt_sec))
            print(f'File name: {fn}')
            print(f'Compression date/time:  {dt}')
            print(f'Compression parameters : Buffer -> {2**int(off)} ({off} bits),') 
            if off == 10:
                print('Max Seq. Len. -> 17 (4 bits)')
            elif off == 12:
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

def filePathFromUI(in_, out):
    outf='{}.{}'.format(out.split('_')[0], FILE_EXTENTION)
    return[in_, outf]

def encode(in_: BinaryIO, out: BinaryIO, lzss_writer=None, ctx=lz.PZYPContext()):
    window = Window(ctx)
    off, leng = window.ctxValues()
    if len(sys.argv)>= 2:
        out_f = out.name
        in_f = in_.name
        window.head_writer(off, leng, in_f, out_f)
    else:
        window.head_writer(off, leng, in_, out)
        out_f = out

    out_=open(f'{out_f}', 'ab')
    with (lzss_writer or lz.LZSSWriter(out_, ctx)) as lzss_out:
        check_characters = []
        if len(sys.argv)>=2:
            text = in_.read()
        else:
            text = openFile(in_)

        i = 0
        for char in text:
            check_characters.append(char)
            index = window.find(check_characters)

            if index == -1 or i == len(text) - 1:
                if len(check_characters) > 1:
                    index = window.find(check_characters[:-1])
                    if index <= lz.MAX_STRING_SIZE:
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
    out_.close()

def decode(in_: BinaryIO, out: BinaryIO, off_len, lzss_reader=None, ctx=lz.PZYPContext()):
    buff_size = off_len[0]  
    len_size = off_len[1]
    ctx=lz.PZYPContext(encoded_offset_size= buff_size, encoded_len_size= len_size)
    window = Window(ctx)
    with (lzss_reader or lz.LZSSReader(in_, ctx)) as lzss_in:
        
        output = window.get_dict() 
        result=b''
        for encoded_flag, element in lzss_in:
                if encoded_flag:    
                    prefix_pos, prefix_len = element 
                    b_decompress = output[-prefix_pos:][:prefix_len]
                    result += b''.join(b_decompress).strip(b'\r')
                    for b in b_decompress:
                        window.extend(b) 
                        output = window.get_dict() 
                else:
                    result += element.strip(b'\r')
                    window.extend(element)
                    output = window.get_dict()
        
        print(result)
        out.write(result.decode(ENCODING))


def get_fileName(filName):
    head, tail = os.path.split(filName)
    fileName=tail
    result=fileName.split('.')
    return result[0]


def main():
    ctx = lz.PZYPContext(
        encoded_offset_size=LEVEL[int(ARGS['--comprlevel'])][0],
        encoded_len_size=LEVEL[int(ARGS['--comprlevel'])][1]  
    )
   
    if ARGS['--compress']:
        fileN = get_fileName(ARGS['FILE'])
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
        print(f"File is compressed [{fileN}.{FILE_EXTENTION}]")
    elif ARGS['--decompress']:
        if '.lzs' not in ARGS['FILE']:
                    print("File is not compressed, please try again")
                    sys.exit()
        else:
            with open(ARGS['FILE'], 'rb') as in_:
                    head = in_.readline().split()
                    fn=head[3].decode(ENCODING)
                    oNl=[int(head[0]), int(head[1])]
                    with open(fn, 'w+') as out:
                        decode(in_, out, oNl)
    else:
        mw.PzypMainWindow.run_app()

    if ARGS['--sumary']:
        fileName = ARGS['FILE']
        if '.lzs' not in fileName:
            print("File is not compressed, please try again")
            sys.exit()
        else:
            head_reader(fileName)
        

if __name__ == '__main__':
    main()