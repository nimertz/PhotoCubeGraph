//cubeobjects
MATCH (co : Object ) return co;
MATCH (co : Object {id: 1}) return co;

//Hierarchy
MATCH (co : Hierarchy ) return co;
MATCH (co : Hierarchy {id: 1}) return co;

//​ Node​/{id}​/tree - Find everything under node with id - based on https://stackoverflow.com/questions/28557055/neo4j-deep-hierarchy-query
// MATCH (root: Node {id: 40})
// MATCH p = (root)<-[:HAS_PARENT*]-() //define path
// WITH last(nodes(p)) AS currNode, length(p) AS depth, root
// OPTIONAL MATCH (currNode)<-[r:HAS_PARENT]-(children: Node) // tranverse children - optional as it can be 0
// MATCH (currNode)-[:REPRESENTS]->(tag: Tag)-[:IN_TAGSET]->(ts: Tagset)
// RETURN currNode, root, depth, tag, ts.name as tagset;

//node hierarchy JSON LIKE FORMAT
MATCH p=(root:Node {id:40})<-[:HAS_PARENT*]-()-[:REPRESENTS]->(tag: Tag)-[:IN_TAGSET]->(ts: Tagset)
WITH collect(p) AS ps
CALL apoc.convert.toTree(ps) yield value
RETURN value;

MATCH p=(root:Node {id:691})<-[:HAS_PARENT*]-()-[:REPRESENTS]->(tag: Tag)
WITH collect(p) AS ps
return ps;

//find immediate node children
MATCH (root: Node {id: 5})
MATCH p = (root)<-[:HAS_PARENT]-()
RETURN p;

//find all images with dogs - 45 - id: 691
MATCH (root:Node)-[:REPRESENTS]-(t:Tag {name:"Dog"})
MATCH (root)<-[:HAS_PARENT*]-()-[:REPRESENTS]->(tag: Tag)<-[:TAGGED]-(o:Object)
RETURN o;

//find all images within entity hierarchy
MATCH (root: Node {id:40})
MATCH (root)<-[:HAS_PARENT*]-()-[:REPRESENTS]->()<-[:TAGGED]-(o:Object)
RETURN o;


// postgres = - Neo4j = 11 ms
//find all images from 2015
 MATCH (tag :Tag:Numerical {name:2015})<-[:TAGGED]-(o)
 return o;

// postgres = - Neo4j = 323 ms
// Combined state - dog, entity hierarchy, year 2015 - ids unknown - 295 ms
MATCH (root: Node)-[:REPRESENTS]-(dogTag: Tag:Alphanumerical {name:"Dog"})
MATCH (root)<-[:HAS_PARENT*]-()-[:REPRESENTS]->()<-[:TAGGED]-(o: Object)
MATCH (ent : Node)-[:REPRESENTS]->(entTag: Tag:Alphanumerical {name: "Entity"})
WHERE EXISTS {
    MATCH (ent)<-[:HAS_PARENT*]-()-[:REPRESENTS]->()<-[:TAGGED]-(o)
} AND EXISTS {
    MATCH (tag:Tag:Numerical {name:2015})<-[:TAGGED]-(o)
}
RETURN o;

// postgres = 7ms - Neo4j = 120 ms
//Combined state - dog, entity hierarchy, year 2015 -   ids known 
MATCH (dog: Node {id:691})
MATCH (ent: Node {id:40})
MATCH (year:Tag:Numerical {id: 1350})
MATCH (dog)<-[:HAS_PARENT*]-()-[:REPRESENTS]->()<-[:TAGGED]-(o: Object)
WHERE EXISTS {
    MATCH  (year)<-[:TAGGED]-(o)
} AND EXISTS {
    MATCH (ent)<-[:HAS_PARENT*]-()-[:REPRESENTS]->()<-[:TAGGED]-(o)
}
RETURN o;


