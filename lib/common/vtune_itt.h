#include "ittnotify.h"

extern __itt_domain* itt_domain_compressBlock;
extern __itt_string_handle* itt_handle_block;
extern __itt_string_handle* itt_handle_lz77;
extern __itt_string_handle* itt_handle_entropy;

void vtune_itt_init(void);
void vtune_update_dist_histogram(uint32_t);
void vtune_update_match_length_histogram(uint32_t);
void vtune_itt_finalize(void);
