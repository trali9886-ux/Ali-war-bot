0332cb24 adrp     x20, #0x81e3000
0332cb28 ldr      x20, [x20, #0x360]
0332cb2c ldr      x0, [x20]
0332cb30 ldr      w8, [x0, #0xe4]
0332cb34 cbnz     w8, #0x332cb3c
0332cb38 bl       #0x30df7e4
0332cb3c mov      x0, xzr
0332cb40 bl       #0x4f8ee54
0332cb44 cbz      x0, #0x332cbf8
0332cb48 ldrh     w0, [x0, #0x1ee]
0332cb4c mov      x1, xzr
0332cb50 bl       #0x44dff78
0332cb54 tbz      w0, #0, #0x332cb90
0332cb58 ldr      x0, [x20]
0332cb5c ldr      w8, [x0, #0xe4]
0332cb60 cbnz     w8, #0x332cb68
0332cb64 bl       #0x30df7e4
0332cb68 mov      x0, xzr
0332cb6c bl       #0x4f8ee54
0332cb70 cbz      x0, #0x332cbf8
0332cb74 ldrh     w21, [x0, #0x1ee]
0332cb78 mov      x0, xzr
0332cb7c bl       #0x4f8ee54
0332cb80 cbz      x0, #0x332cbf8
0332cb84 ldrh     w8, [x0, #0x178]
0332cb88 cmp      w21, w8
0332cb8c b.ne     #0x332cbc4
0332cb90 ldp      x20, x19, [sp, #0x20]
0332cb94 ldp      x22, x21, [sp, #0x10]
0332cb98 ldr      x30, [sp], #0x30
0332cb9c ret      
0332cba0 mov      x0, xzr
0332cba4 bl       #0x3210714
0332cba8 cbz      x0, #0x332cbf8
0332cbac mov      x1, x19
0332cbb0 ldp      x20, x19, [sp, #0x20]
0332cbb4 ldp      x22, x21, [sp, #0x10]
0332cbb8 mov      x2, xzr
0332cbbc ldr      x30, [sp], #0x30
0332cbc0 b        #0x32400d4
0332cbc4 ldr      x0, [x20]
0332cbc8 ldr      w8, [x0, #0xe4]
0332cbcc cbnz     w8, #0x332cbd4
0332cbd0 bl       #0x30df7e4
0332cbd4 mov      x0, xzr
0332cbd8 bl       #0x4f8ee54
0332cbdc cbz      x0, #0x332cbf8
0332cbe0 mov      x1, x19
0332cbe4 ldp      x20, x19, [sp, #0x20]
0332cbe8 ldp      x22, x21, [sp, #0x10]
0332cbec mov      x2, xzr
0332cbf0 ldr      x30, [sp], #0x30
0332cbf4 b        #0x43fa3a8 ; MapManager.RecvMapInfoPlus
