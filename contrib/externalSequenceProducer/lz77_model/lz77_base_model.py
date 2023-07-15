class LZ77BaseModel(object):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, max_match_len):
        self.input_reader = input_reader
        self.seq_writter = seq_writter
        self.hash_cover_bytes = hash_cover_bytes
        self.window_size = 1 << window_log
        self.min_match_len = min_match_len
        self.max_match_len = max_match_len

        self.input_data = self.input_reader.read()
        self.input_length = len(self.input_data)
        self.ilimit = self.input_length - self.hash_cover_bytes
    
    def count_match_length(self, ip, history_addr):
        match_length = 0
        while ip + match_length < self.input_length and match_length < self.max_match_len and self.input_data[ip + match_length] == self.input_data[history_addr + match_length] :
            match_length += 1
        return match_length