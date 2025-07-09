from baml_client import b
from baml_client.types import RequestMoreInformation


def main(resume: str):
    state = [resume]

    res = b.ExtractResume("\n".join(state))

    if isinstance(res, RequestMoreInformation):
        print(res.requests)
        print(res.reason)
        
    else:
        print(res)


if __name__ == "__main__":
    main()
