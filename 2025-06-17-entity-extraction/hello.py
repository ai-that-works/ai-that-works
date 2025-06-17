from baml_client import b
from baml_client.types import Company



def load_companies():
    return {
        "Microsoft Corporation": ["XBOX", "Azure", "MSFT"],
        "Google": ["GCP", "GMAIL"],
        "Amazon": ["AWS", "Amazon Prime", "Amazon Web Services"],
        "Apple": ["Apple", "Apple Music", "Apple TV"],
        "Facebook": ["Meta", "Facebook", "Instagram"],
        "Twitter": ["X", "Twitter", "X.com"],
    }

def pick_potential_company(content: str) -> str | None:
    valid_companies = load_companies()
    for legal_name, aliases in valid_companies.items():
        if any(alias in content for alias in aliases):
            return legal_name
    return None

def valid_company(company: Company) -> Company | None:
    assert company.legal_name is not None
    valid_companies = load_companies()
    for legal_name, aliases in valid_companies.items():
        if legal_name == company.legal_name:
            return company
    
    # todo: ask an LLM to find a better match
    # THIS IS CLASSIFICATION PROBLEM (refer to video)
    potential_company = pick_potential_company(company.legal_name)
    if potential_company is None:
        from_name = pick_potential_company(company.name)
        if from_name is None:
            return None
        else:
            company.legal_name = from_name
            return company
    else:
        company.legal_name = potential_company
        return company


def main(content: str):
    resume = b.ExtractResume(content)
    print("--------------------------------")
    print(resume.model_dump_json(indent=2))
    print("--------------------------------")
    for exp in resume.experience:
        match exp.company.company_type:
            case "startup":
                # do nothing
                exp.company.legal_name = None
                # break
            case "well_known" | "well_known_subsidary":
                if exp.company.legal_name is None:
                    potential_company = pick_potential_company(exp.company.name)
                    if potential_company is None:
                        exp.company.legal_name = None
                else:
                    result = valid_company(exp.company)
                    if result is None:
                        exp.company.legal_name = None
                    else:
                        exp.company = result
            case _:
                raise ValueError(f"Unknown company type: {exp.company.company_type}")
    print("--------------------------------")
    print("AFTER")
    print("--------------------------------")
    print(resume.model_dump_json(indent=2))

    for exp in resume.experience:
        if exp.company.legal_name is None:
            print("kick of JOB to find a better match: ", exp.company.name)

if __name__ == "__main__":
    main("""
        Vaibhav Gupta
      vbv@boundaryml.com

      Experience:
      - Founder at BoundaryML
      - CV Engineer at GCP
      - CV Engineer at XBOX

      Skills:
      - Rust
      - C++
         """)
