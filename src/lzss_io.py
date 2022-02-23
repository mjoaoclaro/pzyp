import io
import math
from typing import Union, BinaryIO, Tuple
# podem também querer: from typing import Iterable

import bitstruct
from bitarray import bitarray


UNENCODED_STRING_SIZE = 8   # in bits
ENCODED_OFFSET_SIZE = 12    # in bits
ENCODED_LEN_SIZE = 4        # in bits
ENCODED_STRING_SIZE = ENCODED_OFFSET_SIZE + ENCODED_LEN_SIZE  # in bits

WINDOW_SIZE = 2 ** ENCODED_OFFSET_SIZE        # in bytes
BREAK_EVEN_POINT = ENCODED_STRING_SIZE // 8   # in bytes
MIN_STRING_SIZE = BREAK_EVEN_POINT + 1        # in bytes
MAX_STRING_SIZE = 2 ** ENCODED_LEN_SIZE - 1  + MIN_STRING_SIZE  # in bytes


class PZYPContext:
    """
    A context objects stores related parameters that control LZSS 
    algorithm. It's essentially a data class that in future versions
    will probably be defined with the new @dataclass decorator available
    since Python 3.7.
    """
    def __init__(
            self,
            encoded_offset_size=ENCODED_OFFSET_SIZE,
            encoded_len_size=ENCODED_LEN_SIZE,
            unenc_string_size=UNENCODED_STRING_SIZE,
    ):
        """
        These sizes are specified in bits.
        """
        self._encoded_offset_size = encoded_offset_size
        self._encoded_len_size = encoded_len_size
        self._unencoded_string_size = unenc_string_size
    #:
    @property
    def encoded_offset_size(self):
        return self._encoded_offset_size
    #:
    @property
    def encoded_len_size(self):
        return self._encoded_len_size
    #:
    @property
    def unencoded_string_size(self):
        return self._unencoded_string_size
    #:
    @property
    def encoded_string_size(self) -> int:
        return self.encoded_offset_size + self.encoded_len_size  # in bits
    #:
    @property
    def window_size(self) -> int:
        return 2 ** self.encoded_offset_size        # in bytes
    #:
    @property
    def break_even_point(self) -> int:
        return self.encoded_string_size // 8        # in bytes
    #:
    @property
    def min_string_size(self) -> int: 
        return self.break_even_point + 1            # in bytes
    #:
    @property
    def max_string_size(self) -> int:
        return 2 ** self.encoded_len_size - 1  + self.min_string_size  # in bytes
    #:
#:

class LZSSWriter:
    """
    An LZSSWriter object writes encoded or unencoded strings to an
    output stream, as stated in the classic LZSS specification.
    A string is just a pair <offset/postion, length>, while an 
    unencoded string is a bytes object with (most probably) one
    byte.
    """
    def __init__(
            self, 
            out: BinaryIO, 
            ctx=PZYPContext(),
            close_out_stream=False,
    ):
        self.buffer = bitarray()
        self._close_out_stream = close_out_stream
        self._out = out
        self._ctx = ctx
        self._enc_fmt = bitstruct.compile(
            f'u{ctx.encoded_offset_size}u{ctx.encoded_len_size}'
        )
        self._inner_bitify_enc = self._bitify_enc_not_multiple_of_8
        if (ctx.encoded_offset_size + ctx.encoded_len_size) % 8 == 0:
            self._inner_bitify_enc = self._bitify_enc_multiple_of_8
    #:
    def write(self, data: Union[bytes, Tuple[int, int]]):
        (self._bitify_unenc if isinstance(data, bytes) else self._bitify_enc)(data)
        if len(self.buffer) == 32_768:
            self._stream_bits()
    #:
    def _bitify_enc(self, enc_data: Tuple[int, int]) -> int:
        pos, len_ = enc_data
        ctx = self._ctx
        assert pos < ctx.window_size, f'pos={pos}'
        assert ctx.min_string_size <= len_ <= ctx.max_string_size, f'pos = {pos}, len = {len_}'
        mapped_len = len_ - ctx.min_string_size
        self.buffer.append(True)
        self._inner_bitify_enc(pos, mapped_len)
        return ctx.encoded_string_size  # remember: it's in bits ...
    #:
    def _bitify_enc_not_multiple_of_8(self, pos: int, mapped_len: int):
        enc_fmt = self._enc_fmt
        bitarr = bitarray()
        bitarr.frombytes(enc_fmt.pack(pos, mapped_len))
        self.buffer.extend(bitarr[:enc_fmt.calcsize()])
    #:
    def _bitify_enc_multiple_of_8(self, pos: int, mapped_len: int):
        self.buffer.frombytes(self._enc_fmt.pack(pos, mapped_len))
    #:
    def _bitify_unenc(self, unenc_data: bytes) -> int:
        assert unenc_data
        self.buffer.append(False)
        self.buffer.frombytes(unenc_data)
        return self._ctx.unencoded_string_size
    #:
    def _stream_bits(self, size_in_bits: int=2**63-1):
        data = self.buffer[:size_in_bits].tobytes()
        del self.buffer[:size_in_bits]
        self._out.write(data)
    #:
    def close(self, flush_buffer=True):
        if flush_buffer:
            self._flush_buffer()
        if self._close_out_stream:
            self._out.close()
    #:
    def __enter__(self):
        return self
    #:
    def __exit__(self, exc_type, exc_value, traceback):
        # Flush the buffer only if an exception hasn't occurred
        self.close(not exc_value)
    #:
    def _flush_buffer(self):
        if self.buffer:
            self.buffer.fill()     # pad buffer with 0s to get
            self._stream_bits()    # an integral number of bytes
    #:
