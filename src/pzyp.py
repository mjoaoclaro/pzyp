#import docopt
from hashlib import new
from re import search
import sys
from collections import deque


FILE_EXTENSION = 'lzs' 

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

def importFile(location):
    file = open(location, 'r+')
    content = file.read()
    file.close()
    return content

def exportFile(compressedText):
    newFile = open(f'teste.{FILE_EXTENSION}', 'w')
    newFile.write(compressedText)
    newFile.close()

class Window:
    def __init__(self):
        self._dictionary = deque(maxlen=100000000000)
        self._searchWord = []
    
    def extendDictionary(self ,data):
        self._dictionary.extend(data)

    def getOffset(self, word)->int:
        dictionaryString = "".join(self._dictionary)
        try:
            return dictionaryString.index(word)
        except ValueError:
            return -1
        
def build_token(distance, length):
        return f'<{str(distance)},{str(length)}>'


def encode(originalText):
    position = 0
    window = Window()
    result = ''
    searchWord = ''

    for originalChar in originalText:
        searchWord += originalChar
        index = window.getOffset(searchWord)
        if(index != -1) :
            #se ja estiver a ver o ultimo caracter
            if(position == len(originalText) - 1):
                index = position - index - len(searchWord) + 1
                length = len(searchWord)  
                pair = build_token(index, length)
                result += build_token(index, length)
                searchWord = ''
            else: 
                # tentar a letra seguinte
                searchWordAndTry = searchWord + originalText[position + 1]
                tryNextCharIndex = window.getOffset(searchWordAndTry) 

                if(tryNextCharIndex == -1):
                    #se com a letra de seguinte nao existe faz a troca
                    index = position - index - len(searchWord) + 1
                    length = len(searchWord)  
                    pair = build_token(index, length)
                    if(len(pair) > length):
                        result += searchWord
                    else:
                        result += build_token(index, length)
                    searchWord = ''
                #se puder continuar a tentar letras vai continuar
        else:
            result += originalChar
            searchWord = ''
        window.extendDictionary(originalChar)
        position += 1
    return result

def decode():
    pass

if __name__ == '__main__':

#   args = docopt('__doc__') / para usar nas fases a seguir
# o ficheiro teste.txt esta na pasta tests
    
    if len(sys.argv) == 2:
        textContent = importFile(sys.argv[1])
        result = encode(textContent)
        exportFile(result)
    else:
        decode()


