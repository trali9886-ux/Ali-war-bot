043faa04 mov      x0, x20
043faa08 mov      w1, w27
043faa0c mov      x2, xzr
043faa10 bl       #0x44df81c ; MapManager.IsCityOrCamp
043faa14 tbz      w0, #0, #0x43fad38
043faa18 ldr      x23, [x20, #0x68]
043faa1c cbz      x23, #0x4405ef0
043faa20 ldr      x0, [x20, #0x98]
043faa24 cbz      x0, #0x4405ef0
043faa28 mov      x1, xzr
043faa2c bl       #0x34a53f8
043faa30 ldr      w8, [x23, #0x18]
043faa34 cmp      w27, w8
043faa38 b.hs     #0x4405ef4
043faa3c add      x8, x23, x22
043faa40 strh     w0, [x8, #0x20]
043faa44 ldr      x8, [x20, #0xa0]
043faa48 cbz      x8, #0x4405ef0
043faa4c ldr      w9, [x8, #0x18]
043faa50 and      w22, w0, #0xffff
043faa54 cmp      w22, w9
043faa58 b.hs     #0x4405ef4
043faa5c umaddl   x8, w22, w26, x8
043faa60 mov      x0, x19
043faa64 mov      w1, #0xd
043faa68 mov      w3, #-1
043faa6c mov      x4, xzr
043faa70 ldr      x2, [x8, #0x50]
043faa74 bl       #0x46bc004
043faa78 ldr      x8, [x20, #0xa0]
043faa7c cbz      x8, #0x4405ef0
043faa80 ldr      w9, [x8, #0x18]
043faa84 cmp      w22, w9
043faa88 b.hs     #0x4405ef4
043faa8c umaddl   x8, w22, w26, x8
043faa90 mov      x0, x19
043faa94 mov      w1, #3
043faa98 mov      w3, #-1
043faa9c mov      x4, xzr
043faaa0 ldr      x2, [x8, #0x40]
043faaa4 bl       #0x46bc004
043faaa8 ldr      x23, [x20, #0xa0]
043faaac cbz      x23, #0x4405ef0
043faab0 mov      x0, x19
043faab4 mov      w1, #-1
043faab8 mov      x2, xzr
043faabc bl       #0x46bbe78 ; MessagePacket.ReadUShort
043faac0 ldr      w8, [x23, #0x18]
043faac4 cmp      w22, w8
043faac8 b.hs     #0x4405ef4
043faacc umaddl   x8, w22, w26, x23
043faad0 strh     w0, [x8, #0x34]
043faad4 ldr      x23, [x20, #0xa0]
043faad8 cbz      x23, #0x4405ef0
043faadc mov      x0, x19
043faae0 mov      w1, #-1
043faae4 mov      x2, xzr
043faae8 bl       #0x46bbf90 ; MessagePacket.ReadByte
043faaec ldr      w8, [x23, #0x18]
043faaf0 cmp      w22, w8
043faaf4 b.hs     #0x4405ef4
043faaf8 umaddl   x8, w22, w26, x23
043faafc strb     w0, [x8, #0x38]
043fab00 ldr      x23, [x20, #0xa0]
043fab04 cbz      x23, #0x4405ef0
043fab08 mov      x0, x19
043fab0c mov      w1, #-1
043fab10 mov      x2, xzr
043fab14 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fab18 ldr      w8, [x23, #0x18]
043fab1c cmp      w22, w8
043fab20 b.hs     #0x4405ef4
043fab24 umaddl   x8, w22, w26, x23
043fab28 strb     w0, [x8, #0x39]
043fab2c ldr      x23, [x20, #0xa0]
043fab30 cbz      x23, #0x4405ef0
043fab34 mov      x0, x19
043fab38 mov      w1, #-1
043fab3c mov      x2, xzr
043fab40 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fab44 ldr      w8, [x23, #0x18]
043fab48 cmp      w22, w8
043fab4c b.hs     #0x4405ef4
043fab50 umaddl   x8, w22, w26, x23
043fab54 strb     w0, [x8, #0x3c]
043fab58 ldr      x23, [x20, #0xa0]
043fab5c cbz      x23, #0x4405ef0
043fab60 mov      x0, x19
043fab64 mov      w1, #-1
043fab68 mov      x2, xzr
043fab6c bl       #0x46bbf90 ; MessagePacket.ReadByte
043fab70 ldr      w8, [x23, #0x18]
043fab74 cmp      w22, w8
043fab78 b.hs     #0x4405ef4
043fab7c umaddl   x8, w22, w26, x23
043fab80 strb     w0, [x8, #0x3d]
043fab84 ldr      x23, [x20, #0xa0]
043fab88 cbz      x23, #0x4405ef0
043fab8c mov      x0, x19
043fab90 mov      w1, #-1
043fab94 mov      x2, xzr
043fab98 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fab9c ldr      w8, [x23, #0x18]
043faba0 cmp      w22, w8
043faba4 b.hs     #0x4405ef4
043faba8 umaddl   x8, w22, w26, x23
043fabac strh     w0, [x8, #0x58]
043fabb0 ldr      x23, [x20, #0xa0]
043fabb4 cbz      x23, #0x4405ef0
043fabb8 mov      x0, x19
043fabbc mov      w1, #-1
043fabc0 mov      x2, xzr
043fabc4 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fabc8 ldr      w8, [x23, #0x18]
043fabcc cmp      w22, w8
043fabd0 b.hs     #0x4405ef4
043fabd4 umaddl   x8, w22, w26, x23
043fabd8 strb     w0, [x8, #0x5a]
043fabdc ldr      x23, [x20, #0xa0]
043fabe0 cbz      x23, #0x4405ef0
043fabe4 mov      x0, x19
043fabe8 mov      w1, #-1
043fabec mov      x2, xzr
043fabf0 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fabf4 ldr      w8, [x23, #0x18]
043fabf8 cmp      w22, w8
043fabfc b.hs     #0x4405ef4
043fac00 umaddl   x8, w22, w26, x23
043fac04 strb     w0, [x8, #0x5b]
043fac08 ldr      x23, [x20, #0xa0]
043fac0c cbz      x23, #0x4405ef0
043fac10 mov      x0, x19
043fac14 mov      w1, #-1
043fac18 mov      x2, xzr
043fac1c bl       #0x46bbf90 ; MessagePacket.ReadByte
043fac20 ldr      w8, [x23, #0x18]
043fac24 cmp      w22, w8
043fac28 b.hs     #0x4405ef4
043fac2c umaddl   x8, w22, w26, x23
043fac30 strb     w0, [x8, #0x5c]
043fac34 ldr      x23, [x20, #0xa0]
043fac38 cbz      x23, #0x4405ef0
043fac3c mov      x0, x19
043fac40 mov      w1, #-1
043fac44 mov      x2, xzr
043fac48 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fac4c ldr      w8, [x23, #0x18]
043fac50 cmp      w22, w8
043fac54 b.hs     #0x4405ef4
043fac58 umaddl   x8, w22, w26, x23
043fac5c strb     w0, [x8, #0x5d]
043fac60 ldr      x23, [x20, #0xa0]
043fac64 cbz      x23, #0x4405ef0
043fac68 mov      x0, x19
043fac6c mov      w1, #-1
043fac70 mov      x2, xzr
043fac74 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fac78 ldr      w8, [x23, #0x18]
043fac7c cmp      w22, w8
043fac80 b.hs     #0x4405ef4
043fac84 umaddl   x8, w22, w26, x23
043fac88 strb     w0, [x8, #0x5e]
043fac8c ldr      x23, [x20, #0xa0]
043fac90 cbz      x23, #0x4405ef0
043fac94 mov      x24, xzr
043fac98 ldr      w8, [x23, #0x18]
043fac9c cmp      w22, w8
043faca0 b.hs     #0x4405ef4
043faca4 umaddl   x8, w22, w26, x23
043faca8 ldr      x27, [x8, #0x60]
043facac cbz      x27, #0x4405ef0
043facb0 ldrsw    x8, [x27, #0x18]
043facb4 cmp      x24, x8
043facb8 b.ge     #0x43faf68
043facbc mov      x0, x19
043facc0 mov      w1, #-1
043facc4 mov      x2, xzr
043facc8 bl       #0x46bbf90 ; MessagePacket.ReadByte
043faccc ldr      w8, [x27, #0x18]
043facd0 cmp      x24, x8
043facd4 b.hs     #0x4405ef4
043facd8 add      x8, x27, x24
043facdc add      x24, x24, #1
043face0 strb     w0, [x8, #0x20]
043face4 ldr      x23, [x20, #0xa0]
043face8 cbnz     x23, #0x43fac98
043facec b        #0x4405ef0
