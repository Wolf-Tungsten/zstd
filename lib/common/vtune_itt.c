#include "ittnotify.h"

__itt_domain* itt_domain_compressBlock;
__itt_string_handle* itt_handle_block;
__itt_string_handle* itt_handle_lz77;
__itt_string_handle* itt_handle_entropy;

__itt_domain* itt_domain_compressBlock_lz77;


void vtune_itt_init(void)
{
    itt_domain_compressBlock = __itt_domain_create("compressBlock");
    itt_domain_compressBlock ->flags = 1;
    itt_handle_block = __itt_string_handle_create("block");
    itt_handle_lz77 = __itt_string_handle_create("lz77");
    itt_handle_entropy = __itt_string_handle_create("entropy");

    itt_domain_compressBlock_lz77 = __itt_domain_create("compressBlock.lz77");
    
}