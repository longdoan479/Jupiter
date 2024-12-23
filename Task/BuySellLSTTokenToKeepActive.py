import asyncio
import os
import random
from datetime import datetime

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

from IncludeAsync.AccountSol import AccountSol
from Constant import TokenContract, strLoggingPath, gRandomTimeMax, gRandomTimeMin, TokenLSTContract, EnumStatusTask
from IncludeAsync.Dex.Jupiter import Jupiter
from IncludeAsync.ConnectSol import ConnectSol
from Logging import Logging
from IncludeAsync.Token import Token

class BuySellLstTokenToKeepActive(ConnectSol):
    def __init__(self, pClient: AsyncClient, pAccountSOL: AccountSol):
        super().__init__(pClient)
        self.mAccountSOL = pAccountSOL
        self.TotalDecision = 1

    async def DoTask(self):
        l_result = False
        # ------------ Get start Token ----------------
        l_StartToken = await self.GetStartToken()

        if l_StartToken == EnumStatusTask.OUT_OF_BALANCE:
            return l_StartToken
        elif l_StartToken is None:
            return None

        l_ListTokenLSTRandom = self.GetListTokenToDoTask(l_StartToken)

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(self.mClient)

        if l_StartToken == TokenContract.SOL:
            l_Balance = await self.mAccountSOL.GetBalanceSOL(True)
        else:
            l_LstToken = Token(self.mClient, Pubkey.from_string(l_StartToken))
            l_Balance = await l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

        l_CurrentToken = l_StartToken
        l_NextToken = random.choice(l_ListTokenLSTRandom)
        if l_Balance > 0:
            l_Timesleep = random.randint(5, 20)
            l_AmountToSwap = float(round(random.uniform(0.000000001, 0.00000001), 11))
            if l_CurrentToken == TokenContract.SOL:
                l_SwapLST, l_result = await l_Jupiter.swap(l_CurrentToken, l_NextToken, l_AmountToSwap, self.mAccountSOL)
            else:
                l_SwapLST, l_result = await l_Jupiter.swap(l_CurrentToken, l_NextToken, l_AmountToSwap, self.mAccountSOL)

            if l_result is True and l_SwapLST is not None:
                # --------------- Logging ---------------------------
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

        return l_result

    def GetListTokenToDoTask(self, pStartToken):
        l_lstToken = TokenLSTContract.getListToken()
        l_lstToken.append(TokenContract.SOL)
        l_lstToken.append(TokenContract.SOL)
        l_lstToken.append(TokenContract.SOL)
        l_lstToken.append(TokenContract.SOL)
        l_lstToken.append(TokenContract.SOL)
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

            if l_DictTokenBalance[l_ContractHasBalance] > 0.005:
                return l_ContractHasBalance
            else:
                return EnumStatusTask.OUT_OF_BALANCE

        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BuySellLstTokenWithPath.GetStartToken: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None



