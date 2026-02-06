def calculate_checksum(data: str) -> tuple[int, list[dict]]:
    """
    Sender Side Logic:
    Returns (checksum, [ {"title": str, "content": list[str]} ])
    for visual separation.
    """
    steps = []
    
    if not data:
        data = ""
    
    # Step 1: Text -> Binary
    step1_lines = []
    encoded = data.encode('ascii') if data else b""
    binary_stream_str = ' '.join(f"{b:08b}" for b in encoded)
    step1_lines.append(f"Input: '{data}'")
    step1_lines.append(f"Binary Stream: {binary_stream_str}")
    steps.append({"title": "Step 1: Data to Binary Conversion", "content": step1_lines})
    
    if len(encoded) % 2 != 0:
        encoded += b'\0'
        # Implicitly handled in next step, but could log if needed
    
    # Step 2: Segmentation
    step2_lines = []
    words = []
    for i in range(0, len(encoded), 2):
        word = (encoded[i] << 8) + encoded[i+1]
        words.append(word)
        step2_lines.append(f"Word {i//2 + 1}: {encoded[i]:08b} {encoded[i+1]:08b} (0x{word:04X})")
    steps.append({"title": "Step 2: Binary Word Segmentation", "content": step2_lines})

    # Step 3: Summation
    step3_lines = []
    total = 0
    if not words:
         step3_lines.append("No words to sum.")
    
    for i, word in enumerate(words):
        prev_total = total
        total += word
        step3_lines.append(f"Add Word {i+1} (0x{word:04X}):")
        step3_lines.append(f"   {prev_total:016b} (Sum so far)")
        step3_lines.append(f" + {word:016b} (Next Word)")
        step3_lines.append(f" = {total:016b} (Intermediate)")
        
        if total > 0xFFFF:
            total = (total & 0xFFFF) + 1
            step3_lines.append(f"   [CARRY WRAP] -> {total:016b}")
            
    steps.append({"title": "Step 3: One's Complement Addition", "content": step3_lines})
    
    # Step 4: Invert
    step4_lines = []
    checksum = (~total) & 0xFFFF
    step4_lines.append(f"Final Sum:    {total:016b} (0x{total:04X})")
    step4_lines.append(f"Inverted Bits:{checksum:016b} (0x{checksum:04X})")
    step4_lines.append(f"CHECKSUM: 0x{checksum:04X}")
    steps.append({"title": "Step 4: One's Complement Operation", "content": step4_lines})
    
    return checksum, steps


def calculate_receiver_checksum(data: str, received_checksum: int) -> tuple[bool, int, list[dict]]:
    """
    Receiver Side Logic:
    Returns (is_valid, final_sum, [ {"title": str, "content": list[str]} ])
    """
    steps = []
    
    # 1. Text -> Binary
    step1 = []
    encoded = data.encode('ascii') if data else b""
    step1.append(f"Received Data: '{data}'")
    step1.append(f"Binary: {' '.join(f'{b:08b}' for b in encoded)}")
    steps.append({"title": "Step 1: Received Data to Binary Conversion", "content": step1})
    
    if len(encoded) % 2 != 0:
        encoded += b'\0'
        
    # 2. Segment
    step2 = []
    words = []
    for i in range(0, len(encoded), 2):
        word = (encoded[i] << 8) + encoded[i+1]
        words.append(word)
        step2.append(f"Word {i//2 + 1}: 0x{word:04X}")
    steps.append({"title": "Step 2: Binary Word Segmentation", "content": step2})
        
    # 3. Add Data + Checksum
    step3 = []
    total = 0
    
    # Add data words
    for i, word in enumerate(words):
        total += word
        if total > 0xFFFF:
            total = (total & 0xFFFF) + 1
    
    step3.append(f"Sum of Data Words: 0x{total:04X}")
    step3.append(f"Add Received Checksum: 0x{received_checksum:04X}")
    
    total += received_checksum
    if total > 0xFFFF:
        total = (total & 0xFFFF) + 1
        step3.append("[Carry Wrapped]")
        
    step3.append(f"Final Total: 0x{total:04X} ({total:016b})")
    steps.append({"title": "Step 3: One's Complement Addition (Including Checksum)", "content": step3})
    
    # 4. Verify
    step4 = []
    is_valid = (total == 0xFFFF)
    
    if is_valid:
        step4.append("Result is all 1s (0xFFFF) -> VALID")
    else:
        step4.append(f"Result (0x{total:04X}) IS NOT all 1s -> MISMATCH")
    
    steps.append({"title": "Step 4: Verification Result", "content": step4})
        
    return is_valid, total, steps
