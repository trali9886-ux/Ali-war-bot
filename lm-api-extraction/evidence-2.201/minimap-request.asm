044e655c stp      x30, x21, [sp, #-0x20]!
044e6560 stp      x20, x19, [sp, #0x10]
044e6564 adrp     x21, #0x8620000
044e6568 mov      w19, w1
044e656c mov      x20, x0
044e6570 ldrb     w8, [x21, #0x8b3]
044e6574 tbnz     w8, #0, #0x44e658c
044e6578 adrp     x0, #0x81e3000
044e657c ldr      x0, [x0, #0x378]
044e6580 bl       #0x30df668
044e6584 mov      w8, #1
044e6588 strb     w8, [x21, #0x8b3]
044e658c ldrh     w8, [x20, #0x1ee]
044e6590 ldrh     w9, [x20, #0x178]
044e6594 cmp      w8, w9
044e6598 b.ne     #0x44e65c0
044e659c adrp     x8, #0x81e3000
044e65a0 ldr      x8, [x8, #0x378]
044e65a4 ldr      x0, [x8]
044e65a8 bl       #0x30df900
044e65ac mov      w1, #0x400
044e65b0 mov      x2, xzr
044e65b4 mov      x20, x0
044e65b8 bl       #0x46bb21c ; MessagePacket..ctor
044e65bc b        #0x44e65cc
044e65c0 mov      x0, xzr
044e65c4 bl       #0x46bb2dc
044e65c8 mov      x20, x0
044e65cc cbz      x20, #0x44e6610
044e65d0 ldr      x8, [x20]
044e65d4 mov      w9, #0x8c1
044e65d8 mov      x0, x20
044e65dc strh     w9, [x20, #0x30]
044e65e0 ldp      x10, x1, [x8, #0x178]
044e65e4 blr      x10
044e65e8 mov      x0, x20
044e65ec mov      w1, w19
044e65f0 mov      x2, xzr
044e65f4 bl       #0x46bb52c ; MessagePacket.Add
044e65f8 mov      x0, x20
044e65fc ldp      x20, x19, [sp, #0x10]
044e6600 mov      w1, wzr
044e6604 mov      x2, xzr
044e6608 ldp      x30, x21, [sp], #0x20
044e660c b        #0x46bb598 ; MessagePacket.Send
044e6610 bl       #0x30df910
