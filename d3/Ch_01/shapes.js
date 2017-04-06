console.log("hello")

var dataArray=[5,11,18];

var svg=d3.select("body").append("svg").attr("height", "100%").attr("width","100%"); //x,y,width,ry,rx, class,transform: https://www.w3.org/TR/SVG/

svg.selectAll("rect")       //return empty or array
  .data(dataArray)          //bind data to rect ie) link 1 rect: 5; 2nd rect:11; 3rd rect:18
  .enter().append("rect")   //enter selection no rect, only datapoint => add 3 place holder of undefined, append as rect
  .attr("height",function(d,i){return d*15})
  .attr("width","50")
  .attr("fill", "green")
  .attr("x", function(d,i){return 60*i;})         //d data; i for index
  .attr("y",function(d,i){return 300-(d*15);});   //what if you have 2 element: d3 join the left over to enter selection; in this case all data are leftover into rect
  
  //what if we have 4 rect with 3 data; d3 put the last data into exit selection: .exit().remove(), so that exit selection will be empty and not effect after any append()

var newX=300;  
svg.selectAll("circle")       //return empty or array
  .data(dataArray)            //bind data to rect ie) link 1 rect: 5; 2nd rect:11; 3rd rect:18
  .enter().append("circle")
  .attr("class", "circle.first")         //css class name to solve conflict below
  .attr("cx",function(d,i){ newX+=(d*3)+(i*20); return newX;})
  .attr("cy","100")
  .attr("r",function(d,i){return d*3;});
  
var newX=600;  
svg.selectAll("ellipse")        //return empty or array
  .data(dataArray)             //bind data to rect ie) link 1 rect: 5; 2nd rect:11; 3rd rect:18
  .enter().append("ellipse")    //enter selection is empty, because data already matched the element:circle(we have rename to ellipse), SOLUTION: we need to add class
  .attr("class", "second")
  .attr("cx",function(d,i){ newX+=(d*3)+(i*20); return newX;})
  .attr("cy","100")
  .attr("rx",function(d,i){return d*3;})
  .attr("ry", "30");  
  
var newX=900;  
svg.selectAll("line")        //return empty or array
  .data(dataArray)             //bind data to rect ie) link 1 rect: 5; 2nd rect:11; 3rd rect:18
  .enter().append("line")    
  /*
  .attr("stroke", "blue") //require to show for line
  .attr("stroke-width", "2") //2 pixel
  */
  //.style("stroke", "pink") //style (30px instead of 30 for font size) take precedence than css(preferable because centralized in css file) > attr  
  .attr("x1",newX)
  .attr("y1",function(d,i){return 80+(i*20);})  //20 pixel gap
  .attr("x2",function(d,i){return newX+(d*15);})
  .attr("y2", function(d,i){return 80+(i*20);});    
  
var textArray=['start','middle', 'end']  
svg.append("text").selectAll("tspan")  //tspan for new line
  .data(textArray)
  .enter().append("tspan")
  .attr("x", newX)
  .attr("y", function(d,i){return 150*i;})
  .text(function(d){return d;});