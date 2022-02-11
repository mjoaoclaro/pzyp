#import docopt
from re import search
import sys
from collections import deque

"""
Implementing a compressor/decompressor using the LZSS method

usage:
    pzyp.py [-c [-l (<LEVEL>)] | -d | -s | -h] [-p (<PASSWORD>)] (<FILE>)

options:
    -h, --help      show this text
    -c              compress FILE
    -d              decompress FILE
    -l              compressing LEVEL [default: 2]
    -s, --sumary    meta-info of compressed FILE
    -p, --password  establishes a PASSWORD for FILE encription

LEVEL: is an int that ranges between 1 and 4; the
compression LEVEL affects the window dimension(size of buffer)
and the maximum size sequence.
Level 1: W =  1 KB ⇒10 bits    M = 15 + 2 ⇒4 bits
Level 2: W =  4 KB⇒12 bits    M = 15 + 3⇒4 bits
Level 3: W = 16 KB ⇒ 14 bits   M = 32 + 3 ⇒ 5 bits
Level 4: W = 32 KB ⇒ 15 bits   M = 32 + 3 ⇒ 5 bits

The output file will have the same name as the FILE with the extension .LZS
"""

class PyzypError(Exception):
    pass

class Window:
    def __init__(self, size: int):
        self._deque = deque(maxlen=size)
        
    
    def extend(self, data):
        self._deque.extend(data)

    def search(self, data_compare)->bool:
        flag = False

        for data in self._deque:
            if data == data_compare:
                flag = True
                break
        return flag

    def get_data(self): #para testes
        for c in self._deque:
            print(c)


def encode(in_):
    buffer = Window(20) # falta definir como ele explicou na aula (ter o tamanho em bytes)
    found = [] # lista para colocar os caracteres que foram encontrados e depois comparar sequencias no buffer
    index_at = 0 # indice de onde se encontra o caracter para depois colocar no "<index_at,pos_>"
    pos_ = 0 # para colocar na posição do comentário em cima; quantos caracteres do found sao iguais em sequencia no buffer

    with open(in_, 'r+') as file_in:
        for c in file_in.read():
            buffer.extend(c)
            try:
                if buffer.search(c):
                    index_at = buffer._deque.index(c)
                    found.append(c)
                    print('Depois do search ', c)

            except PyzypError:
                print('erro')




def decode():
    pass


if __name__ == '__main__':

#   args = docopt('__doc__') / para usar nas fases a seguir

    
    if len(sys.argv) == 2:
        encode(sys.argv[1])
    else:
        decode()


