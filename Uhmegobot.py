import asyncio
from asyncio import get_event_loop

import websockets
import aiohttp
import json
from aiohttp import ClientWebSocketResponse

URI = "wss://uhmegle.com/ws?text"

class Event:
    registered_events = []

    def __init__(self, code: str, onClick):
        self.eventCode = code
        Event.registered_events.append(self)
        self.onClick = onClick

    async def __invoke__(self,**kwargs):
        await self.onClick(**kwargs)

    def __repr__(self):
        return f"{self.eventCode}"

    @staticmethod
    def getEventByCode(codeName:str):
        for event in Event.registered_events:
            if event.eventCode == codeName:
                return event

class ChatBot:
    def __init__(self, name="ChatClient"):
        self.name = name
        self.headers = ChatBot.loadHeaders()
        self.session = aiohttp.ClientSession()
        self.socket = None

    def getName(self):
        return self.name

    async def establish_connection(self):
        try:
            self.socket = await self.session.ws_connect(URI, headers=self.headers)
            print(f"[SUCCESS] {self.name} connected to the WebSocket!")
        except Exception as exception:
            print(f"[ERROR] {self.name} connection to the WebSocket failed {exception}")

    async def receive_message(self):
        async for message in self.socket:
            try:
                data = json.loads(message.data)
                eventCode = data.get("event")
                event = Event.getEventByCode(eventCode)
                if event:
                    await event.__invoke__(bot=self, data=data)
            except json.JSONDecodeError as e:
                continue
            except Exception as e:
                print(data)
                print(e)
                print("error in receiving message")

    async def send_message(self, message):
        await self.socket.send_json(message)

    async def join_chatroom(self):
        await self.socket.send_json({
            "event": "findPeer",
            "interest": False,
            "type": "text",
            "countries": ["ZZ"],
            "interests": "[]"
        })

    @staticmethod
    def loadHeaders():
        try:
            with open("config/headers.json") as f:
                return json.load(f)
        except FileNotFoundError:
            exit(1)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from headers.json. Please check the file format.")
        except Exception as e:
            print(f"Unexpected error occurred while loading headers.json: {e}")
        return None