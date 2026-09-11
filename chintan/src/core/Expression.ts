/*

Expression Parsing unit

Constrcuts dependency tree for mathematical expression
  Iterates with spliting expression with operation into halfs

  appending dependency with elements for their sub expression

  used for explanation in numerical unit of chaitanya
*/ 

const operators:string[] = ["+", "-", "*", "/"];

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
}

let expression = '2x'
const e = new ExpressionGraph(expression)
