#!/usr/bin/python3
import os
import json
import boto3
import pathlib
import logging
import datetime
from botocore.exceptions import ClientError

DATE_TIME = (datetime.datetime.now()).strftime("%Y_%m_%d_%H_%M")
DUMP_NAME = "documentdb_{}_full_{}.dump.gz".format(os.environ["SPACE"], DATE_TIME)
PEM_KEY = 'rds-combined-ca-bundle.pem'
SESSION = boto3.session.Session()


def get_secret(stack_name):

	client = SESSION.client('secretsmanager')

	secret_name = f'/docdb{stack_name}/masteruser'
	get_secret_value_response = client.get_secret_value(SecretId=secret_name)
	secret = get_secret_value_response['SecretString']

	return json.loads(secret)

def get_bucket(stack_name):

	s3_client = SESSION.client('s3')
	response = s3_client.list_buckets()

	for bucket in response['Buckets']:
		if f's3bucketfordocdb{stack_name}' in bucket["Name"]:
			bucket_name = f'{bucket["Name"]}'
			print(f'### Bucket name is: {bucket_name}')
			return bucket_name
	return False

def create_backup(space):

	secret = get_secret(os.environ["SPACE"])
	
	db_username = secret['username']
	db_password = secret['password']
	db_host = secret['host']
	db_port = secret['port']

	client = "mongodump --ssl -h {}:{} --sslCAFile /data/{} -u {} -p '{}' --gzip --archive={}".format(
		db_host,
		db_port,
		PEM_KEY,
		db_username,
		db_password,
		DUMP_NAME
	)
	print(f'### Cli is: {client}')	# DEBUG METHOD!

	try:
		os.system(client)
	except ClientError as e:
		logging.error(e)
		print(f"XXX DEBUG | Error creating backup: {space} space | DEBUG XXX")
		return False
	return True

def upload_files(file_name, bucket, object_name=None):

	if object_name is None:
		object_name = file_name

	s3_client = SESSION.client('s3')

	try:
		s3_client.upload_file(file_name, bucket, object_name)
		print(f"### '{file_name}' has been uploaded to '{bucket}'")
	except ClientError as e:
		logging.error(e)
		print(f"XXX DEBUG | Error uploading to s3: {space} space | DEBUG XXX")
		return False
	return True


print("### Env is: {}".format(os.environ["SPACE"]))
create_backup(os.environ["SPACE"])
os.system('echo "### Check work and data dir: "; pwd; ls -lah . /data')		# DEBUG METHOD!
os.system('touch test_upload')												# DEBUG METHOD!
S3_BUCKET = get_bucket(os.environ["SPACE"])
upload_files('test_upload', S3_BUCKET)										# DEBUG METHOD!
upload_files(DUMP_NAME, S3_BUCKET)
os.remove(DUMP_NAME)
os.system('echo "### Double check workdir: "; ls -lah')						# DEBUG METHOD!
