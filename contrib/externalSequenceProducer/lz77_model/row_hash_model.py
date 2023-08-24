from lz77_base_model import LZ77BaseModel
from hash_func import hash_func
import tqdm
from seq_checker import SeqChecker


class RowHashModel(LZ77BaseModel):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts):
        LZ77BaseModel.__init__(self, input_reader=input_reader, seq_writter=seq_writter,
                               window_log=window_log, hash_cover_bytes=hash_cover_bytes, min_match_len=min_match_len, max_match_len=(1<<16))

        self.hash_log = hash_log
        self.row_log = row_log
        self.tag_bits = tag_bits
        self.nb_attempts = nb_attempts
        self.row_size = 1 << self.row_log

        self.hash_bits = hash_log - row_log + tag_bits
        self.hash_table = {}
        self.seq_checker = SeqChecker(self.input_data)

    def row_tag_hash(self, ip):
        original_hash_value = hash_func(
            self.input_data[ip:ip+self.hash_cover_bytes], self.hash_bits)
        tag = original_hash_value & ((1 << self.tag_bits) - 1)
        row = (original_hash_value >> self.tag_bits) & (
            (1 << (self.hash_log - self.row_log)) - 1)
        return row, tag

    def update_hash_row(self, hash_row, ip, tag):
        hash_row.insert(0, (ip, tag))
        if len(hash_row) > self.row_size:
            hash_row.pop(len(hash_row) - 1)

    def process(self):
        ip = 0
        prev_ip = 0
        with tqdm.tqdm(total=self.ilimit) as pbar:
            while ip < self.ilimit:
                row_idx, tag = self.row_tag_hash(ip)
                if row_idx not in self.hash_table:
                    self.hash_table[row_idx] = []
                hash_row = self.hash_table[row_idx]
                match_length = 0
                offset = 0
                nb_attempts = self.nb_attempts
                for (history_addr, history_tag) in hash_row:
                    if history_tag == tag and ip - history_addr < self.window_size:
                        ml = self.count_match_length(ip, history_addr)
                        if ml > self.min_match_len and ml > match_length:
                            match_length = ml
                            offset = ip - history_addr
                        nb_attempts -= 1
                    if nb_attempts == 0:
                        break
                if offset > 0:
                    # self.seq_checker.check(offset, ip - prev_ip, match_length)
                    self.seq_writter.write_seq(
                        offset, ip - prev_ip, match_length)
                    for i in range(match_length):
                        row_idx, tag = self.row_tag_hash(ip + i)
                        if row_idx not in self.hash_table:
                            self.hash_table[row_idx] = []
                        self.update_hash_row(
                            self.hash_table[row_idx], ip + i, tag)
                    prev_ip = ip + match_length
                    ip += match_length
                    pbar.update(match_length)
                else:
                    self.update_hash_row(hash_row, ip, tag)
                    ip += 1
                    pbar.update(1)