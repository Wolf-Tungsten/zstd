from row_hash_model import RowHashModel
import tqdm

class LazyRowHashModel(RowHashModel):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts, lazy_depth):
        RowHashModel.__init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts)
        self.lazy_depth = lazy_depth

    def search(self, ip):
        row_idx, tag = self.row_tag_hash(ip)
        if row_idx not in self.hash_table:
            return 0, 0
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
        return offset, match_length
    
    def process(self):
        ip = 0
        prev_ip = 0
        with tqdm.tqdm(total=self.ilimit) as pbar:
            while ip < self.ilimit:
                offset = 0
                match_length = 0
                lazy_bias = 0
                for s in range(self.lazy_depth):
                    o, ml = self.search(ip + s)
                    if ml > match_length:
                        offset = o
                        match_length = ml
                        lazy_bias = s
                if offset > 0:
                    # self.seq_checker.check(offset, ip - prev_ip, match_length)
                    self.seq_writter.write_seq(
                        offset, ip - prev_ip + lazy_bias, match_length)
                    for i in range(match_length):
                        row_idx, tag = self.row_tag_hash(ip + i)
                        if row_idx not in self.hash_table:
                            self.hash_table[row_idx] = []
                        self.update_hash_row(
                            self.hash_table[row_idx], ip + i, tag)
                    prev_ip = ip + match_length + lazy_bias
                    ip += match_length + lazy_bias
                    pbar.update(match_length)
                else:
                    row_idx, tag = self.row_tag_hash(ip)
                    if row_idx not in self.hash_table:
                            self.hash_table[row_idx] = []
                    self.update_hash_row(self.hash_table[row_idx], ip, tag)
                    ip += 1
                    pbar.update(1)