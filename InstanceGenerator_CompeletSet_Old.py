import time
import random # Random Module
import pickle # Pickling Module
from itertools import product # Using cartesian product of sell set and buy set
from itertools import combinations # For obtaining a complete subset of a sell/buy set

NumberOfCarrier = int(input('How many carriers in this instance? :'))
Set_CarrierIndex = set(range(1, NumberOfCarrier + 1))  # Create a set of carrier Index

NumberOfRequest = int(input('How many requests in this instance? :'))  # Create a set of carrier Index
Set_RequestIndex = set(range(1, NumberOfRequest + 1))  # Create a set of request Index

def BidPriceGenerator_RequestPriceBased(BuyList,SellList,RequestPriceDict):
    BuyRequestSum = 0
    SellRequestSum = 0
    for EachRequest in SellList:
        SellRequestSum = SellRequestSum + RequestPriceDict[EachRequest]
    for EachRequest in BuyList:
        BuyRequestSum = BuyRequestSum + RequestPriceDict[EachRequest]
    if(len(BuyList)!=0):
       BuyRequestSum = BuyRequestSum*random.uniform(1, 1+(len(BuyList)-1)/(2*len(BuyList)))
    else:
       pass
    TotalBidPrice = (BuyRequestSum + SellRequestSum)
    return TotalBidPrice
def CompleteRandomPrice():
     return random.randint(-50,100)

def RequestPriceGenerator(Set_RequestIndex):
    RequestPriceDict = {}
    for EachRequest in Set_RequestIndex:
        RequestPriceDict['R'+str(EachRequest)] = random.randint(-50,-1)
    for EachRequest in Set_RequestIndex:
        RequestPriceDict['r'+str(EachRequest)] = random.randint(1,100)
    return RequestPriceDict


Start_time = time.time ()
Carrier_Request_Dict = {}  # Create a dictionary to indicate each carrier and their owned request

RequestPriceDict = RequestPriceGenerator(Set_RequestIndex)

for m in Set_CarrierIndex:
    Carrier_Request_Dict[m] = [[],
                               []]  # Attribute each carrier two void list, first one is for the owned requests, second one is for the possible requests

for r in Set_RequestIndex:  # Allocate each request to a arbitrary carrier
    CarrierIndex = random.randint(1, NumberOfCarrier)
    Carrier_Request_Dict[CarrierIndex][0].append(r)

for k in Set_CarrierIndex:
    Carrier_Request_Dict[k][1] = [x for x in Set_RequestIndex if x not in Carrier_Request_Dict[k][0]]

for k in Carrier_Request_Dict:  # Give all sell requests to a string with a 'R' prefix
    NewNameSellRequestList = []
    for x in Carrier_Request_Dict[k][0]:
        NewNameSellRequestList.append('R' + str(x))
    Carrier_Request_Dict[k][0] = NewNameSellRequestList

for k in Carrier_Request_Dict:  # Give all buy requests to a string with a 'r' prefix
    NewNameBuyRequestList = []
    for x in Carrier_Request_Dict[k][1]:
        NewNameBuyRequestList.append('r' + str(x))
    Carrier_Request_Dict[k][1] = NewNameBuyRequestList

BidCollection = {}  # Make a void dict to store all bid structure

for k in Set_CarrierIndex:

    sell_subset = []  # Create a complete set of sell combination
    for i in range(0, len(Carrier_Request_Dict[k][0]) + 1):
        for sell_subset_element in combinations(Carrier_Request_Dict[k][0], i):
            sell_subset.append(sell_subset_element)
    '''print('the sell subset of carrier', k, ':', sell_subset)'''

    buy_subset = []  # Create a complete set of buy combination
    for i in range(0, len(Carrier_Request_Dict[k][1]) + 1):
        for buy_subset_element in combinations(Carrier_Request_Dict[k][1], i):
            buy_subset.append(buy_subset_element)
    '''print('the buy subset of carrier', k, ':', buy_subset)'''

    Request_Exchange_Proposal_List = [p for p in
                                      product(buy_subset,
                                              sell_subset)]  # Cartesian product of sell_subset and buy_subset
    del Request_Exchange_Proposal_List[0]  # delete the [(),()] element which means buys nothing and offer nothing
    '''print('the request exchange offer of carrier', k, ':', Request_Exchange_Proposal_List)'''

    for BidCounterInEachCarrier in range(1,2**(len(Carrier_Request_Dict[k][0])+len(Carrier_Request_Dict[k][1]))):
        #BidCollection[(k, BidCounterInEachCarrier)] = (k, set(Request_Exchange_Proposal_List[BidCounterInEachCarrier-1][0] + Request_Exchange_Proposal_List[BidCounterInEachCarrier-1][1]) ,round(random.normalvariate(100, 40)))
        BidCollection[(k-1)*(2**(len(Carrier_Request_Dict[k][0])+len(Carrier_Request_Dict[k][1]))-1)+BidCounterInEachCarrier] = [k,set(Request_Exchange_Proposal_List[BidCounterInEachCarrier-1][0] + Request_Exchange_Proposal_List[BidCounterInEachCarrier-1][1]), BidPriceGenerator_RequestPriceBased(Carrier_Request_Dict[k][0],Carrier_Request_Dict[k][0],RequestPriceDict)]

# Create a data file for Lagrangian approach
output = open('CK_5_10_003.pkl', 'wb')
pickle.dump(NumberOfCarrier, output)
pickle.dump(NumberOfRequest, output)
pickle.dump(BidCollection, output)
output.close()

# Create a data file for Gurobi solver
Bid_MIP, Carriers_MIP, Requests_MIP =[], [], []
Carrier_sell_MIP, Carrier_buy_MIP, Bid_request_MIP, Bid_Price_MIP = {},{},{},{}

# Create Bid list
for x in range(1,NumberOfCarrier*(2**NumberOfRequest-1)+1):
    Bid_MIP.append('B'+str(x))
'''print (Bid_MIP)'''

# Create Carriers list
for x in Set_CarrierIndex:
    Carriers_MIP.append('C'+str(x))
'''print (Carriers_MIP)'''

# Create Requests list
for x in Set_RequestIndex:
    Requests_MIP.append(str(x))
'''print (Requests_MIP)'''

# Create Carrier_sell dict
for k in Set_CarrierIndex:
    for r in Set_RequestIndex:
        if 'R' + str(r) in Carrier_Request_Dict[k][0]:
            Carrier_sell_MIP[('C'+str(k), str(r))] = 1
        else:
            Carrier_sell_MIP[('C'+str(k), str(r))] = 0
'''print (Carrier_sell_MIP)'''

# Create Carrier_buy dict
for k in Set_CarrierIndex:
    for r in Set_RequestIndex:
        if 'r' + str(r) in Carrier_Request_Dict[k][1]:
            Carrier_buy_MIP[('C'+str(k), str(r))] = 1
        else:
            Carrier_buy_MIP[('C'+str(k), str(r))] = 0
'''print (Carrier_buy_MIP)'''

# Create Bid_request dict
for k in Set_CarrierIndex:
    for b in range (1,NumberOfCarrier*(2**NumberOfRequest-1)+1):
        for r in Set_RequestIndex:
            if BidCollection[b][0]==k and ('R' + str(r) in BidCollection[b][1] or 'r' + str(r) in BidCollection[b][1]):
                Bid_request_MIP[('C'+str(k), 'B'+str(b) ,str(r))] = 1
            else:
                Bid_request_MIP[('C'+str(k), 'B'+str(b) ,str(r))] = 0
'''print (Bid_request_MIP)'''

# Create Bid_Price dict
for x in range (1,NumberOfCarrier*(2**NumberOfRequest-1)+1):
    Bid_Price_MIP['B'+str(x)] = BidCollection[x][2]
'''print (Bid_Price_MIP)'''

def Create_MIP_DataFile():
    output = open('CK_5_10_003_MIP.pkl', 'wb')
    pickle.dump(Bid_MIP, output)
    pickle.dump(Carriers_MIP, output)
    pickle.dump(Requests_MIP, output)
    pickle.dump(Carrier_sell_MIP, output)
    pickle.dump(Carrier_buy_MIP, output)
    pickle.dump(Bid_request_MIP, output)
    pickle.dump(Bid_Price_MIP, output)
    output.close()

Create_MIP_DataFile()

# Calculate running time of the program
End_time = time.time ()
print ('Total running time:',End_time - Start_time )