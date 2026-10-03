033e5124 str      x30, [sp, #-0x10]!
033e5128 tbnz     w1, #0x1f, #0x33e5144
033e512c cbz      x0, #0x33e5180
033e5130 ldr      w8, [x0, #0x18]
033e5134 add      w9, w1, #2
033e5138 cmp      w9, w8
033e513c b.gt     #0x33e514c
033e5140 b        #0x33e5150
033e5144 cbz      x0, #0x33e5180
033e5148 ldr      w8, [x0, #0x18]
033e514c sub      w1, w8, #2
033e5150 cmp      w1, w8
033e5154 b.hs     #0x33e517c
033e5158 add      w9, w1, #1
033e515c cmp      w9, w8
033e5160 b.hs     #0x33e517c
033e5164 add      x8, x0, #0x20
033e5168 ldrb     w10, [x8, w1, sxtw]
033e516c ldrb     w8, [x8, w9, sxtw]
033e5170 orr      w0, w10, w8, lsl #8
033e5174 ldr      x30, [sp], #0x10
033e5178 ret      
033e517c bl       #0x30df918
033e5180 bl       #0x30df910