#:

class LZSSReader:
    """
    A LZSS decoder can use this class to create an object that parses
    reads the 'in_' stream in termos of encoded or unencoded string,
    accordingly to the classic LZSS specification.
    """
    def __init__(
            self, 
            in_: BinaryIO, 
            ctx=PZYPContext(),
            close_in_stream=False,
    ):
        self.buffer = bitarray()
        self.close_in_stream = close_in_stream
        self._in = in_
        self._ctx = ctx
        self._enc_fmt = bitstruct.compile(
            f'u{ctx.encoded_offset_size}u{ctx.encoded_len_size}'
        )
    #:
    def read(self):
        ctx = self._ctx
        assert len(self.buffer) <= ctx.encoded_string_size + 8

        if self._end_of_data():
            return False, b''

        if not self.buffer:
            self.buffer.frombytes(self._in.read(1))
        encoded = bool(self.buffer[0])

        needed_bits = 1 + [ctx.unencoded_string_size, ctx.encoded_string_size][encoded]
        bytes_to_read = math.ceil((needed_bits - len(self.buffer)) / 8)
        self.buffer.frombytes(self._in.read(bytes_to_read))

        data: bitarray = self.buffer[1:needed_bits]
        del self.buffer[:needed_bits]

        if encoded:
            pos, len_ = self._enc_fmt.unpack(data.tobytes())
            return True, (pos, len_ + ctx.min_string_size)
        return False, data.tobytes()
    #:
    def _end_of_data(self) -> bool:
        # Remember: The input stream may be at eof, but the buffer may 
        # still have 0's. Why? Padding to fill the last byte when 
        # encoding.
        buffer_maybe_empty = (
            not self.buffer or 
            (self.buffer.count(0) == len(self.buffer) and len(self.buffer) < 8)
        )
        curr_pos = self._in.tell()
        eof = buffer_maybe_empty and not self._in.read(1)
        self._in.seek(curr_pos)
        return eof
    #:
    def __iter__(self):
        return self
    #:
    def __next__(self):
        data = self.read()
        if not data[1]:
            raise StopIteration()
        return data
    #:
    def close(self):
        assert len(self.buffer) < 16
        empty_buffer = not self.buffer or self.buffer.count(0) == len(self.buffer)
        if not empty_buffer:
            raise LZSSReader.UnreadData(
                'Unread compressed data in buffer.'
            )
        if self.close_in_stream:
            self._in.close()        
    #:
    def __enter__(self):
        return self
    #:
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    #:
    class UnreadData(Exception): 
        pass
    #:
#:

##########################################################################
##
##      ESBOÇOS DOS ALGORITMOS DE COMPRESSÃO E DESCOMPRESSÃO
##
##########################################################################

# def encode(in_: BinaryIO, out: BinaryIO, lzss_writer=None, ctx=PZYPContext()):
#     with (lzss_writer or LZSSWriter(out, ctx)) as lzss_out:
#         window = Window(ctx)
#         # ... RESTO DO ALGORITMO DE COMPRESSÃO ...
# #:

# def decode(in_: BinaryIO, out: BinaryIO, lzss_reader=None, ctx=PZYPContext()):
#     with (lzss_reader or LZSSReader(in_, ctx)) as lzss_in:
#         window = Window(ctx)
#         # ... RESTO DO ALGORITMO DE DESCOMPRESSÃO ...
# #:

##########################################################################
##
##      TESTING CODE
##
##########################################################################

def _test():
    ctx = PZYPContext(
        encoded_offset_size=4,   # janela terá 16 bytes
        encoded_len_size=3       # comprimentos de 8 + 1 - 1 = 8 bytes
    )
    print(f'WINDOW_SIZE     = {ctx.window_size}')
    print(f'MIN_STRING_SIZE = {ctx.min_string_size}')
    print(f'MAX_STRING_SIZE = {ctx.max_string_size}')

    print('\n----\n')

    win = b'ABCDEFGHI'
    with io.BytesIO() as out:
        with LZSSWriter(out, ctx=ctx) as writer:
            print("Vamos gravar os dados em formato LZS")
            for byte_int in win:
                writer.write(bytes((byte_int,)))
            
            print("Vamos gravar uma referência fictícia")
            prefix_pos = 4
            prefix_len = 3
            writer.write((prefix_pos, prefix_len))

        print('\n----\n')

        print('O ficheiro de saída tem os seguintes dados: ')
        out.seek(0)
        dados_comp = out.read()
        print(dados_comp)

    print('\n----\n')

    print('Vamos descodificar os dados anteriores')
    with io.BytesIO(dados_comp) as in_:
        with LZSSReader(in_, ctx=ctx) as reader:
            for encoded_flag, elemento in reader:
                if encoded_flag:
                    prefix_pos, prefix_len = elemento
                    print(f'<{prefix_pos},{prefix_len}>', end='')
                else:
                    print(elemento.decode(), end='')
            print()


if __name__ == '__main__':
    _test()
