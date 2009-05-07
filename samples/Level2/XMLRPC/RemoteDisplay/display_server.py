#!/usr/bin/env python

##Copyright 2009 Thomas Paviot (thomas.paviot@free.fr)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
##You should have received a copy of the GNU General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import wx
import zlib
from OCC.Display.wxDisplay import wxViewer3d
import SimpleXMLRPCServer
import thread
import Queue
import pickle

QUEUE = Queue.Queue()
  
class StringReceiver(object):
    def Ping(self):
        return "I got you"
    
    def SendShapeString(self,s):
        QUEUE.put(s) #Adds this string to the queue
        return True

    def SendCompressedShapeString(self,s, crc32):
        """
        Receive the string, decompress, and then check the crc32 flag.
        """
        s = zlib.decompress(s)
        QUEUE.put(s)
        return True

  
def run_server(port):
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port))
    print 'listening on port %s'%port
    instan = StringReceiver()
    server.register_instance(instan)
    server.serve_forever()
       
def RemoteDisplay(port = 8888):
    class AppFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, "wxDisplay3d sample", style=wx.DEFAULT_FRAME_STYLE,size = (640,480))
            self.canva = wxViewer3d(self)
            # Start thread that listen Queue
            thread.start_new_thread(self.Listen,())

        def Listen(self):
            print "Wait for data to be processed"
            while True:
                str_received = QUEUE.get()
                #print str_received
                # When a str is received, translate to
                #dumped_box = shape_factory.getBox(10.,10.,10.)
                shp = pickle.loads(str_received)
                self.canva._display.DisplayShape(shp)
                #self.canva.DisplayShape(s)
                    
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = AppFrame(None)
    frame.Show(True)
    wx.SafeYield()
    frame.canva.InitDriver()
    # Launch XML/RPC server
    thread.start_new_thread(run_server,(port,))
    app.SetTopWindow(frame)
    app.MainLoop()            

if __name__=="__main__":
    RemoteDisplay(port = 8888)
