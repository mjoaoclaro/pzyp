
from collections import deque
import os
from docopt import docopt
import time
import struct


"""
This is a work of our python class, we're implementing a compressor/decompressor using the LZSS method

    Usage:
        pzyp.py (-c [-l LEVEL] | -d) [-sh] [-p PASSWORD] FILE

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


def importFile(location):
    with open(location, 'rb+') as file:
        content = file.read()
    return content

def exportFile(compressedText, extension):
    head, tail = os.path.split(ARGS['FILE'])
    file=str(tail)
    fileName=file.split('.')
    with open(f'{fileName[0]}.{extension}', 'ab') as newFile:
        newFile.write(compressedText)


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
    def build_token(self, distance, length):
        return f'<{str(distance)},{str(length)}>'

    def decode(self, encodedText):
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

    def encode(self, originalText):
        position = 0
        result = ''
        searchWord = ''

        for originalChar in originalText:
            searchWord += originalChar
            index = self.getOffset(searchWord)
            if(index != -1) :
                #se ja estiver a ver o ultimo caracter
                if(position == len(originalText) - 1):
                    index = position - index - len(searchWord) + 1
                    length = len(searchWord)  
                    pair = self.build_token(index, length)
                    result += self.build_token(index, length)
                    searchWord = ''
                else: 
                    # tentar a letra seguinte
                    searchWordAndTry = searchWord + originalText[position + 1]
                    tryNextCharIndex = self.getOffset(searchWordAndTry) 

                    if(tryNextCharIndex == -1):
                        #se com a letra de seguinte nao existe faz a troca
                        index = position - index - len(searchWord) + 1
                        length = len(searchWord)  
                        pair = self.build_token(index, length)
                        if(len(pair) > length):
                            result += searchWord
                        else:
                            result += self.build_token(index, length)
                        searchWord = ''
                    #se puder continuar a tentar letras vai continuar
            else:
                result += originalChar
                searchWord = ''
            self.extendDictionary(originalChar)
            position += 1
        return result

def head_writer(level_nb, file_name):
    win_dimention = level_nb[0]
    max_seq = level_nb[1]
    dt = time.time()
    with open(f'{file_name}.copia', 'wb+') as f:
        f.write(struct.pack('>iid', win_dimention, max_seq, dt))
        f.write(struct.pack('{}s'.format(len(file_name)), bytes(file_name, 'utf-8')))
        print(struct.calcsize('> i i d'))
        print(struct.calcsize('{}s'.format(len(file_name))))

def head_reader(file_name):
    with open(file_name, 'rb') as f:
        s_list=list(struct.unpack('> i i d 9s', f.read()))
    dt_sec = s_list[2]
    dt = time.ctime(dt_sec)
    print(f'File name: {str(s_list[3])}')
    print(f'Compression date/time:  {dt}')
    print(f'Compression parameters : Buffer -> {2**s_list[0]} ({s_list[0]} bits),')
    if ARGS['--comprlevel'] == 1:
        print('Max Seq. Len. -> 17 (4 bits)')
    elif ARGS['--comprlevel'] == 2:
        print('Max Seq. Len. -> 18 (4 bits)')
    else:
        print('Max Seq. Len. -> 35 (5 bits)')

def main():
    if ARGS['--compress']:
            head_writer(LEVEL[int(ARGS['--comprlevel'])], ARGS['FILE'])
            textContent = importFile(ARGS['FILE'])
            encodeWindow = Window()
            result = encodeWindow.encode(textContent)
            if ARGS['--comprlevel']:
                print("teste")
            exportFile(result, FILE_EXTENTION)         
    elif ARGS['--decompress']:
            textToDecompress = importFile(ARGS['FILE'])
            decodeWindow = Window()
            decompressedResult = decodeWindow.decode(textToDecompress)
            exportFile(decompressedResult, 'txt')
    if ARGS['--password']:
        print("colocar aqui o codigo em vez deste print")
    if ARGS['--sumary']:
        head_reader(ARGS['FILE'])

if __name__ == '__main__':
    main()
    

 



   


