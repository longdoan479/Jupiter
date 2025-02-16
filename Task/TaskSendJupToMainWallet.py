import asyncio
import os
from datetime import datetime

from solders.pubkey import Pubkey

from Constant import strLoggingPath, TokenAltContract, gDictTokenDecimal, EnumStatusTask
from Include.AccountSol import AccountSol
from IncludeAsync.ConnectSol import ConnectSol
from IncludeAsync.Token import Token
from IncludeAsync.Transaction import Transactions
from Logging import Logging


class TaskSendJupToMainWallet(ConnectSol):
    def __init__(self, pClient, pAccountSOL: AccountSol):
        super().__init__(pClient)
        self.mAccountSOL = pAccountSOL

    async def DoTask(self):
        l_result = None
        l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))

        l_AddressMainWallet = Pubkey.from_string("69DjMYsQNr9PS5xpRddKbPCNo21ZyaQ1QnTmYiv8A5r3")
        try:
            l_JupToken = Token(self.mClient, TokenAltContract.JUP)

            l_AmountJUP = await l_JupToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

            if l_AmountJUP > 0:
                l_AmountJUP_Lamport = int(l_AmountJUP * 10**gDictTokenDecimal[TokenAltContract.JUP]['Decimal'])
                l_txnHash = await l_JupToken.Transfer(self.mAccountSOL, l_AddressMainWallet, l_AmountJUP_Lamport)

                l_Transaction = Transactions(self.mClient)
                lstSig = [l_txnHash]
                await asyncio.sleep(10)
                l_StatusTxn = await l_Transaction.WaitForTransaction(lstSig, 200, 10)

                if l_StatusTxn:
                    l_result = EnumStatusTask.SUCCESS
                else:
                    l_result = EnumStatusTask.FAILED
            else:
                l_result = EnumStatusTask.OUT_OF_BALANCE
        except Exception as e:
            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: TaskSendJupToMainWallet: {type(e).__name__} - {e}'
            Logging.WriteLog(l_FilePath, l_TextToLog)
        return l_result
