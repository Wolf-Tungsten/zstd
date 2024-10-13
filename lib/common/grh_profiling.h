#ifndef GRH_PROFILING_H
#define GRH_PROFILING_H
extern long grh_profiling_ml_histogram[2048];
extern long grh_profiling_offset_histogram[2048];
void update_grh_ml_histogram(int ml);
void update_grh_offset_histogram(int offset);
void print_grh_profiling();
#endif