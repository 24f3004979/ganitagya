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

  extract_component(operation:string, expression:string){
    let exp:string = expression;

    for (let i=0; i < exp.length; i++){
      let elem = exp[i];
      
      if (elem === operation){
        let parts = exp.split(elem);
        // simple parse for both elements to get number
        let left_part:string = parts[0];
        let right_part:string = parts[1];

        // regex update for new expression extraction 
        // let left_match = left_part.match(/(\d+)\s*$/);
        // let right_match = right_part.match(/^\s*(\d+)/);
        
        let left_match = left_part.match(/([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*$/);
        let right_match = right_part.match(/^\s*([A-Za-z_]\w*|\d+(?:\.\d+)?)/);

        if (left_match && right_match){
          // Tweak here for returning with a numerical package :)
          //let left_number:number = parseInt(left_match[1], 10);
          //let right_number:number = parseInt(right_match[1], 10);

          let left_number:string = left_match[1];
          let right_number:string = right_match[1];
          console.log(`Parsed operation operands : ${left_number} with right : ${right_number}`);
          return [left_number,elem, right_number];
        }
      }

    }
  }
  parse(){
    // Iterate the operation sequence and update the expression with component
    let operation_order = this.operation_order; // Alters within given operation
    let expression = this.expression;  // changed with in the function

    let components_dictionary:Record<string,string> = {};
    let component_list:string[] = []; // listing all components

    let component_number = 0;

    for (let i=0; i < this.operation_order.length; i++){
      let operation:string = operation_order[i];
      // Extracting operation component
      let operation_component:string[] = this.extract_component(operation, expression);
      let sub_string:string = operation_component.join("");

      // Updating data listings 
      component_list.push(sub_string);
      let tag = `component_${component_number}`
      components_dictionary[tag] = sub_string;

      // replace components position with tag embeding
      expression = expression.replace(sub_string, tag); // replaceAll fix
      component_number ++;
    }
    return [components_dictionary, component_list, expression]
  }
}
let expre:string = "2*2+2*2";
const e = new ExpressionEngine(expre);

let response = e.parse() // working fine 

console.log(`Final Expression ${response[2]}`)
console.log("Final components_dictionary ",response[0])
console.log(`Component List : ${response[1]}`)
console.log(expre)
