import numpy as np
from instruments.device_super import InstrumentUtilty

class J7204B(InstrumentUtilty):
    def __init__(self,ip_address):
        super().__init__(ip_address)
        
        self.query_keys = np.array([
            1,
            2,
            4,
            4,
            10,
            20,
            40,
            40,
        ])
        
        self.channel_values = {
            'Ch.1': 0,
            'Ch.2': 0,
            'Ch.3': 0,
            'Ch.4': 0,
        }
        
        self.channel_query_commands = {
            'Ch.1': 'ROUT:CLOS? (@1101,1102,1103,1104,1105,1106,1107,1108)',
            'Ch.2': 'ROUT:CLOS? (@1121,1122,1123,1124,1125,1126,1127,1128)',
            'Ch.3': 'ROUT:CLOS? (@1141,1142,1143,1144,1145,1146,1147,1148)',
            'Ch.4': 'ROUT:CLOS? (@1161,1162,1163,1164,1165,1166,1167,1168)',
        }
        
        self.channel_write_commands = {
            'Ch.1': 'ROUT:SEQ:TRIG ATTEN_1_',
            'Ch.2': 'ROUT:SEQ:TRIG ATTEN_2_',
            'Ch.3': 'ROUT:SEQ:TRIG ATTEN_3_',
            'Ch.4': 'ROUT:SEQ:TRIG ATTEN_4_',
        }
    
    
    def get_channel_value(self,channel_name):
        response = self.query(self.channel_query_commands[channel_name])
        
        response_list = response.split(',')
        response_list = [int(num) for num in response_list]
        response_list = np.array(response_list)
        
        masked_values = self.query_keys * (1 - response_list)
        
        self.channel_values[channel_name] = np.sum(masked_values)
    
    
    def set_channel_value(self,channel_name,value):
        value = int(value)
        
        if value > 119:
            tens = 110
            ones = value - 110
        else:
            tens = (value // 10) * 10
            ones = value % 10
        
        
        self.write(self.channel_write_commands[channel_name] + '1_' + str(ones))
        if not tens == ((self.channel_values[channel_name] // 10) * 10):
            self.write(self.channel_write_commands[channel_name] + '2_' + str(tens))
    
    def write(self,write_str):
        self.my_instrument.write(write_str)
        self.my_instrument.query('*OPC?')
    
    def query(self,query_str):
        return self.my_instrument.query(query_str)



if __name__ == '__main__':
    my_device = InstrumentUtilty('192.168.002.234')