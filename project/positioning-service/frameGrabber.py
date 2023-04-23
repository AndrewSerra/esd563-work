import cv2
import numpy as np
import time
import mmap
import struct
import sys, random
import ctypes
import copy

class ImageFeedthrough(object):
  def __init__(self):
    self.lib = ctypes.cdll.LoadLibrary('/fusion2/imageFeedthroughDriver.so')
    result = self.lib.init()
    self.frame= np.ones((480,752,8), dtype=np.uint8)
    
  def getStereoRGB(self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,0:3],self.frame[:,:,4:7]

  def getStereoGray (self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,3],self.frame[:,:,7]
    
  def getStereoAll (self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,0:4],self.frame[:,:,4:8]
 
  def __del__(self):
    result = self.lib.destroy
    
class ImageProcessing(object):
  def __init__(self):
    self.lib = ctypes.cdll.LoadLibrary('/fusion2/imageProcessingDriver.so')
    result = self.lib.init()
    self.frame= np.ones((480,752,8), dtype=np.uint8)
    
    self.f2 = open("/dev/mem", "r+b")
    self.switchMem = mmap.mmap(self.f2.fileno(), 1000, offset=0x44a20000)
    self.switchMem.seek(64) 
    self.switchMem.write(struct.pack('l', 0))
    self.switchMem.seek(0) 
    self.switchMem.write(struct.pack('l', 2))    
    self.switchMem.close()
    self.f2.close()
    
  def getMagTheta(self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,0],self.frame[:,:,2]
    
  def getStereoRGB(self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,0:3],self.frame[:,:,4:7]

  def getStereoGray (self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,3],self.frame[:,:,7]
    
  def getStereoAll (self):
    result = self.lib.getFrame(ctypes.c_void_p(self.frame.ctypes.data))
    return self.frame[:,:,0:4],self.frame[:,:,4:8]
    
  def __del__(self):
    result = self.lib.destroy