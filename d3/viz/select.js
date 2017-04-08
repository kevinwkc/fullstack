var data = [];

data[0] = [];
data[1] = [];
data[2] = [];
data[3] = [];

data[0][0] = [1,2,3];
data[0][1] = [4,5,6];

data[1][0] = [7,8];
data[1][1] = [9,10,11,12];
data[1][2] = [13,14,15];

data[2][0] = [16];

data[3][0] = [17,18];

//3 dimension array
//console.log(data);

var width = 1000;
var height = 240;
var barWidth = 100;
var barGap = 10;




var margin = {left:50,right:50,top:0,bottom:0};

var svg = d3.select("body").append("svg").attr("width",width).attr("height",height);
var chartGroup = svg.append("g").attr("transform","translate("+margin.left+","+margin.top+")");

//add 4 groups for 1st dimension
var firstGroups = chartGroup.selectAll("g")
	.data(data)
	.enter().append("g")
		.attr("class",function(d,i){ return "firstLevelGroup"+i; })
		.attr("transform",function(d,i){ return "translate("+(i*(barWidth+barGap))+",0)" ; })

//console.log(firstGroups); it has 4 _groups

//continue from above, add 7 group for 2nd dimension
var secondGroups = firstGroups.selectAll("g")
	.data(function(d){ console.log("secondGroups data:"+d); return d;}) //run 4 times
	.enter().append("g")
  //here run 7 times: 2, 3, 1, 1 times, advice: always log(d) to check
		.attr("class",function(d,i,j){ return "secondLevelGroup"+i; })
		.attr("transform",function(d,i,j){ console.log("secondGroups transform:" + d); return "translate(0,"+(height-((i+1)*50))+")"; }); //7 lines of logs

console.log(secondGroups);

secondGroups.append("rect") //run 7 times
	.attr("x",function(d,i){ return 0;})
	.attr("y","0")
	.attr("width",100)
	.attr("height",50)
	.attr("class","secondLevelRect");

//selectAll and a join
secondGroups.selectAll("circle")
	.data(function(d){ console.log("circle: "+d); return d; }) //run 7 times at 2nd dimension
	.enter().append("circle")
  //run the 3rd dimension
	.filter(function(d){ return d>10; })
		.attr("cx",function(d,i){ console.log("3rd dimension:"+d); return ((i*21)+10); })
		.attr("cy","25")
		.attr("r","10")


secondGroups.selectAll("text")
	.data(function(d){ return d; })
	.enter()
.append("text")
	.attr("x",function(d,i){ return ((i*21)+10); })
	.attr("y","25")
	.attr("class","txt")
	.attr("text-anchor","middle")
	.attr("dominant-baseline","middle")
	.text(function(d,i,nodes){return d;}); //version 4 has function(d,i,nodes); nodes return nodes list of parent
