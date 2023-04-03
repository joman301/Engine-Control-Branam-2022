from time import sleep



def add_in_series(r1, r2, r3, r4):
    resistance = r1 + r2 + r3 + r4
    subtraction = r3 - r2
    output_list = [resistance, subtraction]
    return output_list

def add_parallel(*args):
    total = 0
    for item in args:
        # += is the same thing as total = total + item
        total += 1/item
    total = 1/total

    return total


r1 = 1
r2 = 5
r3 = 25
r4 = 50
r5 = 1000
r6 = 1000000000


print(add_parallel(r1,r2,r3,r4,r5,r6))





# ex_list = [1, 2, 3, 4, 5]
# ex_list2 = ["Josh", "Stefan", "Nick"]
# ex_dict = {
#     "Josh": "I am a string!",
#     "Stefan" : 27,
#     "Nick" : True
# }



# #print(ex_dict["Stefan"])

# # How to make a for statement loop a certain number of times
# for val in range(4):
#     print("val = " + str(val))

# # How to use a for statement to loop through a list
# for item in ex_list2:
#     print(item + " is cool")

# # How to use a for statement to loop through a dictionary
# for key in ex_dict:
#     print(str(ex_dict[key]) + " is stored in " + key)

# # While statement
# while True:
#     print("Hi")
#     sleep(0.5)



# x = 5
# if x == 5:
#     print("X = 5!")