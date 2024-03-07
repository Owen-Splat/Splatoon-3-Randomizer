import zstandard
import struct
import yaml
import oead


def zs_compress(data):
	return zstandard.compress(data, level=10)


def zs_decompress(data):
	return zstandard.decompress(data)


# def readBytes(data: bytes, start: int, length: int, endianness: str, signed: bool = False):
# 	return int.from_bytes(data[start : start + length], endianness, signed=signed)


# def readFloat(data: bytes, start: int, length: int, endianness: str):
# 	if endianness == 'big':
# 		return float(struct.unpack('>f', data[start : start + length])[0])
# 	if endianness == 'little':
# 		return float(struct.unpack('<f', data[start : start + length])[0])


# def readDouble(data: bytes, start: int, length: int, endianness: str):
# 	if endianness == 'big':
# 		return float(struct.unpack('>d', data[start : start + length])[0])
# 	if endianness == 'little':
# 		return float(struct.unpack('<d', data[start : start + length])[0])


# def readString(data, start):
# 	result = b''
# 	index = start

# 	while index < len(data) and data[index]:
# 		result += data[index : index + 1]
# 		index += 1

# 	return str(result, 'utf-8')


# def getNodeData(data: bytes, offset: int, node_type: int, endianness: str, key_table=None, string_table=None):
# 	if node_type == 0xA0: # string
# 		value = str(string_table.strings[readBytes(data, offset, 4, endianness)])
	
# 	elif node_type == 0xC0: # array
# 		value = BymlArray(data, readBytes(data, offset, 4, endianness), endianness, key_table, string_table).data_table
	
# 	elif node_type == 0xC1: # dict
# 		value = BymlDict(data, readBytes(data, offset, 4, endianness), endianness, key_table, string_table).pairs
	
# 	elif node_type == 0xD0: # bool
# 		value = bool(readBytes(data, offset, 4, endianness))
	
# 	elif node_type == 0xD1: # signed int
# 		value = readBytes(data, offset, 4, endianness, signed=True)

# 	elif node_type == 0xD2: # float
# 		value = readFloat(data, offset, 4, endianness)

# 	elif node_type == 0xD3: # unsigned int
# 		value = readBytes(data, offset, 4, endianness, signed=False)

# 	elif node_type == 0xD4: # signed int 64 bits
# 		value = readBytes(data, readBytes(data, offset, 4, endianness), 8, endianness, signed=True)
	
# 	elif node_type == 0xD5: # unsigned int 64 bits
# 		value = readBytes(data, readBytes(data, offset, 4, endianness), 8, endianness, signed=False)
	
# 	elif node_type == 0xD6: # double
# 		value = readDouble(data, readBytes(data, offset, 4, endianness), 8, endianness)
	
# 	elif node_type == 0xFF: # null (always 0)
# 		value = 0

# 	else:
# 		raise TypeError(f'Invalid Array Node Type: {hex(node_type)}')
	
# 	return value


# def defineDataType(node_type):
# 	if node_type == 0xA0:
# 		tag = '!!str'
# 	elif node_type == 0xC0:
# 		tag = '!!seq'
# 	elif node_type == 0xC1:
# 		tag = '!!map'
# 	elif node_type == 0xD0:
# 		tag = '!!bool'
# 	elif node_type == 0xD1:
# 		tag = '!!int32'
# 	elif node_type == 0xD2:
# 		tag = '!!float'
# 	elif node_type == 0xD3:
# 		tag = '!!uint32'
# 	elif node_type == 0xD4:
# 		tag = '!!int64'
# 	elif node_type == 0xD5:
# 		tag = '!!uint64'
# 	elif node_type == 0xD6:
# 		tag = '!!double'
# 	elif node_type == 0xFF:
# 		tag = '!!null'
	
# 	return tag



class SARC:
	def __init__(self, data: bytes):
		self.reader = oead.Sarc(zs_decompress(data))
		self.writer = oead.SarcWriter.from_sarc(self.reader)
		oead.SarcWriter.set_endianness(self.writer, oead.Endianness.Little) # Switch uses Little Endian
	
	def repack(self):
		return zs_compress(self.writer.write()[1])



