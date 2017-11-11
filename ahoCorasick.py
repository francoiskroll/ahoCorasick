# Assignment 3 - Aho-Corasick algorithm
# Francois Kroll
# 16/05/2017
# Python 3.5.3

# Assignment 3 example
keywords = ['pattern', 'tree', 'state', 'prove', 'the', 'it']

text = "As discussed in the session on Combinatorial Pattern Matching, keywords trees provide an efficient solution to search for multiple k patterns in a text of length n. The algorithm requires first the construction of a keyword tree and then, using naïve threading, the patterns can be identified in O(nm), where n is the average length of the k patterns and m is the length of the text. Alfred Aho and Margaret Corasick proposed in 1975 a more efficient solution that allows one to identify the patterns in O(m) time. To achieve this improvement, the keyword tree is replaced by a finite state pattern matching automata. Once this machine is constructed the text can be processed and the starting positions for the different patterns can be returned as output. The full specification of the Aho Corasick algorithm is provided in the original article included with this assignment."

# Aho & Corasick 1975 example
# keywords = ['he', 'she', 'his', 'hers']
# text = "He threw his shoes. She threw hers."

################################################################################

GoToGraph = [{'char': '', 'next_nodes': [], 'fail': 0, 'output':[]}] # Initializes the root of the GoTo graph.
# The GoTo graph is represented by an adjacency list of dictionaries (more details in the report).

############

def graphGoDown (state, char):
    # Small function to go one node down the graph using the edge which matches our next character (if any).
    # 'state' is the node we are on; 'char' is the character we are looking for.
    for node in GoToGraph [state] ['next_nodes']: # node loops through the nodes just after the node we are on ('state').
        if GoToGraph [node] ['char'] == char:
            return node # If there is an edge that matches the correct character, use it to go down one node.
    return None # Returns None if there is no edge matching our character.

############

def insertKeyword (keyword): # Inserts a new keyword in the GoTo graph.
# This is the 'enter' procedure in Aho & Corasick 1975 paper.

    state = 0 # First place yourself on the root.
    j = 0 # j will loop through the indexes of the characters in keyword that are already placed in the graph.
    # Eg. we are trying to add 'there' but 'the' was already placed before; in this case j will loop through 0 (t), 1 (h), 2 (e).

    next_node = graphGoDown (state, keyword[j]) # Look at the first character in the keyword ('keyword[j]' with j = 0);
    # and if there is already an edge from the root in the graph that matches it, use it to go down one node.

    while next_node != None: # While there are edges that match the next characters in our keyword, use them to go down.
    # (also assumes that the previous line did not return None, i.e. there was a first edge from the root we could use)
        state = next_node # Place yourself on the next node, i.e. go down one node.
        j = j + 1

        if j < len(keyword): # i.e. as long as the keyword is not already in the graph entirely.
        # It may happen that the keyword is already in the graph even if there is no duplicate in the input keywords.
        # Eg. we just added 'himself' in the graph, and we are trying to add 'him'.
            next_node = graphGoDown (state, keyword[j]) # Is there an edge we can use to continue going down?
            # If yes, take it (goes back to the while statement).

        else: # If the keyword is already in the graph entirely.
            break # We should not do anything.

    for p in range (j, len(keyword)):
        # p will loop through the indexes of the characters left in the keyword that are not already in the graph, i.e. the ones we need to add.
        # Eg. p would loop through 3 (r) and 4 (e) [in the previous example with 'there'/'the']
        new_node = {'char': keyword [p], 'next_nodes': [], 'fail': 0, 'output': []}
        GoToGraph.append (new_node) # Adds a new node to the graph.
        GoToGraph [state] ['next_nodes'].append (len(GoToGraph) - 1) # Adds the node we just added to the next nodes of the node we are on ('state').
        state = len (GoToGraph) - 1 # Place yourself on the new node we just added, i.e. on the tip of the graph.

    GoToGraph [state] ['output'].append (keyword) # The keyword is now fully placed in the graph.
    # We set the output of the last node to be the keyword.

############

def setGoToGraph (keywords):
    # Builds the architecture of the GoTo graph.
    # Algorithm 2 in Aho & Corasick 1975 paper.
    for key in keywords:
        insertKeyword (key)

############

def setFailureTransitions():
    # Fills in the GoTo graph with the failure transitions.
    # Algorithm 3 in Aho & Corasick 1975 paper.
    queue = [] # queue is a list of nodes that will allow us to explore the graph.

    for d1 in GoToGraph [0] ['next_nodes']: # d1 loops through the nodes of depth 1 (the ones just after the root of the graph).
        queue.append (d1)
        GoToGraph [d1] ['fail'] = 0 # Sets the fail state of the depth 1 nodes to 0.
        # i.e. if you cannot go anywhere from the root, go back to the root.
        # This represents the loop from the root to itself in Fig. 1 (a) of Aho & Corasick 1975 paper.

    while len(queue) > 0:
        r = queue.pop(0) # Takes the first node in queue, and deletes it from queue by doing so.
        # We will now set the failure transition of the nodes just after r; i.e. the nodes of depth = r's depth + 1

        for nxt in GoToGraph [r] ['next_nodes']:
            queue.append (nxt)
            node = GoToGraph [r] ['fail'] # Go explore the node where the failure transition of r leads to.

            while graphGoDown (node, GoToGraph [nxt] ['char']) == None and node != 0:
                # If the fail state of the node does not lead anywhere
                # and we are not at the root
                    # (recall the fail state of the root leads back to the root, so this prevents us from being trapped in the loop).
                node = GoToGraph [nxt] ['fail'] # Look at the fail state of the fail state.

                # and so on until the failure transitions lead us to a node different than the root.

            # When the failure transitions eventually lead us to a node (different than 0):
            GoToGraph [nxt] ['fail'] = graphGoDown (node, GoToGraph [nxt] ['char'])
                # Set the fail state of nxt (the node after r) to be this node.

            if GoToGraph [nxt] ['fail'] is None: # If we never reached a node different than the root;
                GoToGraph [nxt] ['fail'] = 0 # set the fail transition of nxt to lead back to the root.

            GoToGraph [nxt] ['output'] = GoToGraph [nxt] ['output'] + GoToGraph [GoToGraph[nxt] ['fail']] ['output']
            # Adds to the output of node nxt the output of the fail state of node nxt.
            # If one or both outputs are None, it does not change anything.
            # Eg. from Aho & Corasick 1975 paper:
                # We are at node E (after H, after S) and looking for keywords 'she' and 'he': we should output both 'she' and 'he' at node E.

############

def matchMachine (text):
    # Uses the GoTo graph to scan the input text for input keywords.
    # Algorithm 1 from Aho & Corasick 1975 paper.
    text = text.lower() # Puts the whole text in lower case so the matchMachine is case insensitive.
    state = 0 # Start at the root.
    matches = [] # 'matches' is a list of dictionaries that will store the matched keywords (more details in the report).

    for i in range (len(text)): # i loops through the indexes of the characters in the input text.

        while graphGoDown (state, text [i]) is None and state != 0: # If we cannot go down from state and we are not at the root.
        # (same reason than before; this is to prevent being stuck in root -> root failure transitions).
            state = GoToGraph [state] ['fail'] # Look at the fail state, i.e. take the failure transition.
            print (text[i], state)

        state = graphGoDown (state, text [i]) # Go down the graph by taking the edges that match the characters in text.
        print (text[i], state)

        if state is None:
            state = 0 # If we went too far, go back to the root.

        else:
            if GoToGraph [state] ['output'] is not None: # If the state we are on has an output:
                for j in GoToGraph [state] ['output']:
                    print ('>>> "', j, '"', ' found at ', i - len(j) + 1, sep = '') # Print the node's output:
                    # the keywords found and its position (index of its first character).
                    matches.append ({'keyword': j, 'location': i - len(j) + 1}) # Add the match dictionary to the 'matches' list.

    return matches

################################################################################

setGoToGraph(keywords) # Builds the GoTo graph's architecture.
setFailureTransitions() # Fills in the GoTo graph with the failure transitions.

print ('\n\nGOTO GRAPH\n')
print (GoToGraph)
print ('\n\nScanning the text...\n')

output = matchMachine (text) # Scans the text with the GoTo graph.

print ('\n\nOUTPUT')
print ('\n', output)
