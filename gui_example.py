from app import App
import time

class Textsum(App):
    def __init__(self):
        super().__init__()
    
    def OnInitProgrmne(self):
        time.sleep(3)
        
    def OnTextSum(self,text):
        time.sleep(3)
        return text+'asd';

Textsum().MainLoop()
