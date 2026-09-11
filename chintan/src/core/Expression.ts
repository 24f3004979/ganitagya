
// Operation List
const operators:string[] = ["+", "-", "*", "/"];

// head no parent with leaf with no child
type ExpressionNode = {
  left_element:string;
  right_element:string;
  operation:string;

  // Graphing element
  parent:ExpressionNode | null;
  child:ExpressionGraph | null; 
}

const Elements : string[]; // listing all element

// Making Graph object for simple traversal of ExpressionNode 
class Graph{
  // Over riding and over loading features for making graph work
  const Elements:string[];
  const graph_dictionary: Record<string, string[]>;

  constructor(head_element:string){
    this.head_element = this.add_node(head_element)
  }

  initiate_node(element:string){
    self.graph_dictionary[element] = []; // initiate node
  }

}

class ExpressionGraph{
  expression:string;
  depth:number; // solving depth while iteration

  constructor(expression:string){
    this.expression = expression;
    console.log("Calling operation split with constructor");
    const result:string[] = this.operation_split(expression);
    console.log(`Result out put : ${result}`);
  }

  operation_split(expression:string): [string, string, string] | string {
    // Iterate through the expression with index
    const expr:string  = expression.trim();
    for (let i=0; i < expr.length; i++){
      const char = expr[i]

      if (operators.includes(char)){
        const left_split = expr.substring(0,i).trim();
        const right_split = expr.substring(i+1).trim();
        const operator = char; // target operation
        return [left_split, operator, right_split];
      }
    }
    return expression
  }

  initiate_graph(){
    console.log("Initiating graph")

  }
}

let expression = '2x'
const e = new ExpressionGraph(expression)
