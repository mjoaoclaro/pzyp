from collections import deque
import sys


# FILE_EXIT = 'lzs'

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
        
def generatePair(distance, length):
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
                pair = generatePair(index, length)
                result += generatePair(index, length)
                searchWord = ''
            else: 
                #vou tentar a letra seguinte
                searchWordAndTry = searchWord + originalText[position + 1]
                tryNextCharIndex = window.getOffset(searchWordAndTry) 

                if(tryNextCharIndex == -1):
                    #se com a letra de seguinte nao existe faz a troca
                    index = position - index - len(searchWord) + 1
                    length = len(searchWord)  
                    pair = generatePair(index, length)
                    if(len(pair) > length):
                        result += searchWord
                    else:
                        result += generatePair(index, length)
                    searchWord = ''
                #se puder continuar a tentar letras vai continuar
        else:
            result += originalChar
            searchWord = ''
        window.extendDictionary(originalChar)
        position += 1
    print(result)


def decode():
    pass



# def main():
#     print('estou aqui')
#     window = Window()
#     print(window.dictionary)
#     window.extend('abc')
#     print(window.dictionary)
#     pass

# # if __name__ == '__main__':


encode("Blah blah blah blah blah!")
#     # main()

