//responsive design: using javascript to set width, 
//<body onresize='callFunction()'>
//function callFunction(){

//d3.select(window).on("resize", callFunction);
  
var  svgtest=d3.select("body").select("svg");
if(!svgtest.empty()){
  svg.remove();
}

var tooltip=d3.select("body").append("div").style("opacity", "0") //invisible
                .style("position", "absolute");
                
console.log(window.innerWidth)
var width=window.innerWidth || document.documentELement.clientWidth || document.body.clientWidth; //support for older browser old browser might not work
var height=window.innerHeight;

var vertices=d3.range(100) //array [0, 99]
              .map(function(d){return [Math.random()*width, Math.random()*height];});  //array of [x,y]
              
var voronoi = d3.voronoi().size([width,height]);
var svg = d3.select("body").append("svg").attr("width", "100%").attr("height", "100%");

function dragged(){
  d3.select(this).attr("transform", "translate("+d3.event.x+","+d3.event.y+")");
}
var chartGroup = svg.append("g") //groups for zoom
                     .call(d3.drag().on("drag",dragged));
chartGroup.call(d3.zoom()
                   .scaleExtent([0.8,2]) //zoom limit
                  .on("zoom",function(){
  chartGroup.attr("transform", d3.event.transform)
}));

chartGroup.append("g").attr("class", "polygons")
              .selectAll("path")
              .data(voronoi.polygons(vertices))
              .enter().append("path")
              .attr("d", function(d) {console.log(d); return "M" +d.join("L")+"Z"; }) //polygon with diff number of vertices, join the line
//}              
              .on("mousemove", function(d){ 
                    this.style.fill="red";
                    //tooltip.style("opacity", "1").style("left", d3.event.pageX+"px").style("top", d3.event.pageY+"px");  //must use unit px using mouse x,y
                    tooltip.style("opacity", "1").style("left", d[0][0]+"px").style("top", d[0][1]+"px"); //using first corner of polygon
                    tooltip.html("Number of slides: "+d.length);
              })
              .on("mouseout", function(){ this.style.fill="white";});
              
chartGroup.append("g").attr("class", "fuel")
              .selectAll("circle")
              .data(vertices)
              .enter().append("circle")
              .attr("cx", function(d){return d[0];})
              .attr("cy", function(d){return d[1];})
              .attr("r", "2.5");     

//triggle event: d3.dispatch              
d3.select("g.polygons").select("path:nth-child(30)")
                        .transition().duration(5000)
                        .style("fill", "red")         //going from red to blue
                        .transition().duration(5000) //after selection before the thing you want to change
                        .delay(1000)      //delay the transition
                        .style("fill", "blue")       //30 is the 31 element because 0-based
                        .attr("transform", "translate(10,10)"); //move down, right
d3.select("g.polygons").select("path:nth-child(30)").dispatch("mouseover");