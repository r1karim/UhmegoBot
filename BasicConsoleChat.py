import asyncio
from Uhmegobot import Event, ChatBot

class EventHandler(Event):
    @staticmethod
    def loadEvents():
        async def on_cfCreds(**kwargs):
            await kwargs['bot'].join_chatroom()

        async def on_conn(**kwargs):
            print(f"\n[Connected] You've connected to a chatroom with a stranger from {kwargs['data']['country']}.")

        async def on_end(**kwargs):
            print("\n[Disconnected] Stranger left... Searching for next chatroom.")
            await kwargs['bot'].join_chatroom()

        async def on_chatMessage(**kwargs):
            print(f"\nStranger: {kwargs['data']['message']}")

        cfCredsEvent = Event("cfCreds", on_cfCreds)
        connEvent = Event("conn", on_conn)
        onEnd = Event("end", on_end)
        onChatMessageEvent = Event("chatMessage", on_chatMessage)

async def main():
    URI = "wss://uhmegle.com/ws?text"
    EventHandler.loadEvents()
    chatBot = ChatBot()

    async def send_messages(bot):
        while True:
            msg = await asyncio.to_thread(input, "> ")
            if msg.lower() == "/exit":
                print("Exiting chat...")
                await bot.socket.close()
                break
            elif msg.lower() == "/skip":
                print("Skipping current chat...")
                await bot.join_chatroom()
            else:
                print("You: ", msg)
                await bot.send_message({"event": "sendMessage", "message": msg})

    await chatBot.establish_connection()

    receive_task = asyncio.create_task(chatBot.receive_message())
    send_task = asyncio.create_task(send_messages(chatBot))
    await asyncio.gather(receive_task, send_task)

if __name__ == "__main__":
    asyncio.run(main())