from hash_func import hash_func

class DoubleFastModel(object):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes,large_hash_bits, small_hash_bits, min_match_len):
        self.input_reader = input_reader
        self.seq_writter = seq_writter
        self.hash_cover_bytes = hash_cover_bytes
        self.large_hash_bits = large_hash_bits
        self.small_hash_bits = small_hash_bits
        self.window_size = 1 << window_log
        self.min_match_len = min_match_len

        self.large_hash_table = {}
        self.small_hash_table = {}
        self.input_data = self.input_reader.read()
        self.input_length = len(self.input_data)
        self.ilimit = self.input_length - self.hash_cover_bytes

    def count_match_length(self, ip, history_addr):
        match_length = 0
        while ip + match_length < self.input_length and self.input_data[ip + match_length] == self.input_data[history_addr + match_length] :
            match_length += 1
        return match_length

    def check_large_hash_table(self, ip, hash_l):
        if hash_l in self.large_hash_table:
            history_addr = self.large_hash_table[hash_l]
            if ip - history_addr < self.window_size:
                ml = self.count_match_length(ip, history_addr)
                if ml >= 8:
                    return ip - history_addr, ml
        return 0, 0

    def check_small_hash_table(self, ip, hash_s):
        if hash_s in self.small_hash_table:
            history_addr = self.small_hash_table[hash_s]
            if ip - history_addr < self.window_size:
                ml = self.count_match_length(ip, history_addr)
                if ml >= self.min_match_len:
                    return ip - history_addr, ml
        return 0, 0
    
    def process(self):
        ip = 0
        prev_ip = 0
        while ip < self.ilimit:
            hash_l = hash_func(self.input_data[ip:ip+self.hash_cover_bytes], self.large_hash_bits)
            hash_s = hash_func(self.input_data[ip:ip+self.min_match_len], self.small_hash_bits)
            offset, ml = self.check_large_hash_table(ip, hash_l)
            if offset == 0:
                offset, ml = self.check_small_hash_table(ip, hash_s)
            
            if offset > 0:
                self.seq_writter.write_seq(offset, ip - prev_ip, ml)
                for i in range(ml):
                    hash_l = hash_func(self.input_data[ip+i:ip+i+self.hash_cover_bytes], self.large_hash_bits)
                    hash_s = hash_func(self.input_data[ip+i:ip+i+self.min_match_len], self.small_hash_bits)
                    self.large_hash_table[hash_l] = ip + i
                    self.small_hash_table[hash_s] = ip + i
                prev_ip = ip + ml
                ip += ml
            else:
                self.large_hash_table[hash_l] = ip
                self.small_hash_table[hash_s] = ip
                ip += 1

                    



