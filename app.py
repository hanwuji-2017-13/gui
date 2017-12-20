import wx
from frame import mainFrame
import os,sys    
import _thread


EVT_INITED = wx.NewEventType()
EVT_TEXTSUM = wx.NewEventType()

class CountEvent(wx.PyCommandEvent):
    def __init__(self,etype, value=None):
        super().__init__(etype)
        self._value = value

    def GetValue(self):
        return self._value

class sumFrame ( mainFrame ):
	
    def __init__( self):
        super().__init__(None)
        self.m_bpButton4.Enable(False)
        self.m_statusBar1.SetStatusText("loading data")

    def loaing(self,is_loading):
        self.m_bpButton4.Enable(not is_loading)
        self.m_statusBar1.SetStatusText("textsuming" if is_loading else "ready")

    def enable(self,evt):
        self.m_bpButton4.Enable(True)
        self.m_statusBar1.SetStatusText("ready")
            
    def OnFileOpen(self,even):
        dlg=wx.FileDialog(self,"open file to load","", "*.*")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.m_textCtrl7.SetValue(open(path,'r', encoding='UTF-8').read())
            dlg.Destroy()
            
    def OnGenerate( self, event ):
        self.Bind(wx.PyEventBinder(EVT_TEXTSUM),self.OnTextSum)
        str=self.m_textCtrl7.GetValue()
        self.loaing(True)
        _thread.start_new_thread(wx.GetApp().OnFinish,(EVT_TEXTSUM,lambda :wx.GetApp().OnTextSum(str)))

    def OnTextSum(self,event):
        self.loaing(False)
        self.m_textCtrl8.SetValue(event.GetValue())

class App(wx.App):
    def __init__(self):
        super().__init__()
        self.frame = sumFrame();
        self.frame.Show()
        self.frame.Bind(wx.PyEventBinder(EVT_INITED),self.frame.enable)
        _thread.start_new_thread(self.OnFinish,(EVT_INITED,lambda :self.OnInitProgrmne()))
            
    def OnFinish(self,etype,func):
        evt = CountEvent(etype,func())
        wx.PostEvent(self.frame, evt)


