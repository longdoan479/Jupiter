import asyncio
import time

import aiohttp
from solana.rpc.api import Client

# Chuỗi ký tự cần tạo QR code
from Include.AccountSol import AccountSol
from Constant import g_RPC_SOL, strPriceJupAPI, g_ProxyAddress
from FileProcessing import FileProcessing

async def main():

    for i in range(0, 100):
        pInputMint = "LSTxxxnJzKDFSLr4dUkPcmCf5VyryEqzPLz5j4bpxFp"
        l_RequestURL = strPriceJupAPI.format(pInputMint)
        l_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(l_RequestURL, proxy=g_ProxyAddress) as response:
                if response.status == 200:
                    result = await response.json()
                    if pInputMint in result["data"]:
                        print(result["data"][pInputMint]["price"])
asyncio.run(main())