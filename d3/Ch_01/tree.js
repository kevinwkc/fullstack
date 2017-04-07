var height = 200;
var width = 500;
var margin = {left: 50,right:50,top:40,bottom:0};

var tree = d3.tree().size([width,height]);

var svg = d3.select('body').append('svg').attr('width','100%').attr('height','100%');
var chartGroup = svg.append('g').attr('transform','translate('+margin.left+','+margin.top+')');

d3.json('treeData.json').get(function(error,data){

//console.log(data[0]);
//console.log(data[1]);
console.log(data);
var root = d3.hierarchy(data[0]); //layout: turn data into tree data structure
tree(root);                       //d3.tree() for x,y coord
chartGroup.selectAll("circle")
  .data(root.descendants())
  .enter().append("circle")
          .attr("cx",function(d){ return d.x; })
          .attr("cy",function(d){ return d.y; })
          .attr("r","5");

chartGroup.selectAll("path")
  .data(root.descendants().slice(1)) //always need 1 less path than the dots that we have, every dot has a line, apart from the root
  .enter().append("path")
          .attr("class","link")
          //.attr("d", function(d){ return "M"+d.x+","+d.y+"L"+d.parent.x+","+d.parent.y;}); 
          .attr("d",function(d){ return "M"+d.x+","+d.y+"C"+d.x+","+(d.parent.y+d.y)/2+" "+d.parent.x+","+(d.y+d.parent.y)/2+" "+d.parent.x+","+d.parent.y; }); //drawing upward starting with "M" then "C" for curve or "L" for line

});
