import oead, zstandard


def zs_compress(data) -> bytes:
	return zstandard.compress(data, level=10)


def zs_decompress(data) -> bytes:
	return zstandard.decompress(data)



class SARC:
	"""A class for reading/writing SARC files

	SARC files are basically just an archive of files of various types"""

	def __init__(self, data: bytes) -> None:
		self.reader = oead.Sarc(zs_decompress(data))
		self.writer = oead.SarcWriter.from_sarc(self.reader)
		oead.SarcWriter.set_endianness(self.writer, oead.Endianness.Little) # Switch uses Little Endian
	
	def repack(self) -> bytes:
		return zs_compress(self.writer.write()[1])



# BYAML version 4 is the highest this library supports
# Even though the game uses a higher version, it does not use the new data types
# The game also does not check for a specific version
# This means that we can just edit the version marker down to 4
class BYAML:
	"""A class for reading/writing BYAML files

	BYAML files are basically just YAML files encoded in binary form"""

	def __init__(self, data, compressed=False) -> None:
		self.compressed = compressed
		if self.compressed:
			data = oead.Bytes(zs_decompress(data))
		
		data[0x2:0x4] = (4).to_bytes(2, 'little')
		self.info = oead.byml.from_binary(data)


	def repack(self) -> bytes:
		data = oead.byml.to_binary(self.info, False, 4)
		if self.compressed:
			data = zs_compress(data)
		
		return data
