import asyncio, logging
from Uhmegobot import Event, ChatBot

class EventHandler(Event):
    @staticmethod
    def loadEvents():
        async def on_chatMessage(**kwargs):
            print( kwargs['bot'].getRepresentation(), " -> ", kwargs['bot'].otherEnd.getRepresentation(), ": ", kwargs['data']['message'] )
            await kwargs['bot'].otherEnd.send_message({
                'event':'sendMessage',
                'message':kwargs['data']['message']
            })

        async def on_conn(**kwargs):
            kwargs['bot'].currentCountry = kwargs['data']['country']
            print(f"\n[Connected] { kwargs['bot'].getName() } connected to a chatroom with a stranger from {kwargs['data']['country']}.")

        async def on_end(**kwargs):
            print(f"\n[Disconnected] Stranger left in room of {kwargs['bot'].getName()}... Searching for next chatroom.")
            await kwargs['bot'].join_chatroom()

        async def on_cfCreds(**kwargs):
            await kwargs['bot'].join_chatroom()

        cfCredsEvent = EventHandler("cfCreds", on_cfCreds)
        connEvent = EventHandler("conn", on_conn)
        onEnd = EventHandler("end", on_end)
        onChatMessageEvent = EventHandler("chatMessage", on_chatMessage)

class Bot(ChatBot):
    def __init__(self, name):
        super().__init__(name=name)
        self.otherEnd = None
        self.currentCountry = ""

    def getRepresentation(self):
        return f"{self.name}({self.currentCountry})"

async def main():
    URI = "wss://uhmegle.com/ws?text"

    EventHandler.loadEvents()
    alphaBot = Bot("Alpha")
    betaBot = Bot("Beta")
    alphaBot.otherEnd = betaBot
    betaBot.otherEnd = alphaBot

    await alphaBot.establish_connection()
    await betaBot.establish_connection()
    alpha_receive = asyncio.create_task(alphaBot.receive_message())
    beta_receive = asyncio.create_task(betaBot.receive_message())
    await asyncio.gather(alpha_receive, beta_receive)

asyncio.run(main())