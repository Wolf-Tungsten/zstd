#ifndef VTUNE_ITT_H
#define VTUNE_ITT_H
#include <ittnotify.h>

extern __itt_domain* vtune_dist_histogram_domain;
extern __itt_string_handle* vtune_dist_histogram_handle;

void vtune_itt_init(void);
void vtune_itt_done(void);
void update_dist_histogram(uint64_t offset);
void update_match_length_histogram(uint64_t ml);
#endif