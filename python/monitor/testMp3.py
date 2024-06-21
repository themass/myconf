import base64

# Base64编码的文件路径
encoded_file_path = 'encoded.txt'
# 要保存解码内容的目标文件路径
decoded_file_path = 'decoded.txt'

# 打开Base64编码的文件并读取内容
with open(encoded_file_path, 'rb') as encoded_file:
    encoded_data = encoded_file.read()

# 解码Base64内容
decoded_data = base64.b64decode(encoded_data)

# 将解码后的数据写入到新文件中
with open(decoded_file_path, 'wb') as decoded_file:
    decoded_file.write(decoded_data)