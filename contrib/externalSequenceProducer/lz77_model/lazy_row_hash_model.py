from row_hash_model import RowHashModel
import tqdm
from enum import Enum

class LazyState(Enum):
    lazy0 = 0
    lazy1 = 1
    lazy2 = 2
    commit = -1

class LazyRowHashModel(RowHashModel):
    def __init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts):
        RowHashModel.__init__(self, input_reader, seq_writter, window_log, hash_cover_bytes, min_match_len, hash_log, row_log, tag_bits, nb_attempts)
        self.offset_1 = 1
        self.offset_2 = 0
        self.next_hash_insert_ip = 0
        self.next_encode_ip = 0
        self.lazy_state = LazyState.lazy0

    def update_hash_table(self, ip):
        while ip - self.next_hash_insert_ip > 1:
            row_idx, tag = self.row_tag_hash(self.next_hash_insert_ip)
            if row_idx not in self.hash_table:
                self.hash_table[row_idx] = []
            self.update_hash_row(self.hash_table[row_idx], self.next_hash_insert_ip, tag)
            self.next_hash_insert_ip += 1


    def row_find_best_match(self, ip):
        self.update_hash_table(ip)
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
                if ml >= self.min_match_len and ml > match_length:
                    match_length = ml
                    offset = ip - history_addr
                nb_attempts -= 1
            if nb_attempts == 0:
                break
        return offset, match_length

    def check_rep_offset_1(self, ip):
        if self.offset_1 > 0 and self.offset_1 < self.window_size:
            return self.offset_1, self.count_match_length(ip, ip - self.offset_1)
        else:
            return 0, 0
    
    def check_rep_offset_2(self, ip):
        if self.offset_2 > 0 and self.offset_2 < self.window_size:
            return self.offset_2, self.count_match_length(ip, ip - self.offset_2)
        else:
            return 0, 0
        
    def catch_up_count(self, ip, offset):
        catch_up_len = 0
        while catch_up_len < ip - self.next_encode_ip and self.input_data[ip - offset - 1 - catch_up_len] == self.input_data[ip - 1 - catch_up_len]:
            catch_up_len += 1
        return catch_up_len
    
    def bit_count(self, offset):
        return len(bin(offset)) - 2
    
    def process(self):
        with tqdm.tqdm(total=self.ilimit) as pbar:
            offset = 0
            match_length = 0
            enhanced_ip = 0
            ip = 0
            while ip < self.ilimit:
                enhanced = False
                o, ml = self.check_rep_offset_1(ip)
                if self.lazy_state == LazyState.lazy0:
                    if ml >= self.min_match_len and ml > match_length:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                elif self.lazy_state == LazyState.lazy1:
                    # int const gain2 = (int)(mlRep * 3);
                    # int const gain1 = (int)(matchLength*3 - ZSTD_highbit32((U32)offBase) + 1);
                    gain2 = ml * 3
                    gain1 = match_length * 3 - self.bit_count(offset) + 1
                    if ml >= self.min_match_len and gain2 > gain1:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                elif self.lazy_state == LazyState.lazy2:
                    gain2 = ml * 4
                    gain1 = match_length * 4 - self.bit_count(offset) + 1
                    if ml >= self.min_match_len and gain2 > gain1:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                
                o, ml = self.row_find_best_match(ip)
                if self.lazy_state == LazyState.lazy0:
                    if ml >= self.min_match_len and ml > match_length:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                elif self.lazy_state == LazyState.lazy1:
                    gain2 = ml * 4 - self.bit_count(o)
                    gain1 = match_length * 4 - self.bit_count(offset) + 4
                    if ml >= self.min_match_len and gain2 > gain1:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                elif self.lazy_state == LazyState.lazy2:
                    gain2 = ml * 4 - self.bit_count(o)
                    gain1 = match_length * 4 - self.bit_count(offset) + 7
                    if ml >= self.min_match_len and gain2 > gain1:
                        offset = o
                        match_length = ml
                        enhanced_ip = ip
                        enhanced = True
                
                if self.lazy_state == LazyState.lazy0:
                    if enhanced:
                        self.lazy_state = LazyState.lazy1
                        ip += 1
                        continue
                    else:
                        self.lazy_state = LazyState.commit
                elif self.lazy_state == LazyState.lazy1:
                    if enhanced:
                        self.lazy_state = LazyState.lazy1
                        ip += 1
                        continue
                    else:
                        self.lazy_state = LazyState.lazy2
                        ip += 1
                        continue
                elif self.lazy_state == LazyState.lazy2:
                    if enhanced:
                        self.lazy_state = LazyState.lazy1
                        ip += 1
                        continue
                    else:
                        self.lazy_state = LazyState.commit

                    
                assert(self.lazy_state == LazyState.commit)

                if match_length > 0:
                    assert(match_length >= self.min_match_len)
                    catch_up_len = self.catch_up_count(enhanced_ip, offset)
                    enhanced_ip -= catch_up_len
                    match_length += catch_up_len
                    self.seq_writter.write_seq(offset, enhanced_ip - self.next_encode_ip, match_length)
                    pbar.update(enhanced_ip + match_length - self.next_encode_ip)
                    self.next_encode_ip = enhanced_ip + match_length
                    ip = self.next_encode_ip
                    self.lazy_state = LazyState.lazy0
                    self.offset_1 = offset
                    self.offset_2 = self.offset_1
                    match_length = 0
                    offset = 0
                else:
                    ip += 1
                    self.lazy_state = LazyState.lazy0
                    #pbar.update(1)
                    #self.seq_writter.write_seq(offset, ip - prev_ip + lazy_bias, match_length)
