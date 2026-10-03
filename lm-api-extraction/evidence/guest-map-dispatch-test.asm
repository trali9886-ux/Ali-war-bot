0332c474 cmp      w8, #0x4d7
0332c478 b.eq     #0x332c860
0332c47c cmp      w8, #0x8ac
0332c480 b.ne     #0x332cb90
0332c484 adrp     x20, #0x81e3000
0332c488 ldr      x20, [x20, #0x360]
0332c48c ldr      x0, [x20]
0332c490 ldr      w8, [x0, #0xe4]
0332c494 cbnz     w8, #0x332c49c
0332c498 bl       #0x30df7e4
0332c49c mov      x0, xzr
0332c4a0 bl       #0x4f8ee54
0332c4a4 cbz      x0, #0x332cbf8
0332c4a8 ldrh     w0, [x0, #0x1ee]
0332c4ac mov      x1, xzr
0332c4b0 bl       #0x44dff78
0332c4b4 tbz      w0, #0, #0x332cb58
0332c4b8 b        #0x332cb90
