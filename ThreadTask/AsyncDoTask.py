import asyncio
import os
import random
import time
import traceback
from datetime import datetime
from typing import List

import httpx

from Helper import GetRandomRPC
from Logging import Logging
from solana.rpc.async_api import AsyncClient

from Constant import gRandomTimeMax, gRandomTimeMin, g_ProxyAddress, gTotalVolEachAccount, strLoggingPath
from Data import DataWallet
from IncludeAsync.AccountSol import AccountSol
from Task.BuySellLstTokenWithPath import BuySellLstTokenWithPath
from solders.pubkey import Pubkey


class AsyncDoTask:
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount
        self.mDictAccVol = {}

    async def run(self):
        random.shuffle(self.mListAccount)
        await self.SwapJupiter()
        # await self.SendSol()

    async def SwapJupiter(self):
        l_NumOfAccReachTarget = 0
        http_proxy = {
            "http://": g_ProxyAddress,
            "https://": g_ProxyAddress
        }
        while l_NumOfAccReachTarget < len(self.mListAccount):  # if tổng số acc đạt target < len(self.mListAccount) => chạy tiếp
            for l_Account in self.mListAccount:
                l_RandomRPC = GetRandomRPC()

                # Create a custom aiohttp session with proxy settings

                l_FilePath = os.getcwd() + strLoggingPath.format(
                    str(l_Account.mGroup) + "_" + str(l_Account.mAddress))
                try:
                    async with httpx.AsyncClient(timeout=60000, proxies=http_proxy) as session:
                        async with AsyncClient(l_RandomRPC) as l_sol_web3:
                            l_sol_web3._provider.session = session
                            lAccSol = AccountSol(l_Account.mPrivateKey, l_sol_web3, l_Account.mGroup)
                            if str(lAccSol.GetPublicKey()) not in self.mDictAccVol:
                                self.mDictAccVol[str(lAccSol.GetPublicKey())] = 0
                            else:
                                # if Total Vol hiện tại đã vượt mức, chạy ví tiếp theo
                                if self.mDictAccVol[str(lAccSol.GetPublicKey())] > gTotalVolEachAccount:
                                    continue

                            print(f"\n{self.mThreadName}: Account {l_Account.mAddress} is running")

                            l_Task = BuySellLstTokenWithPath(l_sol_web3, lAccSol)
                            l_TotalVolumn = await l_Task.DoTask()

                            self.mDictAccVol[str(lAccSol.GetPublicKey())] += l_TotalVolumn
                            if self.mDictAccVol[str(lAccSol.GetPublicKey())] > gTotalVolEachAccount:
                                l_NumOfAccReachTarget += 1

                            # ================== Logging =========================
                            l_FilePath = os.getcwd() + strLoggingPath.format(str(lAccSol.GetPublicKey()))
                            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ' \
                                          f'Total Volumn account {lAccSol.GetPublicKey()}: ' \
                                          f'{self.mDictAccVol[str(lAccSol.GetPublicKey())]} usd'
                            Logging.WriteLog(l_FilePath, l_TextToLog)
                            # ===========================================
                except Exception as e:
                    l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: SwapJupiter: {type(e).__name__} - {e}\n\n'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                    print(f"{self.mThreadName}: =>")
                    traceback.print_exc()

            random.shuffle(self.mListAccount)
            l_Sleep = random.randint(gRandomTimeMin, gRandomTimeMax)
            print(f"\n{self.mThreadName}: Sleeping {l_Sleep}s before new round")
            await asyncio.sleep(l_Sleep)

    async def SendSol(self):
        http_proxy = {
            "http://": g_ProxyAddress,
            "https://": g_ProxyAddress
        }
        for l_Account in self.mListAccount:
            l_RandomRPC = GetRandomRPC()

            # Create a custom aiohttp session with proxy settings
            print(f"{self.mThreadName}: => {l_Account.mAddress} \n")
            l_FilePath = os.getcwd() + strLoggingPath.format(
                str(l_Account.mGroup) + "_" + str(l_Account.mAddress))
            try:
                async with httpx.AsyncClient(timeout=60000, proxies=http_proxy) as session:
                    async with AsyncClient(l_RandomRPC) as l_sol_web3:
                        l_sol_web3._provider.session = session
                        lAccSol = AccountSol(l_Account.mPrivateKey, l_sol_web3, l_Account.mGroup)

                        await lAccSol.TransferSOL(Pubkey.from_string("DyMT47Z9xPEC6Fgy5FAFA7GmTfZnXbcNdv9aVmW5aehr"), 0.00001)
                        await asyncio.sleep(0.1)
            except Exception as e:
                l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: SendSol: {type(e).__name__} - {e}\n\n'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                print(f"{self.mThreadName}: =>")
                traceback.print_exc()

