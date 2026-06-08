import heapq

class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    heap = [Node(ch, f) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def build_codes(node, prefix='', codebook=None):
    if codebook is None:
        codebook = {}
    if node:
        if node.char is not None:
            codebook[node.char] = prefix
        else:
            build_codes(node.left, prefix + '0', codebook)
            build_codes(node.right, prefix + '1', codebook)
    return codebook

# --- Сериализация и десериализация дерева в текст ---

def serialize_tree_txt(node):
    if node is None:
        return ''
    if node.char is not None:
        return f'L{node.char}'
    return '#' + serialize_tree_txt(node.left) + serialize_tree_txt(node.right)

def deserialize_tree_txt(s, index=0):
    def helper():
        nonlocal index
        if index >= len(s):
            return None
        if s[index] == 'L':
            index += 1
            node = Node(char=s[index])
            index += 1
            return node
        elif s[index] == '#':
            index += 1
            left = helper()
            right = helper()
            return Node(left=left, right=right)
    return helper()

def encode_text(text, codebook):
    return ''.join(codebook[ch] for ch in text)

def pad_encoded_text(encoded_text):
    extra_bits = (8 - len(encoded_text) % 8) % 8
    padded_text = encoded_text + '0' * extra_bits
    return padded_text, extra_bits

def to_bytes(padded_text):
    return bytes(int(padded_text[i:i+8], 2) for i in range(0, len(padded_text), 8))

def from_bytes(data, extra_bits):
    bit_str = ''.join(f'{byte:08b}' for byte in data)
    if extra_bits:
        bit_str = bit_str[:-extra_bits]
    return bit_str

def save_huffman_file_txt(filename, tree, encoded_text):
    tree_str = serialize_tree_txt(tree)
    padded_text, extra_bits = pad_encoded_text(encoded_text)
    encoded_bytes = to_bytes(padded_text)
    with open(filename, 'w') as f:
        f.write(tree_str + '\n')
        f.write(str(extra_bits) + '\n')
        f.write(encoded_bytes.hex() + '\n')

def load_huffman_file_txt(filename):
    with open(filename, 'r') as f:
        tree_str = f.readline().rstrip('\n')
        extra_bits = int(f.readline().rstrip('\n'))
        encoded_hex = f.readline().rstrip('\n')
        encoded_bytes = bytes.fromhex(encoded_hex)
    tree = deserialize_tree_txt(tree_str)
    return tree, encoded_bytes, extra_bits

def decode_text(encoded_bits, tree):
    decoded = []
    node = tree
    for bit in encoded_bits:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded.append(node.char)
            node = tree
    return ''.join(decoded)

# --- Пример использования ---

def main():
    # Кодирование
    text = input("Введите текст для кодирования: ")
    tree = build_huffman_tree(text)
    codebook = build_codes(tree)
    encoded_text = encode_text(text, codebook)
    save_huffman_file_txt('output.txt', tree, encoded_text)
    print("Текст закодирован и сохранён в output.txt")

    # Декодирование
    tree2, encoded_bytes, extra_bits = load_huffman_file_txt('output.txt')
    encoded_bits = from_bytes(encoded_bytes, extra_bits)
    decoded_text = decode_text(encoded_bits, tree2)
    print("Декодированный текст:", decoded_text)


if __name__ == '__main__':
    main()