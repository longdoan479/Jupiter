import os
import random


from Include.FileProcessing import FileProcessing
import Include.Constant as Cons
from ThreadTask.ThreadDoTask import ThreadDoTask


# # ------------------ Run multi acc ----------------------

l_FileKey = FileProcessing("key.xlsx")
l_lstAccount = l_FileKey.ReadDataWallet()

l_FileProxy = FileProcessing("proxy.xlsx")
Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()


l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup

l_lstAccountRandom = []
groups_Account = {}

for i in range(1, l_MaxGroup+1):
    group = i

    l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == group, l_lstAccount))

    # Nhóm dữ liệu theo giá trị group
    if group not in groups_Account:
        groups_Account[group] = []

    random.shuffle(l_lstAccountFilter)
    groups_Account[group].extend(l_lstAccountFilter)


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

