import base64
import json
import os
import time
from datetime import datetime

import solders.transaction
from solana.rpc.api import Client
import requests
from solana.rpc.types import TxOpts, TokenAccountOpts
from solders.hash import Hash
from solders.message import MessageV0, to_bytes_versioned

from solders.pubkey import Pubkey

from Include.AccountSol import AccountSol
from Include.ConnectSol import ConnectSol
from Include.Constant import TokenContract, gDictTokenDecimal
from solana.transaction import Transaction
import Include.Constant as Cons

from Include.Logging import Logging


class Jupiter(ConnectSol):
    def __init__(self, pClient: Client):
        super().__init__(pClient)

    def swap(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountFrom: AccountSol):

        signature_statuses = None
        txHash = None
        l_GetSignatureStatus = None
        while 1:
            l_DataSwap = self.GetDataSwap(pInputMint, pOutputMint, pAmountOriginal, pAccountFrom)


            instruction = base64.b64decode(l_DataSwap)

            # transaction = Transaction.deserialize(instruction)
            raw_tx = solders.transaction.VersionedTransaction.from_bytes(base64.b64decode(l_DataSwap))

            signature = pAccountFrom.GetkeyPairAccount().sign_message(to_bytes_versioned(raw_tx.message))
            signed_tx = solders.transaction.VersionedTransaction.populate(raw_tx.message, [signature])

            txHash = self.mClient.send_raw_transaction(bytes(signed_tx), opts=TxOpts(skip_preflight=True, max_retries=10))
            # print(str(txHash.value))
            lstSig = [txHash.value]
            confirmed = False
            l_Count = 0
            while not confirmed:
                try:
                    l_GetSignatureStatus = self.mClient.get_signature_statuses(lstSig).value[0]
                    if l_GetSignatureStatus is not None:
                        signature_confirm_statuses = l_GetSignatureStatus.confirmation_status
                        signature_statuses = l_GetSignatureStatus.status
                        if signature_confirm_statuses == solders.transaction_status.TransactionConfirmationStatus.Finalized:
                            confirmed = True
                            break
                    l_Count = l_Count + 1
                    if l_Count >= 24:
                        l_FilePath = os.getcwd() + Cons.strLoggingPath.format(pAccountFrom.mGroup, str(pAccountFrom.GetPublicKey()))
                        print(l_FilePath)
                        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Resend Txn'
                        Logging.WriteLog(l_FilePath, l_TextToLog)
                        print("Resend txhash 1")
                        break
                except:
                    pass
                time.sleep(5)  # Chờ 5 giây trước khi kiểm tra lại
            if isinstance(signature_statuses, type(None)) and l_GetSignatureStatus is not None:
                break

        return str(txHash.value)

    def GetDataSwap(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountSol: AccountSol):

        l_ProxyAddress = Cons.g_Data_Proxy[1] if pAccountSol.mGroup not in Cons.g_Data_Proxy else Cons.g_Data_Proxy[pAccountSol.mGroup]

        http_proxy = {
            "http": l_ProxyAddress,
            "https": l_ProxyAddress
        }
        l_quote = self.GetDataQuote(pInputMint, pOutputMint, pAmountOriginal, pAccountSol)
        l_URL = "https://quote-api.jup.ag/v6/swap"
        l_Data = json.dumps({
            "quoteResponse": l_quote,
            "userPublicKey": str(pAccountSol.GetPublicKey()),
            'prioritizationFeeLamports': {"priorityLevelWithMaxLamports": {"priorityLevel": "high", "maxLamports": 500000}},
            'dynamicComputeUnitLimit': True,
            'asLegacyTransaction': False
        })

        l_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        l_response = requests.post(l_URL, data=l_Data, headers=l_headers, proxies=http_proxy).json()
        return l_response["swapTransaction"]

    def GetDataQuote(self, pInputMint: str, pOutputMint: str, pAmountOriginal: float, pAccountSol: AccountSol):
        l_DecimalToken = gDictTokenDecimal[pInputMint]['Decimal']
        pAmountLamport = pAmountOriginal * 10**l_DecimalToken

        l_ProxyAddress = Cons.g_Data_Proxy[1] if pAccountSol.mGroup not in Cons.g_Data_Proxy else Cons.g_Data_Proxy[pAccountSol.mGroup]
        http_proxy = {
            "http": l_ProxyAddress,
            "https": l_ProxyAddress
        }
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
            response = requests.get(url, proxies=http_proxy).json()
            if int(response["slippageBps"]) <= 15:
                return response

