from typing import Dict
import re
import dns.resolver
import requests


# Email validation function
def check_email(email: str) -> Dict[str, str]:
    # Simple regex pattern for email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Check format
    if not re.match(pattern, email):
        return {"validity": False, "msg": "Invalid email address format"}

    # Extract domain from email
    domain = email.split('@')[1]

    # Check if domain has MX records
    try:
        dns.resolver.resolve(domain, 'MX')
    except dns.resolver.NoAnswer:
        return {"validity": False, "msg": "Domain does not have MX records"}
    except dns.resolver.NXDOMAIN:
        return {"validity": False, "msg": "Domain does not exist"}
    except Exception as e:
        return {"validity": False, "msg": str(e)}

    return {"validity": True, "msg": "Valid email address"}
