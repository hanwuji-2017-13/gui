from app import Start_GUI
from app import TextSumApi
import time


class api(TextSumApi):
    
    def get_html_url(self):
        return "http://news.163.com/18/0123/19/D8S08G4K000189FH.html"
    
    def OnInit(self):
        pass

    def OnGenTextSum(self,text):
        time.sleep(3)
        return (text+"qwe",4)
        pass
    
    def OnSelTextSum(self,text):
        time.sleep(3)
        return (text+"zxc",3)
        pass

    def get_help_url(self):
        return "<hrml>hello</html>"
        pass
print("asd")
Start_GUI(api())
