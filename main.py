import os
import random

from solana.rpc.api import Client

from Include.AccountSol import AccountSol
from Include.FileProcessing import FileProcessing
from Task.BuySellSolUsdc import BuySellSolUsdc
import Include.Constant as Cons


# # ------------------ Run multi acc ----------------------
from ThreadTask.ThreadDoTask import ThreadDoTask

l_FileKey = FileProcessing("key.xlsx")
l_lstAccount = l_FileKey.ReadDataWallet()

l_FileProxy = FileProcessing("proxy.xlsx")
Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()

l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup

l_lstAccountRandom = []
for i in range(1, l_MaxGroup+1):
    l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == i, l_lstAccount))
    for j in range(0, Cons.g_Account_Number_Each_Group):
        l_RandomIndexAccount = random.randint(0, int(len(l_lstAccountFilter) - 1))
        if l_lstAccountFilter[l_RandomIndexAccount] not in l_lstAccountRandom:
            l_FilePath = os.getcwd() + Cons.strLoggingPath.format(l_lstAccountFilter[l_RandomIndexAccount].mGroup, l_lstAccountFilter[l_RandomIndexAccount].mAddress)
            if os.path.exists(l_FilePath) is False:
                l_lstAccountRandom.append(l_lstAccountFilter[l_RandomIndexAccount])

groups_Account = {}
# Nhóm dữ liệu theo giá trị group
for acc in l_lstAccountRandom:
    group = acc.mGroup
    if group not in groups_Account:
        groups_Account[group] = []
    groups_Account[group].append(acc)

# Chia các nhóm thành 5 mảng
l_Results = [[] for _ in range(5)]
group_list = list(groups_Account.values())

for i, group in enumerate(group_list):
    l_Results[i % 5].extend(group)

print()

thread1 = ThreadDoTask("Thread 1", l_Results[0])
thread2 = ThreadDoTask("Thread 2", l_Results[1])
thread3 = ThreadDoTask("Thread 3", l_Results[2])
thread4 = ThreadDoTask("Thread 4", l_Results[3])
thread5 = ThreadDoTask("Thread 5", l_Results[4])

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()


thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()

