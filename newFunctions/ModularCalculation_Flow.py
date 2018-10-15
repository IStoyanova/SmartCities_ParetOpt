"""
author: ist-egu
"""

from newFunctions.ModularCalculation_IO import *

def createMatrixFor_b_vector(cityquarter,networkType,current_values):
    """
    Creates a matrix whose columns will be b vector in linear representation A.x=b

    :returns nodeInflow_dict
        A dictionary of arrays, which holds the values of the flow quantities supplied by a network node
        e.g. currentInflow_dict[1]=[100,104, ...]
        ==> 100A current will flow into the electricity network from the node 1 at timestep=0
        ==> 102A current will flow into the electricity network from the node 1 at timestep=1
        ...
    """

    if networkType=='ele':
        nodelist=cityquarter.nodelists_electricity['default']
        no=0
        division=cityquarter.voltage
    if networkType == 'gas':
        nodelist = cityquarter.nodelists_gas['default']
        no=1
        division=1
    if networkType == 'heat':
        nodelist = cityquarter.nodelists_heating['default']
        no=2
        division=1
    if networkType == 'water':
        nodelist = cityquarter.nodelists_water['default']
        no=3
        division = 1

    # Create empty dict of node inflows
    nodeInflow_dict = {}

    for n in nodelist:
        #  If node holds attribute 'node_type'
        if 'node_type' in cityquarter.node[n]:
            #  If node_type is building
            if cityquarter.node[n]['node_type'] == 'building':
                #  If entity is of one of the following types
                if cityquarter.node[n]['entity']._kind in ['pv', 'windenergyconverter', 'chp', 'heps',
                                                    'p2gConverter',
                                                    'p2gStorage', 'gassource', 'watersource']:
                    nodeInflow_dict[n] = calculateIO_device(cityquarter.node[n]['entity'], current_values)[no] / division
                if cityquarter.node[n]['entity']._kind == 'building':
                    nodeInflow_dict[n] = calculateIO_building(cityquarter.node[n]['entity'], current_values)[no] / division

    return nodeInflow_dict

def createMatrixFor_x_Vector(timesteps,nodelist,edgelist):
    """
    Creates a matrix whose columns will be x vector in linear representation A.x=b

    :returns solutionDict
        A dictionary of arrays, which holds the values of the flow between two network nodes
        e.g. solutionDict[1][2]=[80,74, ...]
        ==> 80A current will flow through the edge between node 1 and node 2 at timestep=0
        ==> 74A current will flow through the edge between node 1 and node 2 at timestep=1
        ...
    """
    solutionDict = {}
    for nd in nodelist['default']:
        for ed in edgelist:
            nd1, nd2 = ed
            if nd1 == nd:
                if nd in solutionDict.keys():
                    solutionDict[nd][nd2] = [None] * timesteps
                else:
                    solutionDict.update({nd: {nd2: [None] * timesteps}})
    return solutionDict

def reduceAndSolve(timesteps,nodeinflowDict,flowSolDict,nodelist,edgelist):
    """
    This method reduces the overdetermined system, solves the reduced equation A.x=b
    :returns: A dictionary of arrays that represents the flow quantities through the connection mediums
    """

    row2remove = []

    for pair in edgelist:
        node1, node2 = pair
        if len([item for item in edgelist if node2 in item]) == 1:
            flowSolDict[node1][node2] = -1 * nodeinflowDict[node2]
            row2remove.append(node2)
        elif len([item for item in edgelist if node1 in item]) == 1:
            flowSolDict[node1][node2] = nodeinflowDict[node1]
            row2remove.append(node1)

    column2remove = []
    for i in flowSolDict:
        for j in flowSolDict[i]:
            if flowSolDict[i][j][0] != None:
                column2remove.append((i, j))

    Rowreduced_coef_list = []
    Rowreduced_sol_list = []
    for node in sorted(nodelist['default']):
        if not node in row2remove:
            Rowreduced_sol_list.append(nodeinflowDict[node].tolist())
            list = []
            for pair in edgelist:
                pair1, pair2 = pair
                if pair1 == node:
                    list.append(1)
                elif pair2 == node:
                    list.append(-1)
                else:
                    list.append(0)
            Rowreduced_coef_list.append(list)

    A_rows_reduced = np.array(Rowreduced_coef_list)

    b_rows_reduced = Rowreduced_sol_list

    colRemoved = column2remove[0:len(column2remove) - 1]
    colNotRemoved = column2remove[len(column2remove) - 1]

    colList = [edgelist.index(i) for i in colRemoved]

    A_reduced = np.delete(A_rows_reduced, tuple(colList), axis=1)
    b_reduced = np.stack(b_rows_reduced)

    x = []
    for time in range(timesteps):
        for j in colList:
            node1, node2 = edgelist[j]
            b_reduced[:, time] -= A_rows_reduced[:, j] * flowSolDict[node1][node2][time]
        x.append(np.linalg.solve(A_reduced, b_reduced[:, time]).tolist())

    branchFlowSolutionList= [branch for branch in edgelist if branch not in colRemoved]

    solution = np.stack(x, axis=-1)

    for edge in range(len(solution)):
        n1, n2 = branchFlowSolutionList[edge]
        flowSolDict[n1][n2] = solution[edge]

    return flowSolDict