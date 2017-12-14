import wx
from frame import mainFrame
import os,sys


class sumFrame ( mainFrame ):
	
    def __init__( self, OnGen):
        mainFrame.__init__(self,None)
        self.OnGen=OnGen
        
            
    def OnFileOpen(self,even):
        dlg=wx.FileDialog(self,"open file to load","", "*.*")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.m_textCtrl7.SetValue(open(path,'r', encoding='UTF-8').read())
            dlg.Destroy()
    def OnGenerate( self, event ):
        self.m_textCtrl8.SetValue(self.OnGen(self.m_textCtrl7.GetValue()))

def startGUI(OnSum):
    app = wx.App(False)
    frame = sumFrame(OnSum)
    frame.Show()
    app.MainLoop()
