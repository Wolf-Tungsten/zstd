class SeqChecker(object):
    def __init__(self, raw_input):
        self.raw_input = raw_input
        self.check_buffer = bytearray()
        self.checked_pos = 0

    def check(self, offset, lit_len, match_len):
        # print(offset, lit_len, match_len)
        # if self.checked_pos <= 360807 and self.checked_pos + lit_len + match_len >= 360807:
        #     print("checked_pos=%d, offset=%d, lit_len=%d, match_len=%d" % (self.checked_pos, offset, lit_len, match_len))
        #     exit(1)
        # copy lit_len bytes from raw_input start at checked_pos into check_buffer
        self.check_buffer.extend(self.raw_input[self.checked_pos:self.checked_pos + lit_len])
        # advanced check_pos
        self.checked_pos += lit_len
        # check match correctness while advancing checked_pos
        for i in range(match_len):
            self.check_buffer.append(self.check_buffer[self.checked_pos - offset])
            if self.check_buffer[self.checked_pos] != self.raw_input[self.checked_pos]:
                print("check failed at %d" % (self.checked_pos))
                print("offset=%d, lit_len=%d, match_len=%d" % (offset, lit_len, match_len))
                assert(False)
            self.checked_pos += 1
        