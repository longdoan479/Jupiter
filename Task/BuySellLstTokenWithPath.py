import os
import random
import time
from datetime import datetime

from solana.rpc.api import Client
from solders.pubkey import Pubkey

from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, TokenContract, strLoggingPath, gRandomTimeMax, gRandomTimeMin, TokenLSTContract
from Dex.Jupiter import Jupiter
from Include.Logging import Logging
from Include.Token import Token
from Task.BuyRandomToken import BuyRandomToken


class BuySellLstTokenWithPath:
    def __init__(self, pAccountSOL: AccountSol, pAmountIn: float):
        self.mAccountSOL = pAccountSOL
        self.mAmountIn = pAmountIn
        self.TotalDecision = 1

    def DoTask(self) -> float:
        # -------------- define ----------------
        l_TotalVolumne = 0
        # -------------- Connect to solana ---------------
        l_ProxyAddress = "http://ilztorki-rotate:upiy4xb5ul1z@p.webshare.io:80"
        l_Client = Client(g_RPC_SOL, blockhash_cache=True, extra_headers={'proxy': l_ProxyAddress})

        # ------------ Get start Token ----------------
        l_StartToken = self.GetStartToken(l_Client)
        l_ListTokenLSTRandom = self.GetListTokenToDoTask(l_StartToken)

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(l_Client)

        if l_StartToken == TokenContract.SOL:
            l_Balance = self.mAccountSOL.GetBalanceSOL(True)
        else:
            l_LstToken = Token(l_Client, Pubkey.from_string(l_StartToken))
            l_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

        if l_Balance > 0:
            for i in range(0, len(l_ListTokenLSTRandom)):
                l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)

                if i == 0:
                    l_SwapLST = l_Jupiter.swap(l_StartToken, l_ListTokenLSTRandom[i], round(l_Balance/1.05, 3), self.mAccountSOL)
                    l_TotalVolumne += Jupiter.GetTokenPriceInUSD(l_StartToken, self.mAccountSOL) * l_Balance
                elif i == len(l_ListTokenLSTRandom)-1:
                    break
                else:
                    l_SwapLST = l_Jupiter.swap(l_ListTokenLSTRandom[i], l_ListTokenLSTRandom[i+1], l_Balance, self.mAccountSOL)
                    l_TotalVolumne += Jupiter.GetTokenPriceInUSD(l_ListTokenLSTRandom[i], self.mAccountSOL) * l_Balance

                time.sleep(l_Timesleep)

                if l_ListTokenLSTRandom[i] == TokenContract.SOL:
                    l_Balance = self.mAccountSOL.GetBalanceSOL(True)
                else:
                    l_LstToken = Token(l_Client, Pubkey.from_string(l_ListTokenLSTRandom[i]))
                    l_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

                if l_Balance > 0 and l_ListTokenLSTRandom[i] != TokenContract.SOL:
                    # --------------- Logging ---------------------------
                    l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
                    l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to TokenLST on Jupiter \n => {l_SwapLST}'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                    # ------------------------------------------

                elif l_Balance > 0.1 and l_ListTokenLSTRandom[i] == TokenContract.SOL:
                    # --------------- Logging ---------------------------
                    l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
                    l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to TokenLST on Jupiter \n => {l_SwapLST}'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                else:
                    # --------------- Logging ---------------------------
                    l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
                    l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Not found balance after swap with txn: \n => {l_SwapLST}'
                    Logging.WriteLog(l_FilePath, l_TextToLog)
                    # ------------------------------------------
                    break

                time.sleep(l_Timesleep)

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

    def GetStartToken(self, pClient):
        l_FilePath = os.getcwd() + strLoggingPath.format(
            str(self.mAccountSOL.mGroup) + "_" + str(self.mAccountSOL.GetPublicKey()))
        try:
            l_lstToken = TokenLSTContract.getListToken()
            l_lstToken.append(TokenContract.SOL)
            l_DictTokenBalance = {}
            for l_Token in l_lstToken:
                if l_Token == TokenContract.SOL:
                    l_Balance = self.mAccountSOL.GetBalanceSOL(True)
                else:
                    l_LstToken = Token(pClient, Pubkey.from_string(l_Token))
                    l_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
                time.sleep(0.5)
                l_DictTokenBalance[l_Token] = l_Balance

            l_ContractHasBalance = max(l_DictTokenBalance, key=l_DictTokenBalance.get)

            if l_DictTokenBalance[l_ContractHasBalance] > 0.01:
                return l_ContractHasBalance

        except Exception as e:
            l_TextToLog = f'\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BuySellLstTokenWithPath.GetStartToken: {type(e).__name__} - {e}\n\n'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return None



