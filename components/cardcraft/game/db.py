import motor.motor_asyncio

client: motor.motor_asyncio.AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:3135")
gamedb = client["cardcraft"]