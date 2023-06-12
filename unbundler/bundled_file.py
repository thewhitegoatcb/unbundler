class ExternalStreamEOF(Exception):
    pass

class FileVariant:
    def __init__(self, stream_offset, variant_flag, file_size, data_offset) -> None:
        self.stream_offset = stream_offset
        self.variant_flag = variant_flag
        self.file_size = file_size
        self.data_offset = data_offset

class BundeledFile:
    def __init__(self, bundle, ext_hash, filename_hash, variants, file_entry, stream_size, data) -> None:
        self.ext_hash = ext_hash
        self.filename_hash = filename_hash
        self.variants = variants
        self.file_entry = file_entry
        self.external_stream_size = stream_size
        self.data = memoryview(data)
        self.bundle:bundle.Bundle = bundle

    def get_variant_data(self, variant):
        if variant not in self.variants:
            return None
        
        if len(self.data) < variant.data_offset + variant.file_size:
            return None
        
        out_data = self.data[variant.data_offset: variant.data_offset + variant.file_size]
        #TODO: deal with stream and multiple variatns
        if self.external_stream_size > 0:
            external_data = self.bundle.read_external_stream(variant.stream_offset, self.external_stream_size - variant.stream_offset)
            if len(external_data) < self.external_stream_size:
                raise ExternalStreamEOF("ExternalStreamEOF")
            out_data =  b'' + out_data + external_data
        return out_data
        
