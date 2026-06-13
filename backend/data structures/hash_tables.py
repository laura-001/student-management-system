


class Node:
    def __init__(self,course_code,student_id):
        
        self.value = (course_code,student_id)
        self.next = None

class Linkedlist:
    def __init__(self):
        self.head = None

    def add(self,course_code,student_id):

        #prevents duplicate entries
        if self.contains(course_code,student_id):
            return False 
        
        new_node = Node(course_code,student_id)

        if self.head is None:
            self.head = new_node
            return True
        current = self.head

        def contains(self,course_code,student_id):
            current = self.head
            while current :
                if current.value == (course_code,student_id):
                    return True
                current = current.next

            return False  

        def remove(self,course_code,student_id):
            current = self.head
            previous = None

            while current:
                if current.value == (course_code,student_id):
                    if previous is None:
                        self.head = current.next
                    else:
                        previous.next = current.next
                    return True
                previous = current
                current = current.next

            return False















       # class Node:
   #def __init__(self, data):
       # self.data = data
       # self.next = None
    
#node1 = Node(3)
#node2 = Node(5)
#node3 = Node(13)
#node4 = Node(2)

#node1.next = node2
#node2.next = node3
#node3.next = node4

#currentNode = node1
#while currentNode:
    #print(currentNode.data, end=" -> ")
    #currentNode = currentNode.next
#print("null")  ///