043fcbdc ldrb     w8, [x20, #0x2f9]
043fcbe0 cmp      w8, #0x3d
043fcbe4 b.lo     #0x43fcc08
043fcbe8 sub      w22, w8, #0x3b
043fcbec mov      x0, x19
043fcbf0 mov      w1, #-1
043fcbf4 mov      x2, xzr
043fcbf8 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fcbfc sub      w22, w22, #1
043fcc00 cmp      w22, #1
043fcc04 b.hi     #0x43fcbec
043fcc08 ldr      w8, [sp, #0x84]
043fcc0c add      w24, w24, #1
043fcc10 cmp      w24, w8
043fcc14 b.ne     #0x43fb828
043fcc18 ldr      w8, [sp, #0x60]
043fcc1c mov      w26, #0x50
043fcc20 cmp      w8, #0x17
043fcc24 b.ne     #0x4405288
043fcc28 ldrb     w8, [x20, #0x28]
043fcc2c cbz      w8, #0x43fcc6c
043fcc30 mov      x22, xzr
043fcc34 ldr      x8, [x20, #0x30]
043fcc38 cbz      x8, #0x4405ef0
043fcc3c ldr      w9, [x8, #0x18]
043fcc40 cmp      x22, x9
043fcc44 b.hs     #0x4405ef4
043fcc48 add      x8, x8, x22, lsl #1
043fcc4c mov      x0, x20
043fcc50 mov      x2, xzr
043fcc54 ldrh     w1, [x8, #0x20]
043fcc58 bl       #0x44e7c78
043fcc5c ldrb     w8, [x20, #0x28]
043fcc60 add      x22, x22, #1
043fcc64 cmp      x22, x8
043fcc68 b.lo     #0x43fcc34
043fcc6c strb     wzr, [x20, #0x28]
043fcc70 b        #0x4405288
