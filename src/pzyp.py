
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


from docopt import docopt
from lzss_io import PZYPContext
import compress_decompress as cd
import sys
from desktop_app1 import PzypMainWindow

LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}

ARGS = docopt(__doc__)
FILE_EXTENTION = 'lzs'


def main():
    ctx = PZYPContext(
        encoded_offset_size=LEVEL[int(ARGS['--comprlevel'])][0],
        encoded_len_size=LEVEL[int(ARGS['--comprlevel'])][1]  
    )
   
    if ARGS['--compress']:
        fileN = cd.get_fileName()
        with open(ARGS['FILE'], 'rb') as in_:
            with open(f"{fileN}.{FILE_EXTENTION}", 'ab') as out:
                compressLevel = int(ARGS['--comprlevel'])
                if compressLevel != 2:
                    cd.encode(in_, out, None, ctx)
                else:
                    cd.encode(in_, out)
                if(ARGS['--password']):                    
                    password = ARGS['--password']
                    fileToEncrypt = cd.openFile(f"{fileN}.{FILE_EXTENTION}")
                    cd.genwrite_key(fileN, password)
                    key = cd.call_key(fileN)
                    encripter = cd.Fernet(key)
                    encriptedFile = encripter.encrypt(fileToEncrypt)
                    #para apagar o conteudo antigo
                    out.truncate(0)
                    #guardar conteudo encriptado
                    out.write(encriptedFile)
                    if ARGS['--sumary']:
                        fileName = ARGS['FILE']
                        if '.lzs' not in fileName:
                            print("File is not compressed, please try again")
                            sys.exit()
                        else:
                            cd.head_reader(fileName)
    elif ARGS['--decompress']:
        if '.lzs' not in ARGS['FILE']:
                    print("File is not compressed, please try again")
                    sys.exit()
        else:
            with open(ARGS['FILE'], 'rb') as in_:
                    head = in_.readline().split()#com esta linha o decoder vai ler a 1ª linha que e o cabeçalho
                    fn=head[3].decode(cd.ENCODING)#aqui vamos buscar o nome do ficheiro ao cabeçalho
                    oNl=[int(head[0]), int(head[1])]#aqui vamos buscar o NCODED_OFFSET_SIZE e o ENCODED_LEN_SIZE do ficheiro comprimido
                    with open(fn, 'w+') as out:
                        cd.decode(in_, out, oNl)#quando chamamos o decode, o in_ ja leu a primeira linha e começa no codigo comprimido
    else:
        PzypMainWindow.run_app()



if __name__ == '__main__':
    main()