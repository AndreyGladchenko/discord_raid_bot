# import asyncio
# import json
# import time
#
# from bot import send_message_to_user
#
#
# async def check_and_send_messages():
#     while True:
#         with open('tests.txt', 'r') as file:
#             gameplay_log = json.load(file)
#         with open('subscribers.json', 'r') as file2:
#             subscribers = json.load(file2)
#
#         # print(subscribers, gameplay_log)
#         print(subscribers.values())
#         for event in gameplay_log:
#             print(gameplay_log[event]["alert_sent"])
#             if not gameplay_log[event]["alert_sent"]:
#                 if gameplay_log[event]["owner"] in subscribers.values():
#                     await send_message_to_user(f'Wake up {gameplay_log[event]["owner"]}, {gameplay_log[event]["user"]} is lockpicking your {gameplay_log[event]["object"]}. He tried {gameplay_log[event]["attempts"]} times with {gameplay_log[event]["success"]} success',
#                                          [user_id for user_id, username in subscribers.items() if username == gameplay_log[event]["owner"]][0])
#
#         await asyncio.sleep(1)
