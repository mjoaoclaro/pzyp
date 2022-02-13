
import sys
from collections import deque
import os


FILE_EXTENTION = 'lzs' 

"""
This is a work of our python class, we're implementing a compressor/decompressor using the LZSS method

    Usage:
        pzyp.py [-c | -d |(<FILE>)

    Options: (some of the options will be implemented after)
        -h, --help         show this text
        -c, --compress     compress FILE
        -d, --decompress   decompress FILE
        -l                 compressing LEVEL [default: 2]
        -s, --sumary       meta-info of compressed FILE
        -p, --password     establishes a PASSWORD for FILE encription

    LEVEL: is an int that ranges between 1 and 4; the
    compression LEVEL affects the window dimension(size of buffer)
    and the maximum size sequence.(to be implemented after)

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


class PzypError(ValueError):
    pass


def importFile(location):
    file = open(location, 'r+')
    content = file.read()
    file.close()
    return content

def exportFile(compressedText, extension):
    head, tail = os.path.split(sys.argv[2])
    file=str(tail)
    fileName=file.split('.')
    newFile = open(f'{fileName[0]}.{extension}', 'w')
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
        except PzypError:
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

def decode(encodedText):
    isEncoded = False
    firstElement = True
    index = ''
    length = ''
    result = []
    stringResult = ''

    for char in encodedText:
        if char == '<':
            isEncoded = True
            firstElement = True
        elif char == ',':
            firstElement = False
        elif char == '>':
            isEncoded = False
   
            decodedText = result[-int(index):][:int(length)]
            result.extend(decodedText)

            index = ''
            length = ''
        elif isEncoded:
            if firstElement:
                index += char
            else:
                length += char
        else:
            result.append(char)

    for c in result:
        stringResult += c

    return stringResult

if __name__ == '__main__':
    
#   args = docopt('__doc__') / para usar nas fases a seguir

    if len(sys.argv) < 3:
        print(f"Usage: python3 {sys.argv[0]} -c (for compress) file.txt or - d (for decompress) file.lsz]")
        sys.exit(2)

    if sys.argv[1] == '-c':
            textContent = importFile(sys.argv[2])
            result = encode(textContent)
            exportFile(result, FILE_EXTENTION)
    
    if sys.argv[1] == '-d':
            textToDecompress = importFile(sys.argv[2])
            decompressedResult = decode(textToDecompress)
            exportFile(decompressedResult, 'txt')

 



   


