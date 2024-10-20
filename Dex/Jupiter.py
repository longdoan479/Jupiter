import asyncio
import base64
import json
import os
import time
from datetime import datetime

import aiohttp
import solders.transaction
from solana.rpc.async_api import AsyncClient
import requests
from solana.rpc.types import TxOpts
from solders.message import to_bytes_versioned

from IncludeAsync.AccountSol import AccountSol
from IncludeAsync.ConnectSol import ConnectSol
from Constant import gDictTokenDecimal, g_ProxyAddress, strLoggingPath, strPriceJupAPI
from IncludeAsync.Transaction import Transactions

from Logging import Logging


class Jupiter(ConnectSol):
    def __init__(self, pClient: AsyncClient):
        super().__init__(pClient)

    async def swap(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountFrom: AccountSol):
        txHash = None
        l_result = False
        try:
            l_DataSwap = await self.GetDataSwap(pInputMint, pOutputMint, pAmountOriginal, pAccountFrom)

            raw_tx = solders.transaction.VersionedTransaction.from_bytes(base64.b64decode(l_DataSwap["swapTransaction"]))

            signature = pAccountFrom.GetkeyPairAccount().sign_message(to_bytes_versioned(raw_tx.message))
            signed_tx = solders.transaction.VersionedTransaction.populate(raw_tx.message, [signature])
            txHash = await self.mClient.send_raw_transaction(bytes(signed_tx), opts=TxOpts(skip_preflight=True, max_retries=10))
            lstSig = [txHash.value]

            await asyncio.sleep(30)

            l_Transaction = Transactions(self.mClient)
            l_result = await l_Transaction.WaitForTransaction(lstSig, 600, 10)

        except Exception as e:
            l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountFrom.GetPublicKey()))
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Exception Swap Function: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return txHash, l_result

    async def GetDataSwap(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountSol: AccountSol):

        while 1:
            try:
                http_proxy = {
                    "http": g_ProxyAddress,
                    "https": g_ProxyAddress
                }
                l_quote = await self.GetDataQuote(pInputMint, pOutputMint, pAmountOriginal, pAccountSol)
                l_URL = "https://quote-api.jup.ag/v6/swap"
                l_Data = json.dumps({
                    "quoteResponse": l_quote,
                    "userPublicKey": str(pAccountSol.GetPublicKey()),
                    'prioritizationFeeLamports': {"priorityLevelWithMaxLamports": {"priorityLevel": "veryHigh", "maxLamports": 1000000, "global": False}},
                    'dynamicComputeUnitLimit': True,
                    'asLegacyTransaction': False,
                    'allowOptimizedWrappedSolTokenAccount': True,
                    'dynamicSlippage': {'maxBps': 20}
                })

                l_headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
                l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountSol.GetPublicKey()))
                async with aiohttp.ClientSession() as session:
                    async with session.post(l_URL, data=l_Data, proxy=g_ProxyAddress, headers=l_headers) as response:
                        if response.status == 200:
                            l_result = await response.json()
                            return l_result
                        else:
                            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetDataSwap response.status_code: {str(response.status)}\n' \
                                          f'{l_Data}\n\n'
                            Logging.WriteLog(l_FilePath, l_TextToLog)
            except Exception as e:
                l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountSol.GetPublicKey()))
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetDataSwap: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
            await asyncio.sleep(60)


    async def GetDataQuote(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountSol: AccountSol):
        l_DecimalToken = gDictTokenDecimal[pInputMint]['Decimal']
        pAmountLamport = pAmountOriginal * 10**l_DecimalToken

        l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountSol.GetPublicKey()))
        while 1:
            url = f"https://quote-api.jup.ag/v6/quote?" \
                  f"inputMint={pInputMint}" \
                  f"&outputMint={pOutputMint}" \
                  f"&amount={int(pAmountLamport)}" \
                  f"&autoSlippage=true" \
                  f"&swapMode=ExactIn" \
                  f"&onlyDirectRoutes=false" \
                  f"&autoSlippageCollisionUsdValue=1000" \
                  f"&minimizeSlippage=false" \
                  f"&asLegacyTransaction=false" \
                  f"&maxAccounts=64" \
                  f"&maxAutoSlippageBps=15"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, proxy=g_ProxyAddress) as response:
                        if response.status == 200:
                            result = await response.json()
                            if int(result["slippageBps"]) <= 15:
                                return result
                            else:
                                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetDataQuote result["slippageBps"]: {str(result["slippageBps"])}\n' \
                                              f'{url}\n\n'
                                Logging.WriteLog(l_FilePath, l_TextToLog)
                        else:
                            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetDataQuote response.status_code: {str(response.status)}\n' \
                                          f'{url}\n\n'
                            Logging.WriteLog(l_FilePath, l_TextToLog)

            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetDataQuote: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
            await asyncio.sleep(10)

    @staticmethod
    async def GetTokenPriceInUSD(pInputMint: str, pAccountSol: AccountSol) -> float:
        l_RequestURL = strPriceJupAPI.format(pInputMint)

        l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountSol.GetPublicKey()))
        l_RetryTime = 0

        l_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36'
        }
        while l_RetryTime < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(l_RequestURL, proxy=g_ProxyAddress, headers=l_headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            if pInputMint in result["data"]:
                                return result["data"][pInputMint]["price"]
                        else:
                            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetTokenPriceInUSD: response.status_code: {str(response.status)}\n\n'
                            Logging.WriteLog(l_FilePath, l_TextToLog)
                            l_RetryTime = l_RetryTime + 1
            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetTokenPriceInUSD: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                l_RetryTime = l_RetryTime + 1

            await asyncio.sleep(30)
        return 0