class BYAML:
	def __init__(self, data, compressed=False):
		self.compressed = compressed
		if self.compressed:
			data = oead.Bytes(zs_decompress(data))
		
		data[0x2:0x4] = (4).to_bytes(2, 'little')
		self.info = oead.byml.from_binary(data)

		# self.magic = data[0x0:0x2]
		# if self.magic == b'BY':
		# 	self.endianness = 'big'
		# elif self.magic == b'YB':
		# 	self.endianness = 'little'
		# else:
		# 	raise ValueError('Invalid magic number!')

		# self.version = readBytes(data, 0x2, 2, self.endianness)

		# offset_to_dict_key_table = readBytes(data, 0x4, 4, self.endianness)
		# self.dict_key_table = StringTable(data, offset_to_dict_key_table, self.endianness)
		# offset_to_string_table = readBytes(data, 0x8, 4, self.endianness)
		# self.string_table = StringTable(data, offset_to_string_table, self.endianness)

		# offset_to_root_node = readBytes(data, 0xC, 4, self.endianness)
		# root_node_type = readBytes(data, offset_to_root_node, 1, self.endianness)

		# if root_node_type == 0xC0:
		# 	self.root_node = BymlArray(data, offset_to_root_node, self.endianness, self.dict_key_table, self.string_table)
		# elif root_node_type == 0xC1:
		# 	self.root_node = BymlDict(data, offset_to_root_node, self.endianness, self.dict_key_table, self.string_table)
		# else:
		# 	raise TypeError(f'Invalid root node type: {root_node_type}')


	def repack(self):
		# txt_yml = str(yaml.dump(self.root_node.pairs, encoding='utf-8', allow_unicode=True), 'utf-8')
		# txt_yml = txt_yml.replace('"', '')
		# byml = oead.byml.from_text(txt_yml)
		data = oead.byml.to_binary(self.info, False, 4) # BYAML version 4 is the highest this library supports, but still works

		if self.compressed:
			data = zs_compress(data)
		
		return data



# class BymlDict():
# 	def __init__(self, data, offset, endianness, key_table, string_table):
# 		self.node_type = readBytes(data, offset, 1, endianness)
# 		self.num_pairs = readBytes(data, offset+1, 3, endianness)
# 		pair_table = []
# 		for i in range(self.num_pairs):
# 			pair_table.append(self.Pair(data, offset+(0x4+(8*i)), endianness, key_table, string_table))
		
# 		self.pairs = {}

# 		for pair in pair_table:
# 			key = key_table.strings[pair.dict_key_index]
# 			if key == 'Type':
# 				key = '"Type"'
# 			self.pairs[key] = pair.value
	
	
# 	class Pair:
# 		def __init__(self, data, offset, endianness, key_table, string_table):
# 			self.dict_key_index = readBytes(data, offset+0x0, 3, endianness)
# 			self.node_type = readBytes(data, offset+0x3, 1, endianness)
# 			try:
# 				self.value = getNodeData(data, offset+0x4, self.node_type, endianness, key_table, string_table)
# 			except TypeError:
# 				print(key_table.strings[self.dict_key_index])
# 				exit()



# class BymlArray():
# 	def __init__(self, data, offset, endianness, key_table, string_table):
# 		self.node_type = readBytes(data, offset, 1, endianness)
# 		self.num_elements = readBytes(data, offset+1, 3, endianness)

# 		self.type_table = []
# 		for i in range(self.num_elements):
# 			self.type_table.append(readBytes(data, offset+4+i, 1, endianness))
		
# 		num_null_bytes = 4 - (self.num_elements % 4) if self.num_elements > 0 else 0
# 		if num_null_bytes == 4:
# 			num_null_bytes = 0
		
# 		data_offset = offset + 4 + self.num_elements + num_null_bytes
# 		self.data_table = []
# 		for i in range(self.num_elements):
# 			value = getNodeData(data, data_offset + (4*i), self.type_table[i], endianness, key_table, string_table)
# 			self.data_table.append(value)



# class StringTable():
# 	def __init__(self, data, offset, endianness):
# 		self.node_type = readBytes(data, offset, 1, endianness)
# 		if self.node_type != 0xC2:
# 			raise TypeError('Invalid String Table Node Type!')

# 		self.num_strings = readBytes(data, offset + 0x1, 3, endianness)

# 		self.address_table = []
# 		for i in range(self.num_strings):
# 			self.address_table.append(readBytes(data, offset + (0x4*(i + 1)), 4, endianness))

# 		self.strings = []
# 		for addr in self.address_table:
# 			self.strings.append(readString(data, offset + addr))
