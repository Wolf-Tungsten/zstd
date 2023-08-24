from hash_func import hash_func
from lz77_base_model import LZ77BaseModel
import tqdm

class OrthogonalHashModel(LZ77BaseModel):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, max_match_len, hash_log, row_log, tag_bits, nb_attempts, bank_log, parallel_width):
        super().__init__(input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, max_match_len)
        self.hash_log = hash_log
        self.row_log = row_log
        self.tag_bits = tag_bits
        self.nb_attempts = nb_attempts
        self.row_size = 1 << self.row_log
        self.bank_log = bank_log
        self.parallel_width = parallel_width

        self.hash_bits = hash_log - row_log + tag_bits
        self.hash_table = {}
        self.bank_conflict_book = {}

        self.stat_attempts_hist = [0 for _ in range(self.nb_attempts + 1)]

    def bank_row_tag_hash(self, ip):
        original_hash_value = hash_func(
            self.input_data[ip:ip+self.hash_cover_bytes], self.hash_bits)
        tag = original_hash_value & ((1 << self.tag_bits) - 1)
        row = (original_hash_value >> self.tag_bits) & (
            (1 << (self.hash_log - self.row_log)) - 1)
        bank_idx = row & ((1 << self.bank_log) - 1)
        return bank_idx, row, tag 

    def process(self):
        ip = 0
        prev_ip = 0
        with tqdm.tqdm(total=self.ilimit) as pbar:
            while ip < self.ilimit:
                bank_idx, row_idx, tag = self.bank_row_tag_hash(ip)
                if row_idx not in self.hash_table:
                    self.hash_table[row_idx] = [[False, 0, 0] for _ in range(self.row_size)]
                hash_row = self.hash_table[row_idx]
                match_length = 0
                offset = 0
                nb_attempts = self.nb_attempts
                if ip % self.parallel_width == 0:
                    self.bank_conflict_book = {}
                if bank_idx not in self.bank_conflict_book:
                    self.bank_conflict_book[bank_idx] = {}
                    for (history_valid, history_addr, history_tag) in hash_row:
                        if history_valid and history_tag == tag and ip - history_addr < self.window_size:
                            ml = self.count_match_length(ip, history_addr)
                            if ml > self.min_match_len and ml > match_length:
                                match_length = ml
                                offset = ip - history_addr
                            nb_attempts -= 1
                        if nb_attempts == 0:
                            break
                    self.stat_attempts_hist[self.nb_attempts - nb_attempts] += 1
                if offset > 0:
                    # self.seq_checker.check(offset, ip - prev_ip, match_length)
                    self.seq_writter.write_seq(
                        offset, ip - prev_ip, match_length)
                    for i in range(match_length):
                        bank_idx, row_idx, tag = self.bank_row_tag_hash(ip + i)
                        if row_idx not in self.hash_table:
                            self.hash_table[row_idx] = [[False, 0, 0] for _ in range(self.row_size)]
                        self.hash_table[row_idx][(ip + i) % self.row_size] = [True, ip + i, tag]
                    prev_ip = ip + match_length
                    ip += match_length
                    pbar.update(match_length)
                else:
                    self.hash_table[row_idx][ip % self.row_size] = [True, ip, tag]
                    ip += 1
                    pbar.update(1)

    def print_stat(self):
        print("Attempts histogram:")
        for i in range(self.nb_attempts + 1):
            print("{}: {}".format(i, self.stat_attempts_hist[i]))


