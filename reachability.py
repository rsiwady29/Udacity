#Reachability

#Single Gold Star

#Define a procedure, reachable(graph, node), that takes as input a graph and a
#starting node, and returns a list of all the nodes in the graph that can be
#reached by following zero or more edges starting from node.  The input graph is
#represented as a Dictionary where each node in the graph is a key in the
#Dictionary, and the value associated with a key is a list of the nodes that the
#key node is connected to.  The nodes in the returned list may appear in any
#order, but should not contain any duplicates.


def reachable(graph, node):
    if node not in graph:
        return []
    else:
        result = [node]
        for entry in graph[node]:
            nodes = []
            if entry not in result:
                result.append(entry)
                nodes = reachable(graph,entry)
                
            for ele in nodes:
                if len(ele)>0:
                    result.append(ele)
        return result




#For example,

graph = {'a': ['b', 'c'],
         'b': ['a', 'c'],
         'c': ['b', 'd'],
         'd': ['a'],
         'e': ['a']
         }

print reachable(graph, 'a')
#>>> ['a', 'c', 'd', 'b']

#print reachable(graph, 'd')
#>>> ['d', 'a', 'c', 'b']

#print reachable(graph, 'e')
#>>> ['e', 'a', 'c', 'd', 'b']
