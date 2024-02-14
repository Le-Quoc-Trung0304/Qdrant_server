import requests
import json
import base64

# Đường dẫn đến file bạn muốn upload
file_path = '/home/trung0304/Downloads/Medical_checkup_Le.pdf'
with open(file_path, 'rb') as file_to_upload:
    # encoded_file = base64.b64encode(file_to_upload.read()).decode('utf-8')
    encoded_file = file_to_upload.read()

data = {
    'user_name': 'trunglq',
    'file_name': 'Medical_checkup_Le.pdf',
    'document': encoded_file  # Gửi file dưới dạng chuỗi base64
}

# Endpoint của bạn
upload_url = 'https://qotvnsyf13.execute-api.ap-southeast-2.amazonaws.com/vector-database-stage/upload'

# Gửi request dưới dạng JSON
response = requests.put(upload_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
print(response)
