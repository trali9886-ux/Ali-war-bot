046bb598 str      x30, [sp, #-0x40]!
046bb59c stp      x24, x23, [sp, #0x10]
046bb5a0 stp      x22, x21, [sp, #0x20]
046bb5a4 stp      x20, x19, [sp, #0x30]
046bb5a8 adrp     x21, #0x8621000
046bb5ac adrp     x23, #0x81e3000
046bb5b0 mov      w20, w1
046bb5b4 ldrb     w8, [x21, #0x1a3]
046bb5b8 ldr      x23, [x23, #0x370]
046bb5bc mov      x19, x0
046bb5c0 tbnz     w8, #0, #0x46bb614
046bb5c4 adrp     x0, #0x8207000
046bb5c8 ldr      x0, [x0, #0x978]
046bb5cc bl       #0x30df668
046bb5d0 adrp     x0, #0x8207000
046bb5d4 ldr      x0, [x0, #0x968]
046bb5d8 bl       #0x30df668
046bb5dc adrp     x0, #0x8207000
046bb5e0 ldr      x0, [x0, #0x988]
046bb5e4 bl       #0x30df668
046bb5e8 adrp     x0, #0x81e3000
046bb5ec ldr      x0, [x0, #0x770]
046bb5f0 bl       #0x30df668
046bb5f4 adrp     x0, #0x81e3000
046bb5f8 ldr      x0, [x0, #0x370]
046bb5fc bl       #0x30df668
046bb600 adrp     x0, #0x8207000
046bb604 ldr      x0, [x0, #0x990]
046bb608 bl       #0x30df668
046bb60c mov      w8, #1
046bb610 strb     w8, [x21, #0x1a3]
046bb614 ldr      x0, [x23]
046bb618 ldrb     w9, [x19, #0x1c]
046bb61c ldr      w8, [x0, #0xe4]
046bb620 cbz      w9, #0x46bb744
046bb624 cbnz     w8, #0x46bb62c
046bb628 bl       #0x30df7e4
046bb62c bl       #0x46c2c10
046bb630 cbz      x0, #0x46bb8d0
046bb634 bl       #0x46c2cd4
046bb638 tbnz     w0, #0, #0x46bb640
046bb63c tbz      w20, #0, #0x46bb758
046bb640 ldr      x0, [x19, #0x28]
046bb644 cbz      x0, #0x46bb8d0
046bb648 adrp     x23, #0x8207000
046bb64c mov      w1, wzr
046bb650 ldr      x23, [x23, #0x968]
046bb654 ldr      w20, [x19, #0x18]
046bb658 ldr      x21, [x0, #0x20]
046bb65c ldr      x2, [x23]
046bb660 bl       #0x6250920
046bb664 adrp     x8, #0x81e3000
046bb668 mov      w22, w0
046bb66c ldr      x8, [x8, #0x770]
046bb670 ldr      x8, [x8]
046bb674 ldr      w9, [x8, #0xe4]
046bb678 cbnz     w9, #0x46bb684
046bb67c mov      x0, x8
046bb680 bl       #0x30df7e4
046bb684 mov      w0, w20
046bb688 mov      x1, x21
046bb68c mov      w2, w22
046bb690 mov      x3, xzr
046bb694 bl       #0x33e53d8
046bb698 ldr      x0, [x19, #0x28]
046bb69c cbz      x0, #0x46bb8d0
046bb6a0 ldr      x2, [x23]
046bb6a4 ldr      x20, [x0, #0x20]
046bb6a8 mov      w1, #2
046bb6ac ldrh     w21, [x19, #0x30]
046bb6b0 bl       #0x6250920
046bb6b4 mov      w2, w0
046bb6b8 mov      w0, w21
046bb6bc mov      x1, x20
046bb6c0 mov      x3, xzr
046bb6c4 bl       #0x33e53d8
046bb6c8 ldr      x0, [x19, #0x28]
046bb6cc cbz      x0, #0x46bb8d0
046bb6d0 ldr      x2, [x23]
046bb6d4 ldr      x20, [x0, #0x20]
046bb6d8 mov      w1, #4
046bb6dc bl       #0x6250920
046bb6e0 adrp     x23, #0x8207000
046bb6e4 mov      w22, w0
046bb6e8 ldr      x23, [x23, #0x990]
046bb6ec ldr      w24, [x19, #0x18]
046bb6f0 ldr      w21, [x19, #0x24]
046bb6f4 ldr      x8, [x23]
046bb6f8 ldr      w9, [x8, #0xe4]
046bb6fc cbnz     w9, #0x46bb708
046bb700 mov      x0, x8
046bb704 bl       #0x30df7e4
046bb708 sub      w2, w24, #4
046bb70c mov      x0, x20
046bb710 mov      w1, w22
046bb714 mov      w3, w21
046bb718 bl       #0x46c2d34 ; NetworkPeeper.Cipher
046bb71c ldr      x8, [x23]
046bb720 ldr      x8, [x8, #0xb8]
046bb724 ldr      x0, [x8, #0x10]
046bb728 cbz      x0, #0x46bb8d0
046bb72c ldr      x8, [x0]
046bb730 mov      x1, x19
046bb734 ldr      x9, [x8, #0x238]
046bb738 ldr      x2, [x8, #0x240]
046bb73c blr      x9
046bb740 b        #0x46bb8b8
046bb744 cbnz     w8, #0x46bb74c
046bb748 bl       #0x30df7e4
046bb74c bl       #0x46c2314
046bb750 tbnz     w0, #0, #0x46bb7dc
046bb754 tbnz     w20, #0, #0x46bb7dc
046bb758 ldr      x0, [x19, #0x28]
046bb75c cbz      x0, #0x46bb8d0
046bb760 ldrb     w8, [x0, #0x18]
046bb764 cbnz     w8, #0x46bb7d4
046bb768 adrp     x8, #0x8207000
046bb76c ldr      x8, [x8, #0x988]
046bb770 ldr      x1, [x8]
046bb774 bl       #0x62507c4
046bb778 ldr      x8, [x23]
046bb77c mov      w20, w0
046bb780 ldr      w9, [x8, #0xe4]
046bb784 cbnz     w9, #0x46bb794
046bb788 mov      x0, x8
046bb78c bl       #0x30df7e4
046bb790 ldr      x8, [x23]
046bb794 ldr      x9, [x8, #0xb8]
046bb798 ldr      w10, [x9, #0xb8]
046bb79c cmp      w20, w10
046bb7a0 b.ne     #0x46bb7d4
046bb7a4 ldr      w10, [x8, #0xe4]
046bb7a8 cbnz     w10, #0x46bb7c0
046bb7ac mov      x0, x8
046bb7b0 bl       #0x30df7e4
046bb7b4 ldr      x8, [x23]
046bb7b8 ldr      x9, [x8, #0xb8]
046bb7bc ldr      w20, [x9, #0xb8]
046bb7c0 ldr      w8, [x19, #0x24]
046bb7c4 mov      w0, wzr
046bb7c8 sub      w8, w20, w8
046bb7cc str      w8, [x9, #0xb8]
046bb7d0 b        #0x46bb8bc
046bb7d4 mov      w0, wzr
046bb7d8 b        #0x46bb8bc
046bb7dc ldr      x0, [x19, #0x28]
046bb7e0 cbz      x0, #0x46bb8d0
046bb7e4 adrp     x24, #0x8207000
046bb7e8 mov      w1, wzr
046bb7ec ldr      x24, [x24, #0x968]
046bb7f0 ldr      w20, [x19, #0x18]
046bb7f4 ldr      x21, [x0, #0x20]
046bb7f8 ldr      x2, [x24]
046bb7fc bl       #0x6250920
046bb800 adrp     x8, #0x81e3000
046bb804 mov      w22, w0
046bb808 ldr      x8, [x8, #0x770]
046bb80c ldr      x8, [x8]
046bb810 ldr      w9, [x8, #0xe4]
046bb814 cbnz     w9, #0x46bb820
046bb818 mov      x0, x8
046bb81c bl       #0x30df7e4
046bb820 mov      w0, w20
046bb824 mov      x1, x21
046bb828 mov      w2, w22
046bb82c mov      x3, xzr
046bb830 bl       #0x33e53d8
046bb834 ldr      x0, [x19, #0x28]
046bb838 cbz      x0, #0x46bb8d0
046bb83c ldr      x2, [x24]
046bb840 ldr      x20, [x0, #0x20]
046bb844 mov      w1, #2
046bb848 ldrh     w21, [x19, #0x30]
046bb84c bl       #0x6250920
046bb850 mov      w2, w0
046bb854 mov      w0, w21
046bb858 mov      x1, x20
046bb85c mov      x3, xzr
046bb860 bl       #0x33e53d8
046bb864 ldr      x0, [x19, #0x28]
046bb868 cbz      x0, #0x46bb8d0
046bb86c ldr      x2, [x24]
046bb870 ldr      x20, [x0, #0x20]
046bb874 mov      w1, #4
046bb878 bl       #0x6250920
046bb87c ldr      x8, [x23]
046bb880 ldr      w23, [x19, #0x18]
046bb884 mov      w22, w0
046bb888 ldr      w21, [x19, #0x24]
046bb88c ldr      w9, [x8, #0xe4]
046bb890 cbnz     w9, #0x46bb89c
046bb894 mov      x0, x8
046bb898 bl       #0x30df7e4
046bb89c sub      w2, w23, #4
046bb8a0 mov      x0, x20
046bb8a4 mov      w1, w22
046bb8a8 mov      w3, w21
046bb8ac bl       #0x46c3058 ; NetworkManager.Cipher
046bb8b0 mov      x0, x19
046bb8b4 bl       #0x46c3368 ; NetworkManager.Send
046bb8b8 mov      w0, #1
046bb8bc ldp      x20, x19, [sp, #0x30]
046bb8c0 ldp      x22, x21, [sp, #0x20]
046bb8c4 ldp      x24, x23, [sp, #0x10]
046bb8c8 ldr      x30, [sp], #0x40
046bb8cc ret      
046bb8d0 bl       #0x30df910
046bb8d4 sub      sp, sp, #0x70
