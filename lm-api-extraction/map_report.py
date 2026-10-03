from protocol import encode_map_request

tests = [
    ("1 zone", 1, [0, 0, 0, 0]),
    ("4 zones", 4, [0, 1, 2, 3]),
    ("high zones", 4, [1020, 1021, 1022, 1023]),
]

for name, count, zones in tests:
    data = encode_map_request(
        count,
        zones,
        [0, 0, 0, 0],
        renew=True,
    )

    print(f"\n=== {name} ===")
    print("Length:", len(data))
    print("Hex:", data.hex())
