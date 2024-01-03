from decouple import config
# Set your AWS credentials
app_token = config('app_token')
bot_token = config('bot_token')

print(app_token)
print(bot_token)