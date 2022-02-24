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


from bz2 import decompress
from collections import deque
import os
import sys
from typing import BinaryIO
from unittest import result
from docopt import docopt
import time
import struct
from typing import BinaryIO
from cryptography.fernet import Fernet
import base64, hashlib
from lzss_io import LZSSWriter, PZYPContext, LZSSReader




LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}

ARGS = docopt(__doc__)

FILE_EXTENTION = 'lzs'
ENCODING = 'utf-8'

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

    def extend(self, data: bytes):
        self._dictionary.append(data)
        if len(self._dictionary) >= self._dictionary.maxlen:
            self._dictionary.popleft()

    def get_dict(self): #esta função retorna o deque convertido em lista. tive de fazer assim porque o deque atrofiava com o slice no decode
        return list(self._dictionary)
    
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

    def head_writer(self, win_dimention, max_seq, file_name): #aqui tive de por espaços entre os elementos para o decode
        dt = time.time()                                      #poder dividir e por numa lista
        fl = str(dt)
        newl = '\n'
        fileN = get_fileName()
        with open(f'{fileN}.{FILE_EXTENTION}', 'wb+') as f:
            f.write(bytes(str(win_dimention)+' ', ENCODING))
            f.write(bytes(str(max_seq)+' ', ENCODING))
            f.write(struct.pack('{}s'.format(len(fl)),bytes(fl, ENCODING)))
            f.write(bytes(' '+file_name +' '+newl, ENCODING))
        

def head_reader(file_name): #para ler o cabeçalho tive de mudar as funçoes writer e reader
        with open(file_name, 'rb') as f:
            header=f.readline().split() #coloca o cabeçalho numa lista
            off=header[0].decode(ENCODING)#descodifica os bytes em str
            size_sec=header[2] #para saber o tamanho da data em segundos
            a = struct.unpack('{}s'.format(len(size_sec)), header[2]) #fazemos o unpack dos segundos; da um tuplo
            fn=header[3].decode(ENCODING) #o nome do ficheiro em str
            dt_sec = a[0].decode(ENCODING) #acedemos ao tuplo dos segundos e convertemos numa str
            dt = time.ctime(float(dt_sec)) #transformamos os segundos numa data; (float(dt_sec)) quer dizer str para float
            print(f'File name: {fn}')
            print(f'Compression date/time:  {dt}')
            print(f'Compression parameters : Buffer -> {2**int(off)} ({off} bits),') #de str para int para fazer a conta 
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


def encode(in_: BinaryIO, out: BinaryIO, lzss_writer=None, ctx=PZYPContext()):
    with (lzss_writer or LZSSWriter(out, ctx)) as lzss_out:
        window = Window(ctx)
        window.head_writer(ENCODED_OFFSET_SIZE, ENCODED_LEN_SIZE, ARGS['FILE'])
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


def decode(in_: BinaryIO, out: BinaryIO, off_len, lzss_reader=None, ctx=PZYPContext()):
    with (lzss_reader or LZSSReader(in_, ctx)) as lzss_in:
        buff_size = off_len[0]   #dividimos em posiçao
        len_size = off_len[1]    # e tamanho
        window = Window(ctx=PZYPContext(buff_size, len_size))#instanciamos a janela com os parametros certos do ficheiro
        output = window.get_dict() #criei este novo metodo(explicaçao em cima)
        result=b''
        for encoded_flag, element in lzss_in:
                if encoded_flag:    #se ele encontra o bit a dizer que esta encoded
                    prefix_pos, prefix_len = element #vai buscar a posiçao e comprimento ao element
                    b_decompress = output[-prefix_pos:][:prefix_len] #vamos buscar o que esta codificado na pos e comp
                    result += b''.join(b_decompress) #pomos ainda em bytes no resultado
                    for b in b_decompress:
                        window.extend(b) #vamos colocar o byte no buffer
                        output = window.get_dict() 
                else:
                    result += element #se nao é logo o elemento que nao esta encoded que juntamos ao resultado
                    window.extend(element) #vamos colocar o elemento no buffer
                    output = window.get_dict()


        out.write(result.strip(b'\r').decode(ENCODING)) #escrevemos o resultado no ficheiro de saida


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
        if '.lzs' not in ARGS['FILE']:
                    print("File is not compressed, please try again")
                    sys.exit()
        else:
            with open(ARGS['FILE'], 'rb') as in_:
                    head = in_.readline().split()#com esta linha o decoder vai ler a 1ª linha que e o cabeçalho
                    fn=head[3].decode(ENCODING)#aqui vamos buscar o nome do ficheiro ao cabeçalho
                    oNl=[int(head[0]), int(head[1])]#aqui vamos buscar o NCODED_OFFSET_SIZE e o ENCODED_LEN_SIZE do ficheiro comprimido
                    with open(fn, 'w+') as out:
                        decode(in_, out, oNl)#quando chamamos o decode, o in_ ja leu a primeira linha e começa no codigo comprimido

    if ARGS['--sumary']:
        fileName = ARGS['FILE']
        if '.lzs' not in fileName:
            print("File is not compressed, please try again")
            sys.exit()
        else:
            head_reader(fileName)
        

if __name__ == '__main__':
    main()