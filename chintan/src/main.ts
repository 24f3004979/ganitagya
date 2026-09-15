class ExpressionEngine{
  expression:string;

  constructor(expression:string){
    this.expression = expression;

    // Operation Order
    const exp:string = expression;
    let operation_order:string[] = [];
    const priority_listing:string[] = ["/,*", "+,-"];

    for (let elem of priority_listing){
      let operations :string[] = elem.split(",");

      for (let i=0; i < exp.length; i++){
        let e = exp[i];
        console.log(`Iteration element : ${e}`);
        console.log(`operations : ${operations}`);
        if (operations.includes(e)){
          operation_order.push(e);  // operation order with iterating from left to right
        }

      }
    }

    console.log(`Operation Order sequence : ${operation_order}`);
    this.operation_order = operation_order; // component parsing list

  }

  extract_component(operation:string){
    let expression = this.expression;

    for (let i=0; i < this.expression.length; i++){
      let elem = this.expression[i];
      
      if (elem === operation){
        let parts = expression.split(elem);
        // simple parse for both elements to get number
        let left_part:string = parts[0];
        let right_part:string = parts[1];

        let left_match = left_part.match(/(\d+)\s*$/);
        let right_match = right_part.match(/^\s*(\d+)/);

        if (left_match && right_match){
          let left_number:number = parseInt(left_match[1], 10);
          let right_number:number = parseInt(right_match[1], 10);

          console.log(`Parsed operation operands : ${left_number} with right : ${right_number}`);
          return [left_number, right_number, elem];
        }
      }

    }
  }
  parse(){
    // Iterate the operation sequence and update the expression with components
  }
}

const e = new ExpressionEngine("2+4*8/2+3+9");
console.log(e.extract_component("+"))
