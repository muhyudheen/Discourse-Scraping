import requests
import os

cookies = {
    '_fbp': 'fb.2.1720452718463.229248908494530088',
    '_ga_YRLBGM14X9': 'GS2.1.s1760076888$o1$g1$t1760076967$j60$l0$h0',
    '_ga_QHXRKWW9HH': 'GS2.3.s1763201453$o1$g0$t1763201453$j60$l0$h0',
    '_ga': 'GA1.1.1812424809.1755104123',
    '_gcl_au': '1.1.1251048522.1769350103',
    '_ga_5HTJMW67XK': 'GS2.1.s1771857094$o135$g0$t1771857107$j47$l0$h0',
    '_ga_08NPRH5L4M': 'GS2.1.s1771885242$o261$g0$t1771885242$j60$l0$h0',
    '_forum_session': 'Cb40PdP7d%2Butn5FmLcWQbqXIaG7WsKJcb%2BE4A89G%2BH0RF9p42I2wOVmw2rS468yH1dnz8k7sWzj8QyrdOMle0GnA8f5fj3o658LEBDXcyi8hrjlyOfjWNxtlOIqrwHXUaYf6EY2cwpZFi%2FOBsGzXuOr6fDFmN6rWF5DFI3aj53rxJfxyLlw0%2B9IdHRPPwXXZLZAoww1OfZEX8r1gHskrS1fgNfOwGXfJ6teB3uMHngtKFxLLZXPfMM0S%2BSAAhpCyO%2FOLY3JJXxUSNMa260Y%3D--oNoPvmsc4f5MTL0M--7mi%2Fje6LMGXf5bZEyNI87A%3D%3D',
    '_t': 'l1HwKjoTBcKEA8Lz0hZojXNALPxb0XM1%2FwF%2FWC5LhK8jGkZ1XL7fskwON%2FoiPFwpMt13s8xNOb8ifti0fbW%2FlZ3xm89BmjnjEhqSihBw8tTnlmY3yCDWSgfVDJ4ZhjJ0z2sKU1STAiS%2BjuJuVekAHBQWQUcv%2FZJ8ATej1EFMtuPblCBXkmIHanzuckLwflagFyeU6jG1c4Y%2BT2Lw2VPQxg8Wqu7pIxUc9oyt5o%2BgSw7zTUxddGXP9CV%2BCOqVO1Z4DFJiE6kVglS8BFENaNKoGP1kPgqFz5sXeuJdOg%3D%3D--TevX%2Fywc%2FRaBvg%2B9--wvqLM2hYHqIAcDMiPxDgcQ%3D%3D',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'discourse-logged-in': 'true',
    'discourse-present': 'true',
    'discourse-track-view': 'true',
    'priority': 'u=1, i',
    'referer': 'https://discourse.onlinedegree.iitm.ac.in/u?name=hh&order=likes_recieved&period=all',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-csrf-token': 'uWNxfwd5OtAV_L0pRup-3BirzT7eFoU8MXm6cfG6Z6pReMntPhykU91UPU0eLwh0Z6s1aQ4_jTv9EsrPX3cipA',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': '_fbp=fb.2.1720452718463.229248908494530088; _ga_YRLBGM14X9=GS2.1.s1760076888$o1$g1$t1760076967$j60$l0$h0; _ga_QHXRKWW9HH=GS2.3.s1763201453$o1$g0$t1763201453$j60$l0$h0; _ga=GA1.1.1812424809.1755104123; _gcl_au=1.1.1251048522.1769350103; _ga_5HTJMW67XK=GS2.1.s1771857094$o135$g0$t1771857107$j47$l0$h0; _ga_08NPRH5L4M=GS2.1.s1771885242$o261$g0$t1771885242$j60$l0$h0; _forum_session=Cb40PdP7d%2Butn5FmLcWQbqXIaG7WsKJcb%2BE4A89G%2BH0RF9p42I2wOVmw2rS468yH1dnz8k7sWzj8QyrdOMle0GnA8f5fj3o658LEBDXcyi8hrjlyOfjWNxtlOIqrwHXUaYf6EY2cwpZFi%2FOBsGzXuOr6fDFmN6rWF5DFI3aj53rxJfxyLlw0%2B9IdHRPPwXXZLZAoww1OfZEX8r1gHskrS1fgNfOwGXfJ6teB3uMHngtKFxLLZXPfMM0S%2BSAAhpCyO%2FOLY3JJXxUSNMa260Y%3D--oNoPvmsc4f5MTL0M--7mi%2Fje6LMGXf5bZEyNI87A%3D%3D; _t=l1HwKjoTBcKEA8Lz0hZojXNALPxb0XM1%2FwF%2FWC5LhK8jGkZ1XL7fskwON%2FoiPFwpMt13s8xNOb8ifti0fbW%2FlZ3xm89BmjnjEhqSihBw8tTnlmY3yCDWSgfVDJ4ZhjJ0z2sKU1STAiS%2BjuJuVekAHBQWQUcv%2FZJ8ATej1EFMtuPblCBXkmIHanzuckLwflagFyeU6jG1c4Y%2BT2Lw2VPQxg8Wqu7pIxUc9oyt5o%2BgSw7zTUxddGXP9CV%2BCOqVO1Z4DFJiE6kVglS8BFENaNKoGP1kPgqFz5sXeuJdOg%3D%3D--TevX%2Fywc%2FRaBvg%2B9--wvqLM2hYHqIAcDMiPxDgcQ%3D%3D',
}

os.makedirs('data', exist_ok=True)

for page in range(1, 11):
    params= {
        "period": "all",
        "order": "likes_recieved",
        "page": str(page),
    }
    
    response = requests.get('https://discourse.onlinedegree.iitm.ac.in/directory_items',
                            params=params, cookies=cookies, headers=headers)
    
    data = response.json()
    
    with open(f"data/page_{page}.json", 'w', encoding='utf-8') as f:
        import json
        json.dump(data,f, indent=2)
        
    print(f"saved page {page}")