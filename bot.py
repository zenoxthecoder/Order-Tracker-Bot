import discord
from urllib.parse import quote
from store import get_order, upsert_order, new_order

QUESTIONS = [
    "Enter the **order** ID",
    "Enter Product Details",
    "Status? (e.g. Pending, Paid, Completed)",
    "Price of the product? (in Taka)",
]


def build_embed(order, track_link):
    embed = discord.Embed(title="Order Created", color=0x2F855A)
    embed.add_field(name="Order ID", value=order["orderId"], inline=True)
    embed.add_field(name="Product", value=order["productName"], inline=True)
    embed.add_field(name="Status", value=order["status"], inline=True)
    embed.add_field(name="Price", value=f"৳ {order['price']}", inline=True)
    embed.add_field(name="Track", value=track_link, inline=False)
    embed.set_footer(text="Share the track link with your customer")
    return embed


class OrderBot(discord.Client):
    def __init__(self, base_url, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.sessions = {}

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()

        if content == "!cancel":
            self.sessions.pop(message.author.id, None)
            await message.reply("Creation canceled.")
            return

        if content == "!create":
            self.sessions[message.author.id] = {"step": 0, "data": {}}
            await message.reply(QUESTIONS[0])
            return

        session = self.sessions.get(message.author.id)
        if not session:
            return

        step = session["step"]
        answer = content

        if step == 0:
            if not answer:
                await message.reply("Please enter a valid order ID.")
                return
            session["data"]["orderId"] = answer
            existing = get_order(answer)
            if existing:
                await message.reply("Warning: this order ID already exists and will be overwritten.")

        elif step == 1:
            if not answer:
                await message.reply("Please enter product details.")
                return
            session["data"]["productName"] = answer

        elif step == 2:
            if not answer:
                await message.reply("Please enter a status.")
                return
            session["data"]["status"] = answer

        elif step == 3:
            price = "".join(ch for ch in answer if ch.isdigit() or ch == ".")
            if not price:
                await message.reply("Please enter a numeric price (example: 1200).")
                return
            session["data"]["price"] = price

            order = new_order(
                session["data"]["orderId"],
                session["data"]["productName"],
                session["data"]["status"],
                session["data"]["price"],
            )

            upsert_order(order)

            track_link = f"{self.base_url}/track/{quote(order['orderId'])}"
            embed = build_embed(order, track_link)

            await message.reply(
                content=f"**Track your order here :**\n{track_link}",
                embed=embed,
            )

            self.sessions.pop(message.author.id, None)
            return

        session["step"] += 1
        await message.reply(QUESTIONS[session["step"]])
