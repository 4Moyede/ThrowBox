from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import time


dynamodb = boto3.resource('dynamodb', region_name='khu-1', endpoint_url="http://localhost:8080")
def tableScan(tableName):
    #Select * from tableName과 같다고 보시면 됩니다. Table의 모든 값을 가져옵니다.

    class DecimalEncoder(json.JSONEncoder):
      def default(self, o):
          if isinstance(o, decimal.Decimal):
              if abs(o) % 1 > 0:
                  return float(o)
              else:
                  return int(o)
          return super(DecimalEncoder, self).default(o)

    #dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url="http://localhost:8080")
    table = dynamodb.Table(tableName)
    response=table.scan()
    for i in response['Items']:
     print(json.dumps(i, cls=DecimalEncoder))

def insertToFile(isFile,name,path,createdDate,auth,s3Link):
    
  # Helper class to convert a DynamoDB item to JSON.
  
  class DecimalEncoder(json.JSONEncoder):
      def default(self, o):
          if isinstance(o, decimal.Decimal):
              if abs(o) % 1 > 0:
                  return float(o)
              else:
                  return int(o)
          return super(DecimalEncoder, self).default(o)


  #dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url="http://localhost:8080") 
  table = dynamodb.Table('File')

  response = table.put_item(
    Item={
          'id': str(name)+str(createdDate),
          'name': name,
          'info': {
              'isFile':isFile,
              'path':path,
              'createdDate':str(createdDate),
              'deletedDate':None,
              'auth':auth,
              's3Link':s3Link
          }
      }
  )
  #response의 헤더를 확인 하면 http response 값이 있습니다. 해당 값을 가져와서 db에 insert가 성공했는지 판단하면 될 것 같습니다

def createTableFile():
  #dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url="http://localhost:8080")
  table = dynamodb.create_table(
      
            TableName='File',
            KeySchema=[
            {   
                'AttributeName': 'id',#hae to Unique, we will use createdDate + name for now
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'name',#file name it will be used as sort key
                'KeyType': 'RANGE'  #Sort key 
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'#string
            },
            {
                'AttributeName': 'name',#file name
                'AttributeType': 'S'#string
            },

        ],
        ProvisionedThroughput={#USER AS DEFAULT
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
  )
  print("Table status:", table.table_status)


def testStart(): 
  createTableFile() 
  """
  isFile,Filename,path,createdDate,author, s3Link 순으로 입력하게 됩니다.
  createdDate는 '%Y-%m-%d-%H-%M-%S'의 포맷으로 들어가게 됩니다.
  id값은 fileName과 CreatedDate를 합쳐서 만들게 됩니다.
  """
  insertToFile(True,"testFileName2.text","./testRootDir", time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())),"testUserId","tempURLFORs3")
  
  
  tableScan("File")

testStart()