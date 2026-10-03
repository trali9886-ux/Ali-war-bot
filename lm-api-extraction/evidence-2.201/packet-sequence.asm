046c2284 stp      x30, x21, [sp, #-0x20]!
046c2288 stp      x20, x19, [sp, #0x10]
046c228c adrp     x20, #0x8621000
046c2290 adrp     x21, #0x81e3000
046c2294 mov      x19, x0
046c2298 ldrb     w8, [x20, #0x193]
046c229c ldr      x21, [x21, #0x370]
046c22a0 tbnz     w8, #0, #0x46c22c4
046c22a4 adrp     x0, #0x81e3000
046c22a8 ldr      x0, [x0, #0x378]
046c22ac bl       #0x30df668
046c22b0 adrp     x0, #0x81e3000
046c22b4 ldr      x0, [x0, #0x370]
046c22b8 bl       #0x30df668
046c22bc mov      w8, #1
046c22c0 strb     w8, [x20, #0x193]
046c22c4 ldr      x0, [x21]
046c22c8 ldr      w8, [x0, #0xe4]
046c22cc cbnz     w8, #0x46c22d4
046c22d0 bl       #0x30df7e4
046c22d4 bl       #0x46c2314
046c22d8 tbz      w0, #0, #0x46c2308
046c22dc adrp     x8, #0x81e3000
046c22e0 mov      x0, x19
046c22e4 ldr      x8, [x8, #0x378]
046c22e8 ldp      x20, x19, [sp, #0x10]
046c22ec ldr      x8, [x8]
046c22f0 ldr      x8, [x8, #0xb8]
046c22f4 ldr      w9, [x8]
046c22f8 add      w1, w9, #1
046c22fc str      w1, [x8]
046c2300 ldp      x30, x21, [sp], #0x20
046c2304 b        #0x46c1fa4 ; MessagePacket.Add
046c2308 ldp      x20, x19, [sp, #0x10]
046c230c ldp      x30, x21, [sp], #0x20
046c2310 ret      
