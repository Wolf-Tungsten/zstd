from row_hash_model import RowHashModel
import tqdm

class ConflictRowHashModel(RowHashModel):
    def __init__(self,  input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts, bank_log, parallel_width):
        RowHashModel.__init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts)
        self.bank_log = bank_log
        self.parallel_width = parallel_width
        self.conflict_table = {}
    
    def check_conflict(self, row_idx, ip):
        if ip % self.parallel_width == 0:
            self.conflict_table = {}
        # take the high bank_log bits of row_idx as the bank index
        bank_idx = row_idx >> (self.hash_log - self.row_log - self.bank_log)
        if bank_idx not in self.conflict_table:
            self.conflict_table[bank_idx] = {}
            return False
        else:
            return True

    def process(self):
        ip = 0
        prev_ip = 0
        with tqdm.tqdm(total=self.ilimit) as pbar:
            while ip < self.ilimit:
                row_idx, tag = self.row_tag_hash(ip)
                if self.check_conflict(row_idx, ip):
                    # has hash conflict, just skip it
                    ip += 1
                    pbar.update(1)
                    continue
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
                        if self.check_conflict(row_idx, ip + i):
                            continue
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