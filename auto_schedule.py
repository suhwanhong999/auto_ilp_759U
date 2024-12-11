# I forgot how to code in python! :D
import argparse 
import networkx as nx
import sys
import subprocess

def getGraph(filename: str, graph):
  with open(filename, 'r') as edgelist:
    for line in edgelist:
      line = line.strip()
      nums = line.split()
      n1, n2, w = map(int, nums)
      # print(n1, n2, w) # debug
      graph.add_edge(n1, n2, weight=w)

    # print("Number of nodes:", graph.number_of_nodes()) # debug
    # print("Number of edges:", graph.number_of_edges()) # debug
#   for n1, n2, w in graph.edges.data("weight"):
#     print(str(n1) + ", " + str(n2) + ", " + str(w) + "\n")
  return graph

# Helper function to generate_subjects
def rm_duplicates(glpk_file: str, graph):
  nodelist = list(graph.nodes)
  edgelist = list(graph.edges)

  output = set()
  num_nodes = graph.number_of_nodes()
  for cx in range(1, num_nodes):
    for n1, n2, w in graph.edges.data("weight"):
      for i in range(1, cx+1):
        for j in range(cx+1, num_nodes+1):
          px = "P_x" + str(n1) + "_" + str(i)
          px += "_x" + str(n2) + "_" + str(j)
          x1 = "x" + str(n1) + "_" + str(i)
          x2 = "x" + str(n2) + "_" + str(j)
          label = "  " + px + "quad1: "
          newstr = label + px + " - " + x1 + " - " + x2 + " >= -1 \n"
          output.add(newstr)

          label = "  " + px + "quad2: "
          newstr2 = label + px + " - " + x1 + " <= 0 \n"
          output.add(newstr2)

          label = "  " + px + "quad3: "
          newstr3 = label + px + " - " + x2 + " <= 0 \n"
          output.add(newstr3)

  with open(glpk_file, 'a') as lpfile:
    for item in output:
      # line = item + "\n"
      lpfile.write(item)

# Generate "Subject To" Lines
def generate_subjects(glpk_file: str, graph, area: int, limit: int, min_mem: bool):
  # TODO: Generate GLPK-compatible format

  with open(glpk_file, 'a') as lpfile:
    # "Subject To" Line
    lpfile.write("\nSubject To \n")
    nodelist = list(graph.nodes)
    edgelist = list(graph.edges)

    # Cons Line
    num_nodes = graph.number_of_nodes()
    if (min_mem == True):
      lpfile.write("  cons: L = " + str(num_nodes) + " \n")
    else:
      lpfile.write("  cons: M = " + str(limit) + " \n")
    lpfile.write("\n")

    # Generating "edge" lists
    for edge in edgelist:
      # print(edge) # debug
      newstr = "  edge"
      # nodes = edge.strip('()').split(', ')
      n1, n2 = edge
      n1 = "s" + str(n1)
      n2 = "s" + str(n2)
      newstr = newstr + n1 + "_" + n2 + ": "
      newstr += n1 + " - "
      newstr += n2 + " <= -1 "
      # print(newstr) # debug
      newstr += "\n"
      lpfile.write(newstr)

    # Generating latency lists
    idx = 1

    lpfile.write("\n")
    for node in nodelist:
      newstr = "  lat" + str(idx) + ": "
      newstr += "s" + str(node) + " - L <= 0\n"
      idx += 1
      lpfile.write(newstr)


    # Generating "sch" lists
    idx = 1
    lpfile.write("\n")
    for node in nodelist:
      newstr = "  sch" + str(idx) + ": "
      idx += 1
      for i in range(num_nodes):
        newvar = "x" + str(node) + "_" + str(i+1)
        newstr += newvar
        if i != (num_nodes - 1):
          newstr += " + "
      newstr += " = 1 \n"
      # print(newstr)
      lpfile.write(newstr)

    # Generating "cycl" lists
    lpfile.write("\n")
    idx = 1
    for node in nodelist:
      newstr = "  cycl_" + str(idx) + ": "
      idx += 1
      for i in range(num_nodes):
        if (i != 0):
          newstr += str(i+1) + " x" + str(node) + "_" + str(i+1)
        else:
          newstr += "x" + str(node) + "_" + str(i+1)
        if i != (num_nodes - 1):
          newstr += " + "
      newstr += " - s" + str(node)
      newstr += " = 0 \n"
      # print(newstr) # debug
      lpfile.write(newstr)

    # Generating "area" lists
    idx = 1
    num_nodes = graph.number_of_nodes()
    lpfile.write("\n")
    for i in range(num_nodes):
      newstr = "  area" + str(idx) + ": "
      idx += 1
      for node in nodelist:
        newvar = "x" + str(node) + "_" + str(i+1) + " + "
        newstr += newvar
      # newstr += " - m" + str(node) + " <= 0 \n" #+ str(0) + " \n"
      newstr = newstr[:-3]
      newstr += " <= " + str(area) + "\n"
      lpfile.write(newstr)

    # Generating "mem" lists
    newstr = ""
    idx = 1
    for cx in range(1, num_nodes):
      lpfile.write("\n")
      newstr = "  Mem" + str(cx) + ": "
      for n1, n2, w in graph.edges.data("weight"):
        for i in range(1, cx+1):
          for j in range(cx+1, num_nodes+1):
            newstr += str(w) + " P_x" + str(n1) + "_" + str(i)
            newstr += "_x" + str(n2) + "_" + str(j)
            newstr += " + "

      newstr = newstr[:-3]
    #   newstr += " - m" + str(idx) + " <= 0"
      newstr += " - M <= 0"
      idx += 1
      lpfile.write(newstr)

    lpfile.write(" \n")
    lpfile.write(" \n")
  rm_duplicates(glpk_file, graph)

# Generate "Bounds" Lines
def generate_bounds(glpk_file: str, graph, area: int, limit: int, min_mem: bool):
  nodelist = list(graph.nodes)
  num_nodes = graph.number_of_nodes()
  with open(glpk_file, 'a') as lpfile:
    # "Bounds" Line
    lpfile.write("\n\nBounds \n")
    # Schedule Vars
    for node in nodelist:
      for i in range(num_nodes):
        newstr = "  0 <= x" + str(node) + "_"
        newstr += str(i+1) + " <= 1 \n"
        lpfile.write(newstr)
    lpfile.write("\n")
    # Scheduling SDC Vars
    for node in nodelist:
      newstr = "  1 <= s" + str(node)
      if (min_mem == True):
        newstr += " <= " + str(limit) + "\n"
      else:
        newstr += " <= " + str(num_nodes) + "\n"
      lpfile.write(newstr)

    lpfile.write("\n")

    # for node in nodelist:
    #   newstr = "  0 <= m" + str(node)
    #   # newstr += " <= " + str(limit) + "\n"
    #   newstr +=  "\n"
    #   lpfile.write(newstr)

    # if (min_mem == True):
    #   lpfile.write("  M >= 1 \n")
    # #   lpfile.write("  1 <= L <= " + str(num_nodes) + "\n")
    # else:
    # #   lpfile.write("  1 <= M <= " + str(limit) + "\n")
    #   lpfile.write("  L >= 1 \n")


    # total = "  0 <= "
    # for node in nodelist:
    #   total += "a" + str(node) + " + "
    #   newstr = "  0 <= a" + str(node)
    #   # newstr += " <= " + str(limit) + "\n"
    #   newstr +=  "\n"
    #   lpfile.write(newstr)
    # total = total[:-3]
    # total += " <= " + str(area) + "\n"
    # # lpfile.write(total)

    vars = set()
    for cx in range(1, num_nodes):
        for n1, n2, w in graph.edges.data("weight"):
            for i in range(1, cx+1):
                for j in range(cx+1, num_nodes+1):
                    px = "  0 <= "
                    px += "P_x" + str(n1) + "_" + str(i)
                    px += "_x" + str(n2) + "_" + str(j)
                    px += " <= 1 \n"
                    vars.add(px)
    lpfile.write(" \n")
    for item in vars:
        lpfile.write(item)
    lpfile.write(" \n")


# Generate "Integer" Lines
def generate_integers(glpk_file: str, graph, min_mem: bool):
  nodelist = list(graph.nodes)
  num_nodes = graph.number_of_nodes()
  with open(glpk_file, 'a') as lpfile:
    # "Integer" Line
    lpfile.write("\n\nInteger \n")
    for node in nodelist:
      for i in range(num_nodes):
        newstr = "  x" + str(node) + "_"
        newstr += str(i+1) + "\n"
        lpfile.write(newstr)
    lpfile.write("\n")

    # Schedule Vars
    for node in nodelist:
      newstr = "  s" + str(node) + "\n"
      lpfile.write(newstr)

    lpfile.write("\n")

    # Memory Vars
    # for node in nodelist:
    #   newstr = "  m" + str(node) + "\n"
    #   lpfile.write(newstr)
    if (min_mem == True):
        lpfile.write("  M \n")
    else:
        lpfile.write("  L \n")

    # # Area Vars
    # for node in nodelist:
    #   newstr = "  a" + str(node) + "\n"
    #   lpfile.write(newstr)

    vars = set()
    for cx in range(1, num_nodes):
        for n1, n2, w in graph.edges.data("weight"):
            for i in range(1, cx+1):
                for j in range(cx+1, num_nodes+1):
                    px = "  P_x" + str(n1) + "_" + str(i)
                    px += "_x" + str(n2) + "_" + str(j)
                    px += " \n"
                    vars.add(px)
    lpfile.write(" \n")
    for item in vars:
        lpfile.write(item)
    lpfile.write(" \n")
        # END Line
    lpfile.write("\n\nend")

def generate_minimize(glpk_file: str, graph, min_mem: bool):
  num_nodes = graph.number_of_nodes()
  with open(glpk_file, 'w') as lpfile:
    lpfile.write("\nMinimize \n")

    # Minimize Memory
    if (min_mem == True):
      lpfile.write("  memory: M \n")
    # Minimize Latency
    else:
      lpfile.write("  latency: L \n")

def main():
  print("//////////////////////////////////")
  print("Welcome to Suhwan's Final Project!")
  print("//////////////////////////////////\n")
  parser = argparse.ArgumentParser()
  parser.add_argument("-f", "--filename", type=str, help="Edgelist File Path")
  parser.add_argument("-a", "--area", type=int, help="Area Limit")
  parser.add_argument("-ml", "--memory_limit", type=int, help="Runs in Minimize Latency Mode with Given Memory Limit")
  parser.add_argument("-ll", "--latency_limit", type=int, help="Runs in Minimize Memory Mode with Given Latency Limit")

  args = parser.parse_args()

  print(f"Processing file: {args.filename}")
  print(f"Area Limit: {args.area}")
  area = args.area
  if (args.memory_limit):
    print("Minimize Latency Mode")
    print(f"Memory Limit is: {args.memory_limit}")
    limit = args.memory_limit
    min_memory = False
  elif (args.latency_limit):
    print("Minimize Memory Mode")
    print(f"Latency Limit is: {args.latency_limit}")
    limit = args.latency_limit
    min_memory = True
  else:
    print("ERROR! Must define Memory Or Latency Limit")
    sys.exit(1)

  fname = "data/" + args.filename
  glpk_file = fname + ".lp"

  g = nx.DiGraph()
  getGraph(fname, g)
  generate_minimize(glpk_file, g, min_memory)
  generate_subjects(glpk_file, g, area, limit, min_memory)
  generate_bounds(glpk_file, g, area, limit, min_memory)
  generate_integers(glpk_file, g, min_memory)

  # Running Subprocesses to run GLPK 
  print("\nRunning GLPK Linear Solver now...")
  print("-----------------------------------------------------------------------------------------------------")
  cmd_line = "glpk-5.0/examples/glpsol --cpxlp " + glpk_file + " -o outputs/" + args.filename + ".out"
  subprocess.run(cmd_line, input=cmd_line, shell=True, text=True)

if __name__ == "__main__":
  main()

