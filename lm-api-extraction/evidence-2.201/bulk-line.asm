043fb818 and      w8, w29, #0x3f
043fb81c str      w8, [sp, #0x84]
043fb820 cbz      w8, #0x43fcc18
043fb824 mov      w24, wzr
043fb828 mov      x0, x19
043fb82c mov      w1, #-1
043fb830 mov      x2, xzr
043fb834 bl       #0x46c26e0
043fb838 mov      w25, w0
043fb83c mov      x0, x20
043fb840 mov      x2, xzr
043fb844 mov      w1, w25
043fb848 bl       #0x44e7bd4
043fb84c cmp      w0, #0x100, lsl #12
043fb850 b.ne     #0x43fb908
043fb854 adrp     x22, #0x81ff000
043fb858 adrp     x23, #0x81ff000
043fb85c ldr      x0, [x20, #0x100]
043fb860 ldr      x22, [x22, #0x5b8]
043fb864 ldr      x23, [x23, #0x5a0]
043fb868 cbz      x0, #0x4405ef0
043fb86c mov      x1, xzr
043fb870 bl       #0x34a53f8
043fb874 ldr      x27, [x20, #0x108]
043fb878 cbz      x27, #0x4405ef0
043fb87c mov      w26, w0
043fb880 ldr      w8, [x27, #0x18]
043fb884 cmp      w26, w8
043fb888 b.lt     #0x43fbdd0
043fb88c ldr      x0, [x22]
043fb890 bl       #0x30df900
043fb894 mov      x1, xzr
043fb898 mov      x28, x0
043fb89c bl       #0x45b2908
043fb8a0 ldr      w10, [x27, #0x1c]
043fb8a4 ldr      x8, [x27, #0x10]
043fb8a8 ldr      x9, [x23]
043fb8ac add      w10, w10, #1
043fb8b0 str      w10, [x27, #0x1c]
043fb8b4 cbz      x8, #0x4405ef0
043fb8b8 ldrsw    x10, [x27, #0x18]
043fb8bc ldr      w11, [x8, #0x18]
043fb8c0 cmp      w10, w11
043fb8c4 b.hs     #0x43fb8e4
043fb8c8 add      x0, x8, x10, lsl #3
043fb8cc add      w9, w10, #1
043fb8d0 mov      x1, x28
043fb8d4 str      w9, [x27, #0x18]
043fb8d8 str      x28, [x0, #0x20]!
043fb8dc bl       #0x30df614
043fb8e0 b        #0x43fb8fc
043fb8e4 ldr      x8, [x9, #0x20]
043fb8e8 mov      x0, x27
043fb8ec mov      x1, x28
043fb8f0 ldr      x8, [x8, #0xc0]
043fb8f4 ldr      x2, [x8, #0x70]
043fb8f8 bl       #0x5f32424
043fb8fc ldr      x27, [x20, #0x108]
043fb900 cbnz     x27, #0x43fb880
043fb904 b        #0x4405ef0
043fb908 mov      w26, w0
043fb90c ldr      x0, [x20, #0x108]
043fb910 cbz      x0, #0x4405ef0
043fb914 ldr      x2, [x21]
043fb918 mov      w1, w26
043fb91c bl       #0x5f32154
043fb920 cbz      x0, #0x4405ef0
043fb924 str      w25, [x0, #0x10]
043fb928 ldr      x0, [x20, #0x108]
043fb92c cbz      x0, #0x4405ef0
043fb930 ldr      x2, [x21]
043fb934 mov      w1, w26
043fb938 bl       #0x5f32154
043fb93c cbz      x0, #0x4405ef0
043fb940 ldr      x2, [x0, #0x18]
043fb944 mov      x0, x19
043fb948 mov      w1, #0xd
043fb94c mov      w3, #-1
043fb950 mov      x4, xzr
043fb954 bl       #0x46bc004
043fb958 ldr      x0, [x20, #0x108]
043fb95c cbz      x0, #0x4405ef0
043fb960 ldr      x2, [x21]
043fb964 mov      w1, w26
043fb968 bl       #0x5f32154
043fb96c cbz      x0, #0x4405ef0
043fb970 ldr      x2, [x0, #0x20]
043fb974 mov      x0, x19
043fb978 mov      w1, #3
043fb97c mov      w3, #-1
043fb980 mov      x4, xzr
043fb984 bl       #0x46bc004
043fb988 ldr      x0, [x20, #0x108]
043fb98c cbz      x0, #0x4405ef0
043fb990 ldr      x2, [x21]
043fb994 mov      w1, w26
043fb998 bl       #0x5f32154
043fb99c mov      x23, x0
043fb9a0 mov      x0, x19
043fb9a4 mov      w1, #-1
043fb9a8 mov      x2, xzr
043fb9ac bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fb9b0 cbz      x23, #0x4405ef0
043fb9b4 strh     w0, [x23, #0x28]
043fb9b8 ldr      x0, [x20, #0x108]
043fb9bc cbz      x0, #0x4405ef0
043fb9c0 ldr      x2, [x21]
043fb9c4 mov      w1, w26
043fb9c8 bl       #0x5f32154
043fb9cc cbz      x0, #0x4405ef0
043fb9d0 mov      x23, x0
043fb9d4 mov      x0, x19
043fb9d8 mov      w1, #-1
043fb9dc mov      x2, xzr
043fb9e0 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fb9e4 strh     w0, [x23, #0x2a]
043fb9e8 ldr      x0, [x20, #0x108]
043fb9ec cbz      x0, #0x4405ef0
043fb9f0 ldr      x2, [x21]
043fb9f4 mov      w1, w26
043fb9f8 bl       #0x5f32154
043fb9fc cbz      x0, #0x4405ef0
043fba00 mov      x23, x0
043fba04 mov      x0, x19
043fba08 mov      w1, #-1
043fba0c mov      x2, xzr
043fba10 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fba14 strb     w0, [x23, #0x2c]
043fba18 ldr      x0, [x20, #0x108]
043fba1c cbz      x0, #0x4405ef0
043fba20 ldr      x2, [x21]
043fba24 mov      w1, w26
043fba28 bl       #0x5f32154
043fba2c cbz      x0, #0x4405ef0
043fba30 mov      x23, x0
043fba34 mov      x0, x19
043fba38 mov      w1, #-1
043fba3c mov      x2, xzr
043fba40 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fba44 sturh    w0, [x23, #0x2d]
043fba48 ldr      x0, [x20, #0x108]
043fba4c cbz      x0, #0x4405ef0
043fba50 ldr      x2, [x21]
043fba54 mov      w1, w26
043fba58 bl       #0x5f32154
043fba5c cbz      x0, #0x4405ef0
043fba60 mov      x23, x0
043fba64 mov      x0, x19
043fba68 mov      w1, #-1
043fba6c mov      x2, xzr
043fba70 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fba74 strb     w0, [x23, #0x2f]
043fba78 ldr      x0, [x20, #0x108]
043fba7c cbz      x0, #0x4405ef0
043fba80 ldr      x2, [x21]
043fba84 mov      w1, w26
043fba88 bl       #0x5f32154
043fba8c mov      x23, x0
043fba90 mov      x0, x19
043fba94 mov      w1, #-1
043fba98 mov      x2, xzr
043fba9c bl       #0x46c27f0 ; MessagePacket.ReadULong
043fbaa0 cbz      x23, #0x4405ef0
043fbaa4 str      x0, [x23, #0x30]
043fbaa8 ldr      x0, [x20, #0x108]
043fbaac cbz      x0, #0x4405ef0
043fbab0 ldr      x2, [x21]
043fbab4 mov      w1, w26
043fbab8 bl       #0x5f32154
043fbabc mov      x23, x0
043fbac0 mov      x0, x19
043fbac4 mov      w1, #-1
043fbac8 mov      x2, xzr
043fbacc bl       #0x46c26e0
043fbad0 cbz      x23, #0x4405ef0
043fbad4 str      w0, [x23, #0x38]
043fbad8 ldr      x0, [x20, #0x108]
043fbadc cbz      x0, #0x4405ef0
043fbae0 ldr      x2, [x21]
043fbae4 mov      w1, w26
043fbae8 bl       #0x5f32154
043fbaec mov      x23, x0
043fbaf0 mov      x0, x19
043fbaf4 mov      w1, #-1
043fbaf8 mov      x2, xzr
043fbafc bl       #0x46c26e0
043fbb00 cbz      x23, #0x4405ef0
043fbb04 str      w0, [x23, #0x3c]
043fbb08 ldr      x0, [x20, #0x108]
043fbb0c cbz      x0, #0x4405ef0
043fbb10 ldr      x2, [x21]
043fbb14 mov      w1, w26
043fbb18 bl       #0x5f32154
043fbb1c mov      x23, x0
043fbb20 mov      x0, x19
043fbb24 mov      w1, #-1
043fbb28 mov      x2, xzr
043fbb2c bl       #0x46c26e0
043fbb30 cbz      x23, #0x4405ef0
043fbb34 str      w0, [x23, #0x40]
043fbb38 ldr      x0, [x20, #0x108]
043fbb3c cbz      x0, #0x4405ef0
043fbb40 ldr      x2, [x21]
043fbb44 mov      w1, w26
043fbb48 bl       #0x5f32154
043fbb4c mov      x23, x0
043fbb50 mov      x0, x19
043fbb54 mov      w1, #-1
043fbb58 mov      x2, xzr
043fbb5c bl       #0x46bbf90 ; MessagePacket.ReadByte
043fbb60 cbz      x23, #0x4405ef0
043fbb64 strb     w0, [x23, #0x44]
043fbb68 mov      x0, x19
043fbb6c mov      w1, #-1
043fbb70 mov      x2, xzr
043fbb74 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fbb78 mov      w28, w0
043fbb7c mov      x0, x19
043fbb80 mov      w1, #-1
043fbb84 mov      x2, xzr
043fbb88 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fbb8c ldr      x8, [x20, #0x108]
043fbb90 cbz      x8, #0x4405ef0
043fbb94 ldr      x2, [x21]
043fbb98 mov      w27, w0
043fbb9c mov      x0, x8
043fbba0 mov      w1, w26
043fbba4 bl       #0x5f32154
043fbba8 mov      x23, x0
043fbbac mov      x0, x19
043fbbb0 mov      w1, #-1
043fbbb4 mov      x2, xzr
043fbbb8 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fbbbc cbz      x23, #0x4405ef0
043fbbc0 strb     w0, [x23, #0x7e]
043fbbc4 ldr      x0, [x20, #0x108]
043fbbc8 cbz      x0, #0x4405ef0
043fbbcc ldr      x2, [x21]
043fbbd0 mov      w1, w26
043fbbd4 bl       #0x5f32154
043fbbd8 mov      x23, x0
043fbbdc mov      x0, x19
043fbbe0 mov      w1, #-1
043fbbe4 mov      x2, xzr
043fbbe8 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fbbec cbz      x23, #0x4405ef0
043fbbf0 strh     w0, [x23, #0x80]
043fbbf4 ldr      x0, [x20, #0x108]
043fbbf8 cbz      x0, #0x4405ef0
043fbbfc ldr      x2, [x21]
043fbc00 mov      w1, w26
043fbc04 bl       #0x5f32154
043fbc08 mov      x23, x0
043fbc0c mov      x0, x19
043fbc10 mov      w1, #-1
043fbc14 mov      x2, xzr
043fbc18 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fbc1c cbz      x23, #0x4405ef0
043fbc20 strb     w0, [x23, #0x82]
043fbc24 ldr      x0, [x20, #0x108]
043fbc28 cbz      x0, #0x4405ef0
043fbc2c ldr      x2, [x21]
043fbc30 mov      w1, w26
043fbc34 bl       #0x5f32154
043fbc38 mov      x23, x0
043fbc3c mov      x0, x19
043fbc40 mov      w1, #-1
043fbc44 mov      x2, xzr
043fbc48 bl       #0x46c26e0
043fbc4c cbz      x23, #0x4405ef0
043fbc50 str      w0, [x23, #0x84]
043fbc54 ldr      x0, [x20, #0x108]
043fbc58 cbz      x0, #0x4405ef0
