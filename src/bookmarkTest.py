import bookmark
import numpy as np

arr = list(np.array([[255,255,255],[128,254,255],[0,0,0]],dtype = np.uint8).ravel())
#ar = np.array([[255,255,255],[128,254,255],[0,0,0]],dtype = np.uint8)
#arr = np.array([128,254,255],dtype = np.uint8)
#shape = arr.shape
#print(arr,shape,arr.dtype)

#print(str(arr.tobytes()))
#print(arr.tolist())
#b = str()
#np.savetxt(b,arr)
#print(b)

bk = bookmark.bookmark()
'''
print(bk.read("D:/zeeshan work/fyp gui/Exero/exero/new sample bookmark.txt"))

bk.write("D:/zeeshan work/fyp gui/Exero/exero/new sample bookmark.txt",0.009,"sample image data",str(arr))

print(bk.read("D:/zeeshan work/fyp gui/Exero/exero/new sample bookmark.txt"))

x = bk.read("D:/zeeshan work/fyp gui/Exero/exero/new sample bookmark.txt")[2][2]
#print("x[2:-2]",x)
#b = bytes(x[2:-2],encoding = 'UTF-8')
#print(b,len(b))
#print(np.frombuffer(b,dtype=np.uint8))

#print(np.frombuffer(arr.tobytes(),dtype=np.uint8))
'''
x = bk.read("D:/zeeshan work/fyp gui/Exero/exero/new sample bookmark.txt")[2][2][1:-2]
print(x,len(x.split(", ")))
#recovered = np.array(x.split(", "),dtype = np.uint8).reshape((3,3))
#print(recovered,type(recovered),recovered.dtype,recovered.shape)

#print(recovered.astype(np.uint8))
#print(list(b))
#v = str(list(ar.ravel()))
#print(v,type(v))
#v = v[1:-1].split(", ")
#va = np.array(v)
#print(va,va.shape,va.dtype)
