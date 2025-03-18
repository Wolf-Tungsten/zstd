from row_hash_table import RowHashTable

class MetaHashTable(object):
    def __init__(self, input_reader, window_log, hash_log, row_log, hash_cover_bytes, parallel_width, bank_log, min_match_len, meta_len, hqt):
        self.input_data = input_reader.read()
        self.window_log = window_log
        self.hash_log = hash_log
        self.row_log = row_log
        self.hash_cover_bytes = hash_cover_bytes
        self.parallel_width = parallel_width
        self.bank_log = bank_log
        self.meta_len = meta_len
        self.min_match_len = min_match_len
        self.hqt = hqt

        self.bank_num = 1 << self.bank_log
        self.row_idx_bits = self.hash_log - self.row_log - self.bank_log
        self.hash_bits = self.bank_log + self.row_idx_bits
        self.conflict_book = [0 for _ in range(self.bank_num)]
        self.bank_hash_table = [{} for _ in range(self.bank_num)]
        self.window_size = 1 << self.window_log
        self.row_size = 1 << self.row_log

    def __hash_func(self, raw_bytes, output_bits):
        # concat raw_bytes as a integer
        raw_bytes_int = int.from_bytes(raw_bytes, byteorder='little')
        prime = [0, 0, 0, 506832829, 2654435761, 889523592379, 227718039650203, 58295818150454627, 0xCF1BBCDCB7A56463]
        input_bytes = len(raw_bytes)
        if input_bytes <= 4:
            return ((raw_bytes_int * prime[input_bytes]) & (0xFFFFFFFF)) >> (32 - output_bits)
        else:
            return (((raw_bytes_int << (64-input_bytes*8)) * prime[input_bytes]) & (0xFFFFFFFFFFFFFFFF)) >> (64 - output_bits)

    def bank_row_meta_hash(self, ip):
        original_hash_value = self.__hash_func(
            self.input_data[ip:ip+self.hash_cover_bytes], self.hash_bits)
        meta_history = self.input_data[ip:ip+self.meta_len]
        row_idx = original_hash_value & ((1 << self.row_idx_bits) - 1)
        bank_idx = (original_hash_value >> self.row_idx_bits) & ((1 << self.bank_log) - 1)
        return bank_idx, row_idx, meta_history 
    
    def update_and_read(self, ip):
        bank_idx, row_idx, meta_history = self.bank_row_meta_hash(ip)
        # 判断是否冲突
        if ip % self.parallel_width == 0:
            self.conflict_book = [0 for _ in range(self.bank_num)]
        if self.conflict_book[bank_idx] >= self.hqt:
            self.conflict_book[bank_idx] += 1
            return []
        # 无冲突可以继续进行
        if row_idx not in self.bank_hash_table[bank_idx]:
            self.bank_hash_table[bank_idx][row_idx] = []
        res = []
        for slot in self.bank_hash_table[bank_idx][row_idx]:
            if ip - slot[0] < self.window_size:
                meta_match_len = 0
                while meta_match_len < self.meta_len and meta_history[meta_match_len] == slot[1][meta_match_len]:
                    meta_match_len += 1
                if meta_match_len >= self.min_match_len:
                    res.append((slot[0], meta_match_len))
        self.bank_hash_table[bank_idx][row_idx].append((ip, meta_history))
        if len(self.bank_hash_table[bank_idx][row_idx]) > self.row_size:
            self.bank_hash_table[bank_idx][row_idx].pop(0)
        return res