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

from Logging import Logging


class Jupiter(ConnectSol):
    def __init__(self, pClient: AsyncClient):
        super().__init__(pClient)

    async def swap(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountFrom: AccountSol):

        signature_statuses = None
        txHash = None
        l_GetSignatureStatus = None
        l_Retry = 0
        while l_Retry < 2:
            try:
                l_DataSwap = await self.GetDataSwap(pInputMint, pOutputMint, pAmountOriginal, pAccountFrom)

                # transaction = Transaction.deserialize(instruction)
                raw_tx = solders.transaction.VersionedTransaction.from_bytes(base64.b64decode(l_DataSwap["swapTransaction"]))

                signature = pAccountFrom.GetkeyPairAccount().sign_message(to_bytes_versioned(raw_tx.message))
                signed_tx = solders.transaction.VersionedTransaction.populate(raw_tx.message, [signature])
                txHash = await self.mClient.send_raw_transaction(bytes(signed_tx), opts=TxOpts(skip_preflight=True, max_retries=10))
                # print(str(txHash.value))
                lstSig = [txHash.value]

                await asyncio.sleep(10)

                confirmed = False
                l_Count = 0
                while not confirmed:
                    l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountFrom.GetPublicKey()))

                    try:
                        l_GetSignatureStatus = (await self.mClient.get_signature_statuses(lstSig))
                        if l_GetSignatureStatus.value[0] is not None:
                            signature_confirm_statuses = l_GetSignatureStatus.value[0].confirmation_status
                            signature_statuses = l_GetSignatureStatus.value[0].status
                            if signature_confirm_statuses == solders.transaction_status.TransactionConfirmationStatus.Finalized:
                                confirmed = True
                                break
                        l_Count = l_Count + 1
                        if l_Count >= 24:
                            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Resend Txn'
                            Logging.WriteLog(l_FilePath, l_TextToLog)
                            print("Resend txhash 1")
                            break
                    except Exception as e:
                        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Exception Swap Function: {type(e).__name__} - {e}'
                        Logging.WriteLog(l_FilePath, l_TextToLog)
                    await asyncio.sleep(5) # Chờ 5 giây trước khi kiểm tra lại

                if isinstance(signature_statuses, type(None)) and l_GetSignatureStatus.value[0] is not None:
                    break
                elif l_Count >= 24:
                    l_Retry += 1
            except Exception as e:
                l_FilePath = os.getcwd() + strLoggingPath.format(str(pAccountFrom.GetPublicKey()))
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Exception Swap Function: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
            await asyncio.sleep(60)

        return str(txHash.value)

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
        while 1:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(l_RequestURL, proxy=g_ProxyAddress) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["data"][pInputMint]["price"]
                        else:
                            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetTokenPriceInUSD: response.status_code: {str(response.status)}\n\n'
                            Logging.WriteLog(l_FilePath, l_TextToLog)

            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GetTokenPriceInUSD: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
            await asyncio.sleep(60)
