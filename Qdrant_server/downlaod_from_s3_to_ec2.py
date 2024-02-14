import boto3

def download_file_from_s3(bucket_name, user_name, file_name, local_path):

    s3_key = f'{user_name}/{file_name}'
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"File downloaded successfully to {local_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

if __name__ == "__main__":

    bucket_name = 'chatbot-user-upload'
    user_name = 'trunglq'
    file_name = 'Personal_IDCard_LeQuocTrung.pdf'
    local_path = '/home/ubuntu/' + file_name  
    
    download_file_from_s3(bucket_name, user_name, file_name, local_path)
