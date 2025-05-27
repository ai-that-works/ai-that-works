import asyncio
from baml_client import b
from baml_client.types import CompanyType

async def main(resume_str: str):
    print("Hello from workshop-bonus!")
    resume = await b.ExtractResume(resume_str)
    print(resume.experience)
    for experience in resume.experience:
        company = experience.company
        if company.company_type == "well-known":
            new_company_name = look_up_company_in_database(company.name)
            if new_company_name:
                print(new_company_name)
            else:
                # save this company to the database
                pass
        else:
            # save this to the database and flag for human review
            pass


if __name__ == "__main__":
    asyncio.run(main("some string"))

def look_up_company_in_database(company_name: str) -> str | None:
    pass
