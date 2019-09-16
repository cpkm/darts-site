from flask import current_app
from threading import Thread
import boto3

def upload_file_to_s3(file, bucket_name, acl='public-read', folder=None):

    s3 = boto3.client(
       's3',
       aws_access_key_id=current_app.config['S3_KEY'],
       aws_secret_access_key=current_app.config['S3_SECRET'],
       region_name=current_app.config['AWS_DEFAULT_REGION'])

    result = s3.get_bucket_acl(Bucket=bucket_name)
    print(result)

    if folder:
        filename = folder+'/'+file.filename
    else:
        filename = file.filename

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                'ACL': acl,
                'ContentType': file.content_type})

    except Exception as e:
        print('Failure during upload: ', e)
        return None

    return '{}{}'.format(current_app.config['S3_LOCATION'], filename)
