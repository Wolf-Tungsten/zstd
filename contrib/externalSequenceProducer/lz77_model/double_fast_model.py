from hash_func import hash_func
from lz77_base_model import LZ77BaseModel
import tqdm
class DoubleFastModel(LZ77BaseModel):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, large_hash_bits, small_hash_bits):
        LZ77BaseModel.__init__(self, input_reader=input_reader, seq_writter=seq_writter, window_log=window_log, hash_cover_bytes=hash_cover_bytes, min_match_len=min_match_len, max_match_len=1<<16)
        self.large_hash_bits = large_hash_bits
        self.small_hash_bits = small_hash_bits
        self.large_hash_table = {}
        self.small_hash_table = {}

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
        with tqdm.tqdm(total=self.ilimit) as pbar:
            while ip < self.ilimit:
                hash_l = hash_func(self.input_data[ip:ip+self.hash_cover_bytes], self.large_hash_bits)
                hash_s = hash_func(self.input_data[ip:ip+self.min_match_len], self.small_hash_bits)
                assert(hash_l < 1<<self.large_hash_bits)
                assert(hash_s < 1<<self.small_hash_bits)
                offset, ml = self.check_large_hash_table(ip, hash_l)
                if offset == 0:
                    offset, ml = self.check_small_hash_table(ip, hash_s)
                
                if offset > 0:
                    self.seq_writter.write_seq(offset, ip - prev_ip, ml)
                    for i in range(1):
                        hash_l = hash_func(self.input_data[ip+i:ip+i+self.hash_cover_bytes], self.large_hash_bits)
                        hash_s = hash_func(self.input_data[ip+i:ip+i+self.min_match_len], self.small_hash_bits)
                        self.large_hash_table[hash_l] = ip + i
                        self.small_hash_table[hash_s] = ip + i
                    prev_ip = ip + ml
                    ip += ml
                    pbar.update(ml)
                else:
                    self.large_hash_table[hash_l] = ip
                    self.small_hash_table[hash_s] = ip
                    ip += 1
                    pbar.update(1)

                    



