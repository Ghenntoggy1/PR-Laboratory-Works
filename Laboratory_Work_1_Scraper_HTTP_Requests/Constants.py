class Constants:
    URL_WEBSITE = "https://darwin.md/telefoane/smartphone"
    DECODE_FORMAT = "utf-8"
    COOKIE = "_fbp=fb.1.1719846485266.162323985159961622; _ga=GA1.1.2125998619.1719846485; cf_clearance=.bMwPdD8M.HqjrNlVbQPCwTM4wWiLi0OQuBhegur5cE-1728031595-1.2.1.1-ACUx2Er753OSxOdsebs2m46dzKfZ0S8PbDPs5XXqYJPGdhpkOdsHREoIcr6WnygF3j4zwCYi0MPtl7XBlYglNBOmfUaOsh3zIRUB6i7ZyhcotvXPclHNBzkIz7dTGT8OFlDvCsvfDGU.HJnCerZ6T5W8bMeZ28J12CjfLQX.Auzv1J5KqtUT7jHorOqpXmG.T7QsxC657dXYk5L0En4mn6ua5lnCeTV1S5PznLexm1CCMU00EfLzXDbb5foqEfyh2odjgW8bO3JhPMNWhC6TyzyeYKWDW7edWV5pXaEnAV_Q8xG6NOat5zWMnyGThG3MRjfJOZbER2g7TcJ03Y.u7VtEQO2aONK_pANjkRJTGseOgB5gj3OTz6rdP8iJiu9FmNguEB0XFv4W6UicqdrmbqOJOdglLjp7_cWOB7TBPvpexDBXdB6wZH5jQiO_Xhs1; _gcl_au=1.1.1891374826.1728031495; XSRF-TOKEN=eyJpdiI6ImtlclNSUnY2MThSalhUWGhhM3FQYkE9PSIsInZhbHVlIjoib056cjk2V083N3RrVzdVWEJIdjhIWnFram9jT1VSMTFndm1ZdkVrbkFoYmpmR3dCOVhJa2tMazdxR0xBY2dwanFNUVhoazBiY2JsUVB2a2J6b2FtbkVGYVRZZzkvajlqcUR3QmU0ZWZYYm5NejZEbHFicDBsM0lZeGRwYmRPRXoiLCJtYWMiOiI4N2ZiYmE0NTVhMzY4OTIxYjExN2ViOGMzMWUwMzYyYmVjYjRmMmYyZThkODBkZTk4N2YzYzUyZDQzNDM1OGRkIiwidGFnIjoiIn0%3D; darwin_session=eyJpdiI6ImE3K1FzVk5DcnpRYlMrRTNSa3g2ckE9PSIsInZhbHVlIjoiQVk0M1B5aEl0eDZQZXh4NGI5cjNqVENPekpkNm1pWm1YWVEvWkhuc2Roak1wV0FxM2ViWE8zTTBZbll3cklQdlg4M0g3R2VTMFpmcFNzWmtRZ2hLeS9MVDVqTi81dFR4VisyUW5vSS9rTE0vOTkrT3RVYzcrem95M0lDdDhjbk8iLCJtYWMiOiIwN2M1OWIxMTJjMDJmN2RiNjA2ODQxZmZkOTQwMGUwNmUyMDIyY2Y4YWE3NDE5ODRkYWYyZjE4MjVjOWUxMGNiIiwidGFnIjoiIn0%3D; locale=eyJpdiI6ImI5MncweGpiZG1PajdQNmlYK1YxbUE9PSIsInZhbHVlIjoiRlYxNkhidHRWYjYzeHRtbFZaekFMWDI4QnBXNlJGL1RDNDhtbkdFUzN3NmZ2bGRIY2ttWXlLSjBLbk8ySzdVayIsIm1hYyI6ImYxYmY0NGE5YjI1MTI3ZGNlMzk3MTE1YWYzNWZiZGZjNjE4N2VhZGEwMmEzZmYyNmQzMjBlNTM0YTU0ZTk3N2EiLCJ0YWciOiIifQ%3D%3D; _ga_1L5MBWQHMV=GS1.1.1732451217.24.0.1732451217.60.0.0; _clck=1ee4tix%7C2%7Cfr5%7C0%7C1732; _clsk=s77dkb%7C1732451219546%7C1%7C1%7Cf.clarity.ms%2Fcollect"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    HOST = "darwin.md"
    HEADERS = {
        "User-Agent": USER_AGENT,
        "Cookie": COOKIE,
        # "Content-Type": "text/html; charset=UTF-8"
    }
    PARSER_TYPE = "html.parser"
    EXCHANGE_RATES = {
        ("MDL", "EUR"): 1 / 19.5,
        ("EUR", "MDL"): 19.5
    }
    PORT = 443
