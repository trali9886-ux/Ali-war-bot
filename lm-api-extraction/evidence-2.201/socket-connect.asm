046ca25c ldr      x9, [x8, #0xb8]
046ca260 adrp     x8, #0x8207000
046ca264 ldr      x8, [x8, #0xaf0]
046ca268 ldr      w20, [x9, #0x150]
046ca26c strb     wzr, [x9, #0xcd]
046ca270 ldr      x0, [x8]
046ca274 bl       #0x30df900
046ca278 mov      w1, w20
046ca27c mov      w2, #1
046ca280 mov      w3, #6
046ca284 mov      x4, xzr
046ca288 mov      x19, x0
046ca28c bl       #0x779b2cc
046ca290 cbz      x19, #0x46ca378
046ca294 mov      x0, x19
046ca298 mov      w1, wzr
