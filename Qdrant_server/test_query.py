import requests

# Thay thế YOUR_API_ENDPOINT bằng endpoint thực tế của bạn
query_url = 'https://qotvnsyf13.execute-api.ap-southeast-2.amazonaws.com/vector-database-stage/query'

# Điền thông tin query của bạn vào đây
data = {
    'query':"hello",
    'collection': 'First',
    'user_name': 'your_user_name',
    'file_name': 'your_file_name'
}

response = requests.post(query_url, json=data)
print(response)
