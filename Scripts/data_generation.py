import random


def generate_data(min, max, num_of_sensors, num_of_faulty_sensors, break_t_or_f):
    
    faulty_chance = 0.1  # 10% chance the sensor has a faulty reading - voltage spike or something
    data = []
    faulty = []

    if num_of_sensors < num_of_faulty_sensors:
        print("You have more faulty sensors than total sensors ya goob")
        return False


    for i in range(num_of_sensors):    
            if num_of_faulty_sensors >= i+1:
                faulty.append(True)
            else:
                faulty.append(False)

    for sensor in range(num_of_sensors):

        if faulty[sensor]:
            temp = random.random()
            if temp < faulty_chance:
                data.append(5*((max-min)*random.random()+min))
            else:
                data.append((max-min)*random.random()+min)
        else:
            data.append((max-min)*random.random()+min)
        
    return data


if __name__ == "__main__":
    print(generate_data(80, 100, 5, 5))