class InputReader(object):
    def __init__(self, input_path):
        self.input_path = input_path
    
    def read(self):
        # return whole file once
        with open(self.input_path, 'rb') as f:
            return f.read()
        
class SeqWritter(object):
    def __init__(self, output_path):
        self.output_path = output_path
        self.fd = open(self.output_path, 'wb')
    
    def write_seq(self, offset, lit_len, match_len):
        # write seq to file
        concat_seq =(match_len << 48) + (lit_len << 32) + offset
        self.fd.write(concat_seq.to_bytes(8, byteorder='little'))
        
    def close(self):
        self.fd.close()