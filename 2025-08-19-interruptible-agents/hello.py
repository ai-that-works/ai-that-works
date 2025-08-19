import asyncio

from manager import ResearchManager
from dotenv import load_dotenv


async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    load_dotenv("../.env")
    asyncio.run(main())
