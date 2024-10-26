import asyncio
import os
import random
from datetime import datetime

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

from IncludeAsync.AccountSol import AccountSol
from Constant import TokenContract, strLoggingPath, gRandomTimeMax, gRandomTimeMin, TokenLSTContract
from Dex.Jupiter import Jupiter
from IncludeAsync.ConnectSol import ConnectSol
from Logging import Logging
from IncludeAsync.Token import Token


class BuySellLstTokenWithPath(ConnectSol):
    def __init__(self, pClient: AsyncClient, pAccountSOL: AccountSol):
        super().__init__(pClient)
        self.mAccountSOL = pAccountSOL
        self.TotalDecision = 1

    async def DoTask(self) -> float:
        # -------------- define ----------------
        l_TotalVolumne = 0

        # ------------ Get start Token ----------------
        l_StartToken = await self.GetStartToken()
        l_ListTokenLSTRandom = self.GetListTokenToDoTask(l_StartToken)

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(self.mClient)

        if l_StartToken == TokenContract.SOL:
            l_Balance = await self.mAccountSOL.GetBalanceSOL(True)
        else:
            l_LstToken = Token(self.mClient, Pubkey.from_string(l_StartToken))
            l_Balance = await l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

        l_CurrentToken = l_StartToken
        l_NextToken = l_ListTokenLSTRandom[0]
        if l_Balance > 0:
            l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)

            if l_CurrentToken == TokenContract.SOL:
                l_SwapLST, l_result = await l_Jupiter.swap(l_CurrentToken, l_NextToken, round(l_Balance/1.1, 3), self.mAccountSOL)
            else:
                l_SwapLST, l_result = await l_Jupiter.swap(l_CurrentToken, l_NextToken, l_Balance, self.mAccountSOL)

            if l_result is True and l_SwapLST is not None:
                # --------------- Logging ---------------------------
                l_TotalVolumne += await Jupiter.GetTokenPriceInUSD(l_CurrentToken, self.mAccountSOL) * l_Balance

                l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
                l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to TokenLST on Jupiter \n => {l_SwapLST.value}'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                # ------------------------------------------
            else:
                # --------------- Logging ---------------------------
                l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
                l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to TokenLST on Jupiter Failed'
                Logging.WriteLog(l_FilePath, l_TextToLog)
            await asyncio.sleep(l_Timesleep)

        return l_TotalVolumne

    def GetListTokenToDoTask(self, pStartToken):
        l_lstToken = TokenLSTContract.getListToken()
        l_lstToken.append(TokenContract.SOL)

        l_lstToken = [l_Contract for l_Contract in l_lstToken if l_Contract != pStartToken]
        random.shuffle(l_lstToken)

        l_RandomNumOfLST = random.randint(4, int(len(l_lstToken) - 1))

        # --------------- Logging ---------------------------
        l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Execute {l_RandomNumOfLST+1} transaction'
        Logging.WriteLog(l_FilePath, l_TextToLog)
        # ------------------------------------------

        return l_lstToken[0:l_RandomNumOfLST]

    async def GetStartToken(self):
        l_FilePath = os.getcwd() + strLoggingPath.format(
            str(self.mAccountSOL.mGroup) + "_" + str(self.mAccountSOL.GetPublicKey()))
        try:
            l_lstToken = TokenLSTContract.getListToken()
            l_lstToken.append(TokenContract.SOL)
            l_DictTokenBalance = {}
            for l_Token in l_lstToken:
                if l_Token == TokenContract.SOL:
                    l_Balance = await self.mAccountSOL.GetBalanceSOL(True)
                else:
                    l_LstToken = Token(self.mClient, Pubkey.from_string(l_Token))
                    l_Balance = await l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
                await asyncio.sleep(0.5)
                l_DictTokenBalance[l_Token] = l_Balance

            l_ContractHasBalance = max(l_DictTokenBalance, key=l_DictTokenBalance.get)

            if l_DictTokenBalance[l_ContractHasBalance] > 0.01:
                return l_ContractHasBalance

        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BuySellLstTokenWithPath.GetStartToken: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None



