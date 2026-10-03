043faf68 ldr      w8, [sp, #0x78]
043faf6c cmp      w8, #0x26
043faf70 b.lo     #0x43faf9c
043faf74 ldr      w23, [sp, #0x64]
043faf78 mov      x0, x19
043faf7c mov      w1, #-1
043faf80 mov      x2, xzr
043faf84 bl       #0x46bbf90 ; MessagePacket.ReadByte
043faf88 sub      w23, w23, #1
043faf8c cmp      w23, #1
043faf90 b.gt     #0x43faf78
043faf94 ldr      x23, [x20, #0xa0]
043faf98 cbz      x23, #0x4405ef0
043faf9c mov      x0, x19
043fafa0 mov      w1, #-1
043fafa4 mov      x2, xzr
043fafa8 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fafac ldr      w8, [x23, #0x18]
043fafb0 cmp      w22, w8
043fafb4 b.hs     #0x4405ef4
043fafb8 umaddl   x8, w22, w26, x23
043fafbc strb     w0, [x8, #0x68]
043fafc0 ldr      x23, [x20, #0xa0]
043fafc4 cbz      x23, #0x4405ef0
043fafc8 mov      x0, x19
043fafcc mov      w1, #-1
043fafd0 mov      x2, xzr
043fafd4 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fafd8 ldr      w8, [x23, #0x18]
043fafdc cmp      w22, w8
043fafe0 b.hs     #0x4405ef4
043fafe4 umaddl   x8, w22, w26, x23
043fafe8 strh     w0, [x8, #0x6a]
043fafec ldr      w8, [sp, #0x84]
043faff0 add      w25, w25, #1
043faff4 cmp      w25, w8
043faff8 b.ne     #0x43fa86c
043faffc b        #0x43fb818
