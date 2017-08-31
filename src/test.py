class_list = [1,1,2,2,3,4,5,6,7]
class_list = list(set(class_list))
print(class_list)
print(id(class_list))
cl = class_list
print(id(cl))
del class_list
print(cl)