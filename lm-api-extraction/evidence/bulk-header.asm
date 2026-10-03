043fa5b8 and      w25, w0, #0xff
043fa5bc sub      w8, w25, #0x16
043fa5c0 cmp      w8, #2
043fa5c4 b.lo     #0x43fa600
043fa5c8 mov      x0, x19
043fa5cc mov      w1, #-1
043fa5d0 cmp      w25, #0x19
043fa5d4 b.eq     #0x43fcc74
043fa5d8 cmp      w25, #0x18
043fa5dc b.ne     #0x43fd068
043fa5e0 mov      x2, xzr
043fa5e4 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fa5e8 mov      w1, w0
043fa5ec mov      x0, x20
043fa5f0 mov      w2, wzr
043fa5f4 mov      x3, xzr
043fa5f8 bl       #0x44d8484
043fa5fc b        #0x4405288
043fa600 mov      x0, x19
043fa604 mov      w1, #-1
043fa608 mov      x2, xzr
043fa60c fmov     d12, #0.50000000
043fa610 bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fa614 and      w8, w0, #0xffff
043fa618 mov      w29, w0
043fa61c cmp      w8, #1, lsl #12
043fa620 b.lo     #0x43fa828
043fa624 ldrb     w8, [x20, #0x28]
043fa628 cbz      w8, #0x43fa678
043fa62c mov      x22, xzr
043fa630 ldr      x8, [x20, #0x30]
043fa634 cbz      x8, #0x4405ef0
043fa638 ldr      w9, [x8, #0x18]
043fa63c cmp      x22, x9
043fa640 b.hs     #0x4405ef4
043fa644 add      x8, x8, x22, lsl #1
043fa648 mov      x0, x20
043fa64c mov      x2, xzr
043fa650 ldrh     w1, [x8, #0x20]
043fa654 bl       #0x44e7c78
043fa658 ldrb     w8, [x20, #0x28]
043fa65c add      x22, x22, #1
043fa660 cmp      x22, x8
043fa664 b.lo     #0x43fa630
043fa668 and      w8, w29, #0xffff
043fa66c strb     wzr, [x20, #0x28]
043fa670 cmp      w8, #1, lsl #12
043fa674 b.lo     #0x43fa828
043fa678 ubfx     w22, w29, #0xc, #4
043fa67c mov      x23, xzr
043fa680 ldrb     w8, [x20, #0x28]
043fa684 ldr      x24, [x20, #0x30]
043fa688 mov      x0, x19
043fa68c mov      w1, #-1
043fa690 mov      x2, xzr
043fa694 add      w8, w8, #1
043fa698 strb     w8, [x20, #0x28]
043fa69c bl       #0x46bbe78 ; MessagePacket.ReadUShort
043fa6a0 strh     w0, [sp, #0x10c]
043fa6a4 cbz      x24, #0x4405ef0
043fa6a8 ldr      w8, [x24, #0x18]
043fa6ac cmp      x23, x8
043fa6b0 b.hs     #0x4405ef4
043fa6b4 add      x8, x24, x23, lsl #1
043fa6b8 mov      w1, #-1
043fa6bc mov      x2, xzr
043fa6c0 strh     w0, [x8, #0x20]
043fa6c4 mov      x0, x19
043fa6c8 ldr      x24, [x20, #0x38]
043fa6cc bl       #0x46c27f0 ; MessagePacket.ReadULong
043fa6d0 cbz      x24, #0x4405ef0
043fa6d4 ldr      w8, [x24, #0x18]
043fa6d8 cmp      x23, x8
043fa6dc b.hs     #0x4405ef4
043fa6e0 add      x8, x24, x23, lsl #3
043fa6e4 str      x0, [x8, #0x20]
043fa6e8 ldr      x8, [x20, #0x38]
043fa6ec cbz      x8, #0x4405ef0
043fa6f0 ldr      w9, [x8, #0x18]
043fa6f4 cmp      x23, x9
043fa6f8 b.hs     #0x4405ef4
043fa6fc add      x8, x8, x23, lsl #3
043fa700 ldr      x9, [x8, #0x20]
043fa704 cbnz     x9, #0x43fa710
043fa708 mov      w9, #1
043fa70c str      x9, [x8, #0x20]
043fa710 add      x23, x23, #1
043fa714 cmp      x22, x23
043fa718 b.ne     #0x43fa680
043fa71c and      w8, w29, #0xffff
043fa720 cmp      w8, #1, lsl #12
043fa724 b.lo     #0x43fa828
043fa728 ldr      x2, [x20, #0x30]
043fa72c ldrb     w1, [x20, #0x28]
043fa730 mov      x0, x20
043fa734 mov      x3, xzr
043fa738 bl       #0x44e67bc
043fa73c ldrb     w8, [x20, #0x28]
043fa740 cbz      w8, #0x43fa7e0
043fa744 ldr      x8, [x20, #0x30]
043fa748 mov      x22, xzr
043fa74c cbz      x8, #0x4405ef0
043fa750 ldr      w9, [x8, #0x18]
043fa754 cmp      w22, w9
043fa758 b.hs     #0x4405ef4
043fa75c add      x8, x8, x22, lsl #1
043fa760 mov      x0, x20
043fa764 mov      w2, #1
043fa768 mov      x3, xzr
043fa76c ldrh     w1, [x8, #0x20]
043fa770 bl       #0x44d8484
043fa774 ldr      x8, [x20, #0x30]
043fa778 cbz      x8, #0x4405ef0
043fa77c ldr      w9, [x8, #0x18]
043fa780 cmp      w22, w9
043fa784 b.hs     #0x4405ef4
043fa788 ldr      x9, [x20, #0x60]
043fa78c cbz      x9, #0x4405ef0
043fa790 ldr      x10, [x20, #0x38]
043fa794 cbz      x10, #0x4405ef0
043fa798 ldr      w11, [x10, #0x18]
043fa79c cmp      w22, w11
043fa7a0 b.hs     #0x4405ef4
043fa7a4 add      x11, x8, x22, lsl #1
043fa7a8 ldr      w12, [x9, #0x18]
043fa7ac ldrh     w11, [x11, #0x20]
043fa7b0 cmp      w11, w12
043fa7b4 b.hs     #0x4405ef4
043fa7b8 ubfiz    x12, x11, #3, #0x20
043fa7bc add      x10, x10, x22, lsl #3
043fa7c0 add      x22, x22, #1
043fa7c4 add      x11, x12, w11, uxtw
043fa7c8 ldr      x10, [x10, #0x20]
043fa7cc add      x9, x9, x11
043fa7d0 str      x10, [x9, #0x20]
043fa7d4 ldrb     w9, [x20, #0x28]
043fa7d8 cmp      w22, w9
043fa7dc b.lo     #0x43fa74c
043fa7e0 mov      x0, x19
043fa7e4 mov      w1, #-1
043fa7e8 mov      x2, xzr
043fa7ec bl       #0x46bbf90 ; MessagePacket.ReadByte
043fa7f0 add      w8, w0, #0x7f
043fa7f4 and      w8, w8, #0xff
043fa7f8 cmp      w8, #0xa8
043fa7fc b.lo     #0x43fa804
043fa800 strb     w0, [x20, #0x2f8]
043fa804 mov      x0, x19
043fa808 mov      w1, #-1
043fa80c mov      x2, xzr
043fa810 bl       #0x46bbf90 ; MessagePacket.ReadByte
043fa814 add      w8, w0, #0x7f
043fa818 and      w8, w8, #0xff
043fa81c cmp      w8, #0xb1
043fa820 b.lo     #0x43fa828
043fa824 strb     w0, [x20, #0x2f9]
043fa828 ubfx     w8, w29, #6, #6
043fa82c str      w25, [sp, #0x60]
043fa830 str      w8, [sp, #0x84]
043fa834 cbz      w8, #0x43fb818
043fa838 ldrb     w8, [x20, #0x2f8]
043fa83c mov      w25, wzr
043fa840 sub      w8, w8, #4
043fa844 and      w8, w8, #0xff
043fa848 sub      w10, w8, #0x2c
043fa84c sub      w9, w8, #0x19
043fa850 str      w8, [sp, #0x78]
043fa854 stp      w10, w9, [sp, #0x38]
043fa858 add      w10, w8, #1
043fa85c sub      w9, w8, #0x25
043fa860 sub      w8, w8, #0x24
043fa864 str      w9, [sp, #0x5c]
043fa868 stp      w8, w10, [sp, #0x64]
