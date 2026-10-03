044de8dc str      x30, [sp, #-0x10]!
044de8e0 ldrb     w9, [x0, #0x19]
044de8e4 and      w8, w1, #0xff
044de8e8 cbz      w9, #0x44de8fc
044de8ec ldrb     w10, [x0, #0x18]
044de8f0 lsr      w10, w10, w9
044de8f4 cmp      w10, #1
044de8f8 b.ne     #0x44de974
044de8fc ldr      x13, [x0, #0x20]
044de900 cbz      x13, #0x44de9d4
044de904 ldr      x11, [x0, #0x48]
044de908 ldr      w12, [x13, #0x18]
044de90c mov      x10, xzr
044de910 add      x13, x13, #0x20
044de914 add      x15, x2, #0x20
044de918 add      x14, x11, #0x20
044de91c cmp      x12, x10
044de920 b.eq     #0x44de9d0
044de924 cbz      x11, #0x44de9d4
044de928 ldr      w16, [x11, #0x18]
044de92c cmp      w10, w16
044de930 b.hs     #0x44de9d0
044de934 ldrh     w16, [x13, x10, lsl #1]
044de938 strh     w16, [x14, x10, lsl #1]
044de93c cbz      x2, #0x44de9d4
044de940 ldr      w16, [x2, #0x18]
044de944 cmp      w10, w16
044de948 b.hs     #0x44de9d0
044de94c ldrh     w16, [x15, x10, lsl #1]
044de950 strh     w16, [x13, x10, lsl #1]
044de954 add      x10, x10, #1
044de958 cmp      x10, #4
044de95c b.ne     #0x44de91c
044de960 strb     w9, [x0, #0x40]
044de964 and      w1, w3, #1
044de968 strb     w8, [x0, #0x19]
044de96c ldr      x30, [sp], #0x10
044de970 b        #0x44de9d8 ; MapManager.sendRequestMapdataMsg
044de974 sub      w9, w8, #1
044de978 cmp      w9, #3
044de97c b.hi     #0x44de9c8
044de980 cbz      x2, #0x44de9d4
044de984 ldr      x10, [x0, #0x58]
044de988 ldr      w11, [x2, #0x18]
044de98c mov      x9, xzr
044de990 add      x12, x2, #0x20
044de994 add      x13, x10, #0x20
044de998 cmp      x11, x9
044de99c b.eq     #0x44de9d0
044de9a0 cbz      x10, #0x44de9d4
044de9a4 ldr      w14, [x10, #0x18]
044de9a8 cmp      w9, w14
044de9ac b.hs     #0x44de9d0
044de9b0 ldrh     w14, [x12, x9, lsl #1]
044de9b4 strh     w14, [x13, x9, lsl #1]
044de9b8 add      x9, x9, #1
044de9bc cmp      x9, #4
044de9c0 b.ne     #0x44de998
044de9c4 strb     w8, [x0, #0x50]
044de9c8 ldr      x30, [sp], #0x10
044de9cc ret      
044de9d0 bl       #0x30df918
044de9d4 bl       #0x30df910
044de9d8 str      x30, [sp, #-0x30]!
044de9dc stp      x22, x21, [sp, #0x10]
044de9e0 stp      x20, x19, [sp, #0x20]
044de9e4 adrp     x21, #0x8620000
044de9e8 mov      w20, w1
044de9ec mov      x19, x0
044de9f0 ldrb     w8, [x21, #0x885]
044de9f4 tbnz     w8, #0, #0x44dea18
044de9f8 adrp     x0, #0x81e3000
044de9fc ldr      x0, [x0, #0x360]
044dea00 bl       #0x30df668
044dea04 adrp     x0, #0x81e3000
044dea08 ldr      x0, [x0, #0x378]
044dea0c bl       #0x30df668
044dea10 mov      w8, #1
044dea14 strb     w8, [x21, #0x885]
044dea18 ldrb     w8, [x19, #0x205]
044dea1c cbnz     w8, #0x44debf0
044dea20 ldr      x8, [x19, #0x20]
044dea24 cbz      x8, #0x44dec00
044dea28 ldr      w9, [x8, #0x18]
044dea2c cbz      w9, #0x44dec04
044dea30 adrp     x21, #0x81e3000
044dea34 ldrh     w8, [x8, #0x20]
044dea38 ldr      x21, [x21, #0x360]
044dea3c cmp      w8, #4, lsl #12
044dea40 ldr      x0, [x21]
044dea44 cset     w8, eq
044dea48 lsl      w8, w8, #1
044dea4c ldr      w9, [x0, #0xe4]
044dea50 strb     w8, [x19, #0x18]
044dea54 cbnz     w9, #0x44dea60
044dea58 bl       #0x30df7e4
044dea5c ldr      x0, [x21]
044dea60 ldr      x8, [x0, #0xb8]
044dea64 ldr      x8, [x8, #0x58]
044dea68 cbz      x8, #0x44dec00
044dea6c ldr      w9, [x8, #0x18]
044dea70 cbz      w9, #0x44dec04
044dea74 mov      w9, #0x64
044dea78 mov      w0, #1
044dea7c mov      w1, wzr
044dea80 strb     w9, [x8, #0x20]
044dea84 mov      x3, xzr
044dea88 ldr      x8, [x21]
044dea8c ldr      x8, [x8, #0xb8]
044dea90 ldr      x2, [x8, #0x58]
044dea94 bl       #0x34a910c
044dea98 ldrh     w8, [x19, #0x1ee]
044dea9c ldrh     w9, [x19, #0x178]
044deaa0 cmp      w8, w9
044deaa4 b.eq     #0x44deab4
044deaa8 ldrh     w9, [x19, #0x1f4]
044deaac cmp      w8, w9
044deab0 b.ne     #0x44dead8
044deab4 adrp     x8, #0x81e3000
044deab8 ldr      x8, [x8, #0x378]
044deabc ldr      x0, [x8]
044deac0 bl       #0x30df900
044deac4 mov      w1, #0x400
044deac8 mov      x2, xzr
044deacc mov      x21, x0
044dead0 bl       #0x46bb21c ; MessagePacket..ctor
044dead4 b        #0x44deae4
044dead8 mov      x0, xzr
044deadc bl       #0x46bb2dc
044deae0 mov      x21, x0
044deae4 mov      x0, x19
044deae8 bl       #0x44dec90
044deaec cbz      x21, #0x44dec00
044deaf0 ldr      x8, [x21]
044deaf4 tst      w0, #1
044deaf8 mov      w9, #0x899
044deafc mov      w10, #0x8b9
044deb00 mov      x0, x21
044deb04 csel     w9, w10, w9, ne
044deb08 ldp      x10, x1, [x8, #0x178]
044deb0c strh     w9, [x21, #0x30]
044deb10 blr      x10
044deb14 ldrb     w1, [x19, #0x19]
044deb18 mov      x0, x21
044deb1c mov      x2, xzr
044deb20 bl       #0x46bb52c ; MessagePacket.Add
044deb24 mov      x22, xzr
044deb28 ldr      x8, [x19, #0x20]
044deb2c cbz      x8, #0x44dec00
044deb30 ldr      w9, [x8, #0x18]
044deb34 cmp      x22, x9
044deb38 b.hs     #0x44dec04
044deb3c add      x8, x8, x22, lsl #1
044deb40 mov      x0, x21
044deb44 mov      x2, xzr
044deb48 ldrh     w1, [x8, #0x20]
044deb4c bl       #0x46bb3a8 ; MessagePacket.Add
044deb50 add      x22, x22, #1
044deb54 cmp      x22, #4
044deb58 b.ne     #0x44deb28
044deb5c tbz      w20, #0, #0x44deb80
044deb60 mov      w20, #4
044deb64 mov      x0, x21
044deb68 mov      x1, xzr
044deb6c mov      x2, xzr
044deb70 bl       #0x46c23f4 ; MessagePacket.Add
044deb74 subs     w20, w20, #1
044deb78 b.ne     #0x44deb64
044deb7c b        #0x44debd8
044deb80 mov      x20, xzr
044deb84 ldr      x8, [x19, #0x20]
044deb88 cbz      x8, #0x44dec00
044deb8c ldr      w9, [x8, #0x18]
044deb90 cmp      x20, x9
044deb94 b.hs     #0x44dec04
044deb98 ldr      x9, [x19, #0x60]
044deb9c cbz      x9, #0x44dec00
044deba0 add      x8, x8, x20, lsl #1
044deba4 ldr      w10, [x9, #0x18]
044deba8 ldrh     w8, [x8, #0x20]
044debac cmp      w8, w10
044debb0 b.hs     #0x44dec04
044debb4 add      x8, x8, x8, lsl #3
044debb8 mov      x0, x21
044debbc mov      x2, xzr
044debc0 add      x8, x9, x8
044debc4 ldr      x1, [x8, #0x20]
044debc8 bl       #0x46c23f4 ; MessagePacket.Add
044debcc add      x20, x20, #1
044debd0 cmp      x20, #4
044debd4 b.ne     #0x44deb84
044debd8 mov      x0, x21
044debdc mov      w1, wzr
044debe0 mov      x2, xzr
044debe4 bl       #0x46bb598 ; MessagePacket.Send
044debe8 mov      w8, #0x3fc00000
044debec str      w8, [x19, #0x1e4]
044debf0 ldp      x20, x19, [sp, #0x20]
044debf4 ldp      x22, x21, [sp, #0x10]
044debf8 ldr      x30, [sp], #0x30
044debfc ret      
044dec00 bl       #0x30df910
