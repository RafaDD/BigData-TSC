import numpy as np


carbon_table = {
    0: 3529,
    1: 5134, 2: 7089, 3: 9852, 4: 12449, 5: 14845, 6: 17930,
    7: 6985, 8: 7950, 9: 9683, 10: 12423, 11: 16578, 12: 21855, 13: 29459, 14: 40359, 15: 50682,
    16: 9951, 17: 15956, 18: 20786, 19: 27104, 20: 36102, 21: 46021 
} # CO2 emission in g/hr

def VSP(v, a):
    vsp = 0.1565 * v + 2.002e-3 * v ** 2 + 4.926e-4 * v ** 3 + 1.479 * v * a
    return vsp

def get_cate(vsp, v):
    if v == 0:
        idx = 0
    elif v <= 6.9444:
        vsp_k = np.array([-np.inf, 0, 3, 6, 9, np.inf])
        idx = np.max(np.where(vsp <= vsp_k)[0]) + 1
    elif v <= 13.889:
        vsp_k = np.array([-np.inf, 0, 3, 6, 9, 12, 18, 24, np.inf])
        idx = np.max(np.where(vsp <= vsp_k)[0]) + 7
    else:
        vsp_k = np.array([-np.inf, 6, 12, 18, 24, np.inf])
        idx = np.max(np.where(vsp <= vsp_k)[0]) + 16
    return idx, carbon_table[idx]


class CarbonMetric():
    def __init__(self, world):
        self.world = world
        self.world.subscribe(["vehicles", "time"])
        self.vehicle_last_speed = {}


    def reset(self):
        self.vehicle_last_speed = {}

    def update(self, done=False):
        vehicles = self.world.get_info("vehicles")
        # current_time = self.world.get_info("time")s
        
        carbon_lst = []
        cate_lst = np.zeros(22)

        for vehicle in vehicles:
            veh_info = self.world.eng.get_vehicle_info(vehicle)
            # print(veh_info)
            
            if self.vehicle_last_speed.get(vehicle) == None:
                self.vehicle_last_speed[vehicle] = veh_info['speed'][0]
            
            v = veh_info['speed'][0]
            a = v - self.vehicle_last_speed[vehicle]
            vsp = VSP(v, a)
            cate, carbon = get_cate(vsp, v)
            
            cate_lst[cate] += 1
            carbon_lst.append(carbon)
            
            self.vehicle_last_speed[vehicle] = veh_info['speed'][0]
            
        if len(vehicles) == 0:
            return cate_lst, 0
        return cate_lst / np.sum(cate_lst), np.mean(carbon_lst)
