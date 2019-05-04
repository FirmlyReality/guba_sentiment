import pandas as pd
import numpy as np

inputdir = "../res_data1"

sbsi = pd.read_csv(inputdir+"/HS300_MsgBSI.csv")
gbsi = pd.read_csv(inputdir+"/g_MsgBSI.csv")

prebsi = 0.8*np.array(sbsi['preMsgBSI']) + 0.2*np.array(gbsi['g_preMsgBSI'])
intbsi = 0.8*np.array(sbsi['intMsgBSI']) + 0.2*np.array(gbsi['g_intMsgBSI'])
preallbsi = 0.8*np.array(sbsi['preallMsgBSI']) + 0.2*np.array(gbsi['g_preallMsgBSI'])

print(np.percentile(prebsi,[33.3,66.7]))
print(np.percentile(intbsi,[33.3,66.7]))
print(np.percentile(preallbsi,[33.3,66.7]))

print(np.mean(prebsi))
print(np.std(prebsi,ddof=1))

print(np.mean(intbsi))
print(np.std(intbsi,ddof=1))

print(np.mean(preallbsi))
print(np.std(preallbsi,ddof=1))