// import javax.swing.*;
// import java.util.Arrays;

// public class RouterNode {
//     private int myID; 
//     private GuiTextArea myGUI; 
//     private RouterSimulator sim; 
//     private int[] costs = new int[RouterSimulator.NUM_NODES]; // Link costs to other nodes
//     private boolean[] neighbors = new boolean[RouterSimulator.NUM_NODES]; // Indicates if a node is a direct neighbor
//     private int[][] table = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES]; // Distance table
//     private int[] route = new int[RouterSimulator.NUM_NODES]; // Forwarding table indicating the next hop
    
//     //--------------------------------------------------
//     public RouterNode(int ID, RouterSimulator sim, int[] costs) {
//         this.myID = ID; 
//         this.sim = sim; 
//         this.myGUI = new GuiTextArea("Output window for Router #" + ID);

//         // Initialize costs and the routing table
//         System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);

//         // Initialize the routing table and identify neighbors
//         for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//             if (i == myID) {
//                 // Initialize row corresponding to this router's own ID with direct costs
//                 System.arraycopy(costs, 0, this.table[i], 0, RouterSimulator.NUM_NODES);
//             } else {
//                 // Initialize all other rows to "INFINITY" to indicate no direct connection initially
//                 Arrays.fill(this.table[i], RouterSimulator.INFINITY);
//             }

//             // Set up the route table and determine if each node is a neighbor
//             this.route[i] = (costs[i] == RouterSimulator.INFINITY) ? -1 : i; // -1 if no direct link, otherwise the direct route
//             this.neighbors[i] = (costs[i] != RouterSimulator.INFINITY); // True if there's a direct link to the node
//         }

//         // Broadcast initial routing information to neighbors
//         broadcast();
//     }

//     //--------------------------------------------------
    
//     public void recvUpdate(RouterPacket pkt) {    // Receive updates from other routers
//         // If the incoming distance vector hasn't changed, ignore it
//         if (Arrays.equals(this.table[pkt.sourceid], pkt.mincost)) return;

//         // Update the routing table with the new distance vector
//         System.arraycopy(pkt.mincost, 0, this.table[pkt.sourceid], 0, RouterSimulator.NUM_NODES);
//         boolean update = false; // Flag to track if any updates were made

//         // Use the Bellman-Ford algorithm to update the routing table
//         for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//             if (i == this.myID || this.route[i] == -1) continue; // Skip the current router and unreachable nodes

//             // Calculate new cost through the route's next hop
//             int newcost = this.table[this.route[i]][i] + this.table[this.myID][this.route[i]];
//             if (this.table[this.myID][i] != newcost) {
//                 this.table[this.myID][i] = newcost;
//                 update = true; // Mark that an update was made
//             }

//             // Reset to the original cost if the current route becomes more expensive
//             if (this.table[this.myID][i] > this.costs[i]) {
//                 this.table[this.myID][i] = this.costs[i];
//                 this.route[i] = i; // Update the route to the direct link
//                 update = true;
//             }

//             // Iterate over all neighbors to find better routes through 
//             for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
//                 if (j == this.myID) continue;

//                 // Calculate the cost of the route 
//                 int cost = this.table[this.myID][i] + this.table[i][j];
//                 if (this.table[this.myID][j] > cost) {
//                     this.table[this.myID][j] = cost; 
//                     this.route[j] = this.route[i]; 
//                     update = true;
//                 }
//             }
//         }

//         // If the routing table was updated, broadcast the changes
//         if (update) {
//             broadcast();
//         }
//     }
    
//     //--------------------------------------------------
//     private void sendUpdate(RouterPacket pkt) {    
//         sim.toLayer2(pkt); 
//     }


//     //--------------------------------------------------
//     public void printDistanceTable() {     // Print the distance table and routing information
//         myGUI.println("Current table for " + myID +
//         "  at time " + sim.getClocktime());
        
//         myGUI.println("\nDistancetable:\n");

//         String line = "-----------------------------------------------------------------";
//         String dst = F.format("dst ", 10) + " |"; // Column headers

//         // Print column headers (destination nodes)
//         for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//             dst += F.format(i, 10);
//         }
//         myGUI.println(dst);
//         myGUI.println(line);

//         // Print the distance table for each neighbor
//         for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//             if (this.myID != i && this.costs[i] != RouterSimulator.INFINITY) {
//                 String temp = F.format("nbr " + i + " |", 10);
//                 for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
//                     temp += F.format(table[i][j], 10);
//                 }
//                 myGUI.println(temp);
//             }
//         }

//         // Print the distance vector (costs and routes)
//         myGUI.println("\nDistance vector and routes: \n");
//         String costLine = F.format("cost ", 9) + " |";
//         String routeLine = F.format("route ", 8) + " |";

//         // Print the cost and route for each node
//         for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//             costLine += F.format(this.table[this.myID][i], 10);
//             routeLine += (this.table[this.myID][i] == RouterSimulator.INFINITY) ? F.format("-", 10) : F.format(i, 10);
//         }

//         myGUI.println(costLine);
//         myGUI.println(routeLine);
//         myGUI.println("\n\n\n");
//     }

//     //--------------------------------------------------
//     public void updateLinkCost(int dest, int newcost) {    
//       this.costs[dest] = newcost; // Update the cost array
//       this.table[this.myID][dest] = newcost; // Update the routing table for this direct link
  
//       // Iterate over all other nodes to update the routing table
//       for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
//           if (j == this.myID) continue;
  
//           // Update the cost if routing through `dest` is cheaper
//           int cost = this.table[this.myID][dest] + this.table[dest][j];
//           if (this.table[this.myID][j] > cost) {
//               this.table[this.myID][j] = cost;
//               this.route[j] = this.route[dest]; // Update the first hop
//           }
//       }
  
//       // Broadcast the updated information
//       broadcast();
//   }

//     //----------------added function--------------------


//     private void broadcast() {    // Broadcast the current distance vector to all neighbors
//       for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
//           if (i != this.myID && this.neighbors[i]) {
//               // Create a copy of the current router's distance vector
//               int[] arr = Arrays.copyOf(this.table[myID], RouterSimulator.NUM_NODES);

//               // Poison reverse: Set routes through neighbor `i` to infinity to avoid loops
//               if (RouterSimulator.POISONREVERSE) {
//                   for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
//                       if (this.route[j] == i && i != j) {
//                           arr[j] = RouterSimulator.INFINITY; // "Poison" this route
//                       }
//                   }
//               }
//               // Send the updated vector to the neighbor
//               sendUpdate(new RouterPacket(myID, i, arr));
//           }
//       }
//   }
  
// }

import javax.swing.*;

public class RouterNode {
    private int myID;
    private GuiTextArea myGUI;
    private RouterSimulator sim;
    private int[] costs = new int[RouterSimulator.NUM_NODES];
    private int[] routes = new int[RouterSimulator.NUM_NODES];
    private int numNeighbors;
    private int[] neighbors;
    private int[][] distTable;
    private int[] distVector = new int[RouterSimulator.NUM_NODES];

    private boolean poisonedReverseEnabled = false;
    //--------------------------------------------------
    public RouterNode(int ID, RouterSimulator sim, int[] costs) {
        myID = ID;
        this.sim = sim;
        myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

        System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
        System.arraycopy(costs, 0, distVector, 0, RouterSimulator.NUM_NODES);

        // Find routes to neighbors
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(this.costs[i] != RouterSimulator.INFINITY) {
                // This is a neighbour, next hop is known
                this.routes[i] = i;
                if(i != this.myID) {
                    this.numNeighbors++;
                }
            }
            else {
                this.routes[i] = RouterSimulator.INFINITY; // Unknown route
            }
        }

        this.neighbors = new int[numNeighbors];
        int iNeighbor = 0;
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(i == myID) {
                continue;
            }
            if(this.costs[i] != RouterSimulator.INFINITY){
                neighbors[iNeighbor] = i;
                iNeighbor++;
            }
        }

        this.distTable = new int[numNeighbors][RouterSimulator.NUM_NODES];
        for(int i = 0; i < numNeighbors; i++) {
            for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
                if(neighbors[i] == j) {
                    distTable[i][j] = 0;
                } else {
                    distTable[i][j] = RouterSimulator.INFINITY;
                }
                // No idea about neighbors distance to anywhere, even ourself (sic!)
            }
        }

        printDistanceTable();

        for(int i = 0; i < this.neighbors.length; i++) {
            sendUpdate(new RouterPacket(this.myID, this.neighbors[i], this.costs));
        }

    }

    //--------------------------------------------------
    public void recvUpdate(RouterPacket pkt) {

        if(pkt.destid == this.myID) {
            distTable[java.util.Arrays.binarySearch(neighbors, pkt.sourceid)] = pkt.mincost;
        }

        recomputeCostsAndRoutesVectors();
    }


    //--------------------------------------------------
    private void sendUpdate(RouterPacket pkt) {
        sim.toLayer2(pkt);
    }


    //--------------------------------------------------
    public void printDistanceTable() {
        F formatter = new F();
        myGUI.println("Current table for " + myID +
                      "  at time " + sim.getClocktime());

        myGUI.println("Distancetable:");
        String dstTableHeader = new String();
        dstTableHeader = "    dst |";
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            dstTableHeader += "    " + i;
        }

        // Print distance table
        myGUI.println(dstTableHeader);
        myGUI.println(new String(new char[dstTableHeader.length()]).replace("\0", "-"));

        for(int i = 0; i < neighbors.length; i++) {
            String dstString = new String();
            dstString = " nbr " + neighbors[i] + "  |";

            for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
                dstString += formatter.format(distTable[i][j], 5);
            }
            myGUI.println(dstString);
        }

        // Print cost and route vectors
        myGUI.println("Our distance vector and routes:");
        myGUI.println(dstTableHeader);
        myGUI.println(new String(new char[dstTableHeader.length()]).replace("\0", "-"));

        String costString = new String();
        String routeString = new String();
        costString = " dist   |";
        routeString = " route  |";

        for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
            costString += formatter.format(distVector[j], 5);
            if(routes[j] == RouterSimulator.INFINITY) {
                routeString += formatter.format("-", 5);
            } else {
                routeString += formatter.format(routes[j], 5);
            }
        }

        myGUI.println(costString);
        myGUI.println(routeString);
        myGUI.println();


    }

    //--------------------------------------------------
    public void updateLinkCost(int dest, int newcost) {
        costs[dest] = newcost;
        recomputeCostsAndRoutesVectors();
    }

    private void recomputeCostsAndRoutesVectors() { // THIS IS JAAAAVAAAA!
        boolean somethingChanged = false;

        for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
            int shortestPathFound = RouterSimulator.INFINITY;
            int nextHop = -1;

            if(j == myID) {
                shortestPathFound = 0;
                nextHop = myID;
                continue;
            }

            // Shortest path, if we first route through a neighbour
            for(int i = 0; i < neighbors.length; i++) {

                if(costs[neighbors[i]] + distTable[i][j] < shortestPathFound) {
                    shortestPathFound = costs[neighbors[i]] + distTable[i][j];
                    nextHop = neighbors[i];
                }
            }

            if(shortestPathFound != distVector[j]) {
                somethingChanged = true;
                distVector[j] = shortestPathFound;
                routes[j] = nextHop;
            }
        }

        if(somethingChanged) {
            sendUpdatesToAllTheOtherRouterNodes();
        }

        printDistanceTable();
    }

    private void sendUpdatesToAllTheOtherRouterNodes() {
        for(int i = 0; i < this.neighbors.length; i++) {
            int[] poisonedReversedCosts = new int[RouterSimulator.NUM_NODES];
            System.arraycopy(distVector, 0, poisonedReversedCosts, 0, distVector.length);

            if(poisonedReverseEnabled){
                for(int j = 0; j < routes.length; j++) {
                    if(neighbors[i] == routes[j] && j != neighbors[i]) {
                        poisonedReversedCosts[j] = RouterSimulator.INFINITY;
                    }
                }
            }
            sendUpdate(new RouterPacket(myID, neighbors[i], poisonedReversedCosts));
        }
    }

}
