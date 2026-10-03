046c3058 sub      sp, sp, #0x70
046c305c str      x30, [sp, #0x30]
046c3060 stp      x24, x23, [sp, #0x40]
046c3064 stp      x22, x21, [sp, #0x50]
046c3068 stp      x20, x19, [sp, #0x60]
046c306c adrp     x24, #0x8621000
046c3070 adrp     x23, #0x81e3000
046c3074 mov      w22, w3
046c3078 ldrb     w8, [x24, #0x1cd]
046c307c ldr      x23, [x23, #0x370]
046c3080 mov      w21, w2
046c3084 mov      w19, w1
046c3088 mov      x20, x0
046c308c tbnz     w8, #0, #0x46c30c8
046c3090 adrp     x0, #0x8206000
046c3094 ldr      x0, [x0, #0xe90]
046c3098 bl       #0x30df668
046c309c adrp     x0, #0x81e2000
046c30a0 ldr      x0, [x0, #0x878]
046c30a4 bl       #0x30df668
046c30a8 adrp     x0, #0x81e9000
046c30ac ldr      x0, [x0, #0x670]
046c30b0 bl       #0x30df668
046c30b4 adrp     x0, #0x81e3000
046c30b8 ldr      x0, [x0, #0x370]
046c30bc bl       #0x30df668
046c30c0 mov      w8, #1
046c30c4 strb     w8, [x24, #0x1cd]
046c30c8 ldr      x0, [x23]
046c30cc str      xzr, [sp, #0x38]
046c30d0 str      xzr, [sp, #0x28]
046c30d4 ldr      w8, [x0, #0xe4]
046c30d8 cbnz     w8, #0x46c30e4
046c30dc bl       #0x30df7e4
046c30e0 ldr      x0, [x23]
046c30e4 cmp      w22, #1
046c30e8 b.lt     #0x46c32ac
046c30ec ldr      x8, [x0, #0xb8]
046c30f0 ldrb     w8, [x8, #0x70]
046c30f4 cmp      w8, #0xe
046c30f8 b.lo     #0x46c32ac
046c30fc adrp     x8, #0x81e9000
046c3100 ldr      x8, [x8, #0x670]
046c3104 ldr      x0, [x8]
046c3108 bl       #0x30df900
046c310c and      w3, w21, #0xfffffff8
046c3110 mov      x1, x20
046c3114 mov      w2, w19
046c3118 mov      w4, wzr
046c311c mov      w5, wzr
046c3120 mov      x6, xzr
046c3124 mov      x22, x0
046c3128 bl       #0x72b35a4
046c312c ldr      x0, [x23]
046c3130 add      x9, sp, #0x38
046c3134 str      x22, [sp, #0x38]
046c3138 stp      xzr, x9, [sp, #0x18]
046c313c ldr      w8, [x0, #0xe4]
046c3140 cbnz     w8, #0x46c314c
046c3144 bl       #0x30df7e4
046c3148 ldr      x0, [x23]
046c314c adrp     x9, #0x8206000
046c3150 ldr      x8, [x0, #0xb8]
046c3154 ldr      x9, [x9, #0xe90]
046c3158 ldr      x23, [x8, #0x10]
046c315c ldr      x0, [x9]
046c3160 bl       #0x30df900
046c3164 mov      x1, x22
046c3168 mov      x2, x23
046c316c mov      w3, wzr
046c3170 mov      x4, xzr
046c3174 mov      x21, x0
046c3178 bl       #0x71a4d30
046c317c ldr      x0, [sp, #0x38]
046c3180 add      x8, sp, #0x28
046c3184 str      x21, [sp, #0x28]
046c3188 stp      xzr, x8, [sp, #8]
046c318c cbz      x0, #0x46c32c8
046c3190 ldr      x8, [x0]
046c3194 ldr      x1, [x8, #0x3b0]
046c3198 ldr      x9, [x8, #0x3a8]
046c319c blr      x9
046c31a0 cbz      x21, #0x46c32cc
046c31a4 ldr      x8, [x21]
046c31a8 mov      w3, w0
046c31ac ldr      x9, [x8, #0x338]
046c31b0 ldr      x4, [x8, #0x340]
046c31b4 mov      x0, x21
046c31b8 mov      x1, x20
046c31bc mov      w2, w19
046c31c0 blr      x9
046c31c4 mov      x19, xzr
046c31c8 add      x8, sp, #0x28
046c31cc ldr      x20, [x8]
046c31d0 cbz      x20, #0x46c3234
046c31d4 adrp     x10, #0x81e2000
046c31d8 ldr      x8, [x20]
046c31dc ldr      x10, [x10, #0x878]
046c31e0 ldrh     w9, [x8, #0x12e]
046c31e4 ldr      x1, [x10]
046c31e8 cbz      x9, #0x46c320c
046c31ec ldr      x10, [x8, #0xb0]
046c31f0 add      x10, x10, #8
046c31f4 ldur     x11, [x10, #-8]
046c31f8 cmp      x11, x1
046c31fc b.eq     #0x46c321c
046c3200 subs     x9, x9, #1
046c3204 add      x10, x10, #0x10
046c3208 b.ne     #0x46c31f4
046c320c mov      x0, x20
046c3210 mov      w2, wzr
046c3214 bl       #0x3118cbc
046c3218 b        #0x46c3228
046c321c ldrsw    x9, [x10]
046c3220 add      x8, x8, x9, lsl #4
046c3224 add      x0, x8, #0x138
046c3228 ldp      x8, x1, [x0]
046c322c mov      x0, x20
046c3230 blr      x8
046c3234 cbnz     x19, #0x46c32d0
046c3238 ldr      x8, [sp, #0x20]
046c323c ldr      x19, [x8]
046c3240 cbz      x19, #0x46c32a4
046c3244 adrp     x10, #0x81e2000
046c3248 ldr      x8, [x19]
046c324c ldr      x10, [x10, #0x878]
046c3250 ldrh     w9, [x8, #0x12e]
046c3254 ldr      x1, [x10]
046c3258 cbz      x9, #0x46c327c
046c325c ldr      x10, [x8, #0xb0]
046c3260 add      x10, x10, #8
046c3264 ldur     x11, [x10, #-8]
046c3268 cmp      x11, x1
046c326c b.eq     #0x46c328c
046c3270 subs     x9, x9, #1
046c3274 add      x10, x10, #0x10
046c3278 b.ne     #0x46c3264
046c327c mov      x0, x19
046c3280 mov      w2, wzr
046c3284 bl       #0x3118cbc
046c3288 b        #0x46c3298
046c328c ldrsw    x9, [x10]
046c3290 add      x8, x8, x9, lsl #4
046c3294 add      x0, x8, #0x138
046c3298 ldp      x8, x1, [x0]
046c329c mov      x0, x19
046c32a0 blr      x8
046c32a4 ldr      x0, [sp, #0x18]
046c32a8 cbnz     x0, #0x46c32c4
046c32ac ldp      x20, x19, [sp, #0x60]
046c32b0 ldr      x30, [sp, #0x30]
046c32b4 ldp      x22, x21, [sp, #0x50]
046c32b8 ldp      x24, x23, [sp, #0x40]
046c32bc add      sp, sp, #0x70
046c32c0 ret      
046c32c4 bl       #0x30df908
046c32c8 bl       #0x30df910
046c32cc bl       #0x30df910
046c32d0 mov      x0, x19
046c32d4 bl       #0x30df908
046c32d8 b        #0x46c3328
046c32dc b        #0x46c32e4
046c32e0 b        #0x46c32e4
046c32e4 mov      x20, x1
046c32e8 mov      x19, x0
046c32ec cmp      w20, #1
046c32f0 b.ne     #0x46c3318
046c32f4 mov      x0, x19
046c32f8 bl       #0x7e29300
046c32fc ldr      x19, [x0]
046c3300 str      x19, [sp, #8]
046c3304 bl       #0x7e29310
046c3308 ldr      x8, [sp, #0x10]
046c330c b        #0x46c31cc
046c3310 mov      x20, x1
046c3314 mov      x19, x0
046c3318 add      x0, sp, #8
046c331c bl       #0x2c56e3c
046c3320 b        #0x46c3330
046c3324 b        #0x46c3328
046c3328 mov      x20, x1
046c332c mov      x19, x0
046c3330 cmp      w20, #1
046c3334 b.ne     #0x46c3354
046c3338 mov      x0, x19
046c333c bl       #0x7e29300
046c3340 ldr      x8, [x0]
046c3344 str      x8, [sp, #0x18]
046c3348 bl       #0x7e29310
046c334c b        #0x46c3238
046c3350 mov      x19, x0
046c3354 add      x0, sp, #0x18
046c3358 bl       #0x2c56e3c
046c335c mov      x0, x19
046c3360 bl       #0x31cdd1c
046c3364 bl       #0x2c56e30
