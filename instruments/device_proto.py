from instruments.device_super import InstrumentUtilty

class INSTRUMENT(InstrumentUtilty):
    def __init__(self,ip_address):
        super().__init__(ip_address)
        self.channel_values = {}
        # Rest of initialization stuff
    
    
    def get_channel_value(self,channel_name):
        """Gets channel value and saves them in self.channel_values"""
        pass
    
    
    def set_channel_value(self,channel_name,value):
        """Sets a value in a specific channel"""
        pass
    
    
    def write(self,write_str):
        """Write to machine"""
        pass
    
    
    def query(self,query_str):
        """Read from machine and retrun value"""
        pass


if __name__ == '__main__':
    my_device = INSTRUMENT('192.168.002.234')