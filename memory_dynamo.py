# import boto3
# from boto3.dynamodb.conditions import Key
# from config import AWS_REGION, DDB_ENDPOINT

# dynamodb = boto3.resource(
#     "dynamodb",
#     region_name=AWS_REGION,
#     endpoint_url=DDB_ENDPOINT
# # )

# # table = dynamodb.Table("SupportSessions")

# def save_message(user_id, session_id, msg):
#     sk = f"{session_id}#{msg['timestamp']}"
#     item = {
#         "user_id": user_id,
#         "sk": sk,
#         **msg
#     }
#     table.put_item(Item=item)

# def fetch_recent(user_id, session_id, limit=10):
#     sk_start = f"{session_id}#"
#     resp = table.query(
#         KeyConditionExpression=Key("user_id").eq(user_id)
#         & Key("sk").begins_with(sk_start),
#         Limit=limit,
#         ScanIndexForward=False
#     )
#     return resp.get("Items", [])
