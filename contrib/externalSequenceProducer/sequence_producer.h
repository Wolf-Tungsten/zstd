/*
 * Copyright (c) Yann Collet, Meta Platforms, Inc.
 * All rights reserved.
 *
 * This source code is licensed under both the BSD-style license (found in the
 * LICENSE file in the root directory of this source tree) and the GPLv2 (found
 * in the COPYING file in the root directory of this source tree).
 * You may select, at your option, one of the above-listed licenses.
 */

#ifndef MATCHFINDER_H
#define MATCHFINDER_H

#define ZSTD_STATIC_LINKING_ONLY
#include "zstd.h"
#include "stdint.h"

#define SIMULATOR_SLICE_LOG 13
#define SIMULATOR_SLICE_SIZE (1 << SIMULATOR_SLICE_LOG)

typedef struct {
    int isFirstBlock;
    void* firstBlockStartPtr;
    void* prevBlockStartPtr;
    size_t prevBlockSize;
    uint64_t* seqBuffer;
    uint64_t* indexBuffer;
    size_t seqAmount;
    size_t indexAmount;
} SimulatorState;

typedef struct {
  uint32_t prevSeqAmount;
  uint16_t encodeLength;
  uint8_t eof;
} SimulatorIndex;


size_t simpleSequenceProducer(
  void* sequenceProducerState,
  ZSTD_Sequence* outSeqs, size_t outSeqsCapacity,
  const void* src, size_t srcSize,
  const void* dict, size_t dictSize,
  int compressionLevel,
  size_t windowSize
);

size_t simulatorSequenceProducer(
  void* sequenceProducerState,
  ZSTD_Sequence* outSeqs, size_t outSeqsCapacity,
  const void* src, size_t srcSize,
  const void* dict, size_t dictSize,
  int compressionLevel,
  size_t windowSize
);



#endif
