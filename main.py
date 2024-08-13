import re
import asyncio
import aiohttp
from telethon import TelegramClient, events

# Define your API ID, hash, and phone number
api_id = ''
api_hash = ''

# Define your group chat where you want to send the messages (use the correct ID found from the previous script)
destination_chat = 'tiger_cc41'

BIN_API_URL = 'https://bins.antipublic.cc/bins/{bin}'

client = TelegramClient('tiger_scrapper', api_id, api_hash)

def filter_cards(text):
    regex = r'\b\d{16}\|\d{2}\|\d{2,4}\|\d{3,4}\b'
    matches = re.findall(regex, text)
    print(f"Filtered cards: {matches}")
    return matches

async def get_bin_info(bin):
    bin_info_url = BIN_API_URL.format(bin=bin)
    async with aiohttp.ClientSession() as session:
        async with session.get(bin_info_url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

def format_message(card_info, data):
    return (
        f"⚜️𝗖𝗮𝗿𝗱 ➔ <code>{card_info}</code>\n"
        f"⚜️𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➔ <b>Charged! ✅</b>\n"
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</b>\n"
        f"⚜️𝗜𝗻𝗳𝗼 ➔ <b>{data.get('brand', '')}, {data.get('type', '')}, {data.get('level', '')}</b>\n"
        f"⚜️𝐈𝐬𝐬𝐮𝐞𝐫 ➔ <b>{data.get('bank', '')}</b>\n"
        f"⚜️𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➔ <b>{data.get('country_name', '')}, {data.get('country_flag', '')}</b>\n"
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</b>\n"
        "⚜️𝗖𝗿𝐞𝗮𝐭𝗼𝐫 ➔ <b>@FKdzzz41</b>"
    )

@client.on(events.NewMessage)
async def handler(event):
    try:
        print(f"New message: {event.message.message}")
        if re.search(r'(CHARGED|Charged|CVV Charged|Charge Full|succeeded|CVV CHARGED|SHOPIFY|Shopify|shopify|Your order is confirmed!|Charge)', event.message.message):
            filtered_card_info = filter_cards(event.message.message)
            if not filtered_card_info:
                return

            for card_info in filtered_card_info:
                bin_number = card_info[:6]
                bin_info = await get_bin_info(bin_number)
                if bin_info:
                    formatted_message = format_message(card_info, bin_info)
                    try:
                        await client.send_message(destination_chat, formatted_message, parse_mode='html')
                        print(f"Sent message to {destination_chat}: {formatted_message}")
                    except Exception as e:
                        print(f"Failed to send message: {e}")

                    with open('reserved.txt', 'a', encoding='utf-8') as f:
                        f.write(card_info + '\n')
                else:
                    print(f"Failed to retrieve bin info for BIN: {bin_number}")
    except Exception as e:
        print(f"Error in handler: {e}")

async def main():
    # Start the client
    await client.start()
    print("Client Created")

    # Iterate through all the dialogs (channels, groups, etc.) the bot is part of
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            print(f"Adding event handler for channel: {dialog.name}")
            client.add_event_handler(handler, events.NewMessage(chats=dialog.id))

    # Verify the destination chat
    try:
        entity = await client.get_entity(destination_chat)
        print(f"Found destination chat: {entity.title if hasattr(entity, 'title') else entity.username}")
    except Exception as e:
        print(f"Error finding destination chat: {e}")
        return

    # Run the client until disconnected
    await client.run_until_disconnected()

# Run the script
asyncio.run(main())