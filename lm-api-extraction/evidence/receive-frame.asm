046cb380 ldr      x8, [x0, #0xb8]
046cb384 ldp      w9, w19, [x8, #0xb0]
046cb388 sub      w9, w9, w19
046cb38c cmp      w9, #3
046cb390 b.le     #0x46cb248
046cb394 ldr      w9, [x0, #0xe4]
046cb398 cbnz     w9, #0x46cb3ac
046cb39c bl       #0x30df7e4
046cb3a0 ldr      x8, [x21]
046cb3a4 ldr      x8, [x8, #0xb8]
046cb3a8 ldr      w19, [x8, #0xb4]
046cb3ac ldr      x0, [x22]
046cb3b0 ldr      x20, [x8, #0xa0]
046cb3b4 ldr      w9, [x0, #0xe4]
046cb3b8 cbnz     w9, #0x46cb3c0
046cb3bc bl       #0x30df7e4
046cb3c0 mov      x0, x20
046cb3c4 mov      w1, w19
046cb3c8 mov      x2, xzr
046cb3cc bl       #0x33e5124
046cb3d0 mov      w19, w0
046cb3d4 sub      w8, w0, #4
046cb3d8 ldr      x0, [x21]
046cb3dc and      w9, w8, #0xffff
046cb3e0 ldr      w8, [x0, #0xe4]
046cb3e4 cmp      w9, #0xffd
046cb3e8 b.hs     #0x46cb4e8
046cb3ec cbnz     w8, #0x46cb3f8
046cb3f0 bl       #0x30df7e4
046cb3f4 ldr      x0, [x21]
046cb3f8 ldr      x8, [x0, #0xb8]
046cb3fc and      w25, w19, #0xffff
046cb400 ldp      w9, w20, [x8, #0xb0]
046cb404 sub      w8, w9, w20
046cb408 cmp      w8, w25
046cb40c b.lt     #0x46cb248
046cb410 ldr      w8, [x0, #0xe4]
046cb414 cbnz     w8, #0x46cb428
046cb418 bl       #0x30df7e4
046cb41c ldr      x8, [x21]
046cb420 ldr      x8, [x8, #0xb8]
046cb424 ldr      w20, [x8, #0xb4]
046cb428 ldr      x0, [x23]
046cb42c bl       #0x30df900
046cb430 ldr      x8, [x21]
046cb434 mov      x19, x0
046cb438 sub      w3, w25, #4
046cb43c ldr      x8, [x8, #0xb8]
046cb440 add      x1, x8, #0xa0
046cb444 add      w2, w20, #4
046cb448 bl       #0x46c219c ; MessagePacket..ctor
046cb44c ldr      x8, [x21]
046cb450 ldr      x0, [x22]
046cb454 ldr      x8, [x8, #0xb8]
046cb458 ldr      w9, [x0, #0xe4]
046cb45c ldr      x20, [x8, #0xa0]
046cb460 ldr      w26, [x8, #0xb4]
046cb464 cbnz     w9, #0x46cb46c
046cb468 bl       #0x30df7e4
046cb46c add      w1, w26, #2
046cb470 mov      x0, x20
046cb474 mov      x2, xzr
046cb478 bl       #0x33e5124
046cb47c cbz      x19, #0x46cb554
046cb480 mov      w8, w0
046cb484 ldr      x0, [x19, #0x28]
046cb488 strh     w8, [x19, #0x30]
046cb48c cbz      x0, #0x46cb55c
046cb490 ldr      x8, [x21]
046cb494 ldr      x2, [x24]
046cb498 ldr      x8, [x8, #0xb8]
046cb49c ldr      x20, [x8, #0xa0]
046cb4a0 mov      w1, wzr
046cb4a4 bl       #0x6250920
046cb4a8 mov      w1, w0
046cb4ac ldr      w2, [x19, #0x18]
046cb4b0 mov      x0, x20
046cb4b4 mov      w3, wzr
046cb4b8 bl       #0x46c3058 ; NetworkManager.Cipher
046cb4bc ldr      x8, [x21]
046cb4c0 ldr      x8, [x8, #0xb8]
046cb4c4 ldr      x0, [x8, #0x88]
046cb4c8 cbz      x0, #0x46cb558
046cb4cc ldr      x8, [x0]
046cb4d0 ldr      x9, [x8, #0x238]
046cb4d4 ldr      x2, [x8, #0x240]
046cb4d8 mov      x1, x19
046cb4dc blr      x9
046cb4e0 ldr      x0, [x21]
046cb4e4 b        #0x46cb4f8
046cb4e8 cbnz     w8, #0x46cb4f4
046cb4ec bl       #0x30df7e4
046cb4f0 ldr      x0, [x21]
046cb4f4 mov      w25, #4
046cb4f8 ldr      x8, [x0, #0xb8]
046cb4fc ldr      w9, [x8, #0xb4]
046cb500 add      w9, w9, w25
046cb504 str      w9, [x8, #0xb4]
