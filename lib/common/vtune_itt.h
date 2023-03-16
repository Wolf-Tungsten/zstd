#include "ittnotify.h"

extern __itt_domain* itt_domain_compressBlock;
extern __itt_string_handle* itt_handle_block;
extern __itt_string_handle* itt_handle_lz77;
extern __itt_string_handle* itt_handle_entropy;

extern __itt_domain* itt_domain_compressBlock_lz77;

void vtune_itt_init(void);

