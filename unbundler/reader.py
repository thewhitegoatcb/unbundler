class BundleReader:
    SIZE_UNCOMPRESSED = 0x10000
    
    def __init__(self, stream, total_size) -> None:
        self.stream = stream
        self.total_size = total_size
        self.chunk = bytes()
        self.pos = 0
    
    def _unpack(self, fmt):
        import struct

        size = struct.calcsize(fmt)
        buf = self.stream.read(size)
        return struct.unpack(fmt, buf)

    def _read_next_chunk(self):
        import zlib
        [chunk_size] = self._unpack('<L')
            
        compressed_chunk = self.stream.read(chunk_size)
        # handle total_size EOF
        if chunk_size != BundleReader.SIZE_UNCOMPRESSED:
            return zlib.decompress(compressed_chunk)
        else:
            return compressed_chunk
    
    def readinto(self, b):
        size = len(b)
        bytes_read = 0
        if size != 0:
            while size > 0:
                if self.pos == len(self.chunk):
                    self.chunk = self._read_next_chunk()
                    if not self.chunk:
                        # The stream is exhausted
                        break
                    self.pos = 0
                chunk_size = min(len(self.chunk) - self.pos, size)
                if chunk_size == len(self.chunk):
                    b[bytes_read:bytes_read+chunk_size] = self.chunk
                else:
                    b[bytes_read:bytes_read+chunk_size] = memoryview(self.chunk)[self.pos:self.pos+chunk_size]
                bytes_read += chunk_size
                self.pos += chunk_size
                size -= chunk_size
        return bytes_read
        
    def read(self, size):
        if size == -1:
            out_buffer = bytearray()
            while True:
                if self.pos == len(self.chunk):
                    self.chunk = self._read_next_chunk()
                    if not self.chunk:
                        # The stream is exhausted
                        break
                    self.pos = 0
                if self.pos == 0:
                    out_buffer.extend(self.chunk)
                else:
                    out_buffer.extend(memoryview(self.chunk)[self.pos:])
                self.pos = len(self.chunk)
            return out_buffer
        else:
            out_buffer = bytearray(size)
            read_size = self.readinto(out_buffer)
            if read_size < size:
                #maybe raise EOF
                return out_buffer[:read_size]
            return out_buffer
        