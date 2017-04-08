var parseDate = d3.timeParse("%Y");

d3.xml("data2.xml").get(function(error,xml){

  var height = 200;
  var width = 500;
  var margin = {left: 50, right: 50, top: 40, bottom:0};

  xml = [].map.call(xml.querySelectorAll("dat"),function(d){
    return {
      date: parseDate(d.getAttribute("id")),
      top: +d.querySelector("top").textContent,
      middle: +d.querySelector("middle").textContent,
      bottom: +d.querySelector("bottom").textContent

    };

  })
  var x = d3.scaleTime()
            .domain(d3.extent(xml,function(d){return d.date;}))
            .range([0,width]);
  var y = d3.scaleLinear()
            .domain([0,d3.max(xml,function(d){ return d.top+d.middle+d.bottom; })]) //total of 3 element
            .range([height,0]);

  var categories = ['top','middle','bottom']; //xml tags

  var stack = d3.stack().keys(categories); //generator output x,y coord; stack generate 2 y coord.

  var area = d3.area()
                .x(function(d,i){ return x(d.data.date);}) //d.data has object before transform by stack generator
                .y0(function(d){ return y(d[0]);}) // 0 
                .y1(function(d){ return y(d[1]);});  // upper bound

  var svg = d3.select("body").append("svg").attr("width","100%").attr("height","100%");
  var chartGroup = svg.append("g").attr("transform","translate("+margin.left+","+margin.top+")");

  var stacked = stack(xml); //run the stack generator
  console.log(stacked);  //array contains 3 array(26); data stack on top of each other
  
  chartGroup.append("g").attr("class","x axis")
                        .attr("transform","translate(0,"+height+")")
                        .call(d3.axisBottom(x));
  chartGroup.append("g").attr("class","y axis")
                        .call(d3.axisLeft(y).ticks(5));

  // chartGroup.selectAll("path.area")
  //   .data(stacked)
  //   .enter().append("path")
  //             .attr("class","area")
  //             .attr("d",function(d){ return area(d); });
  // ALTERNATIVE:
chartGroup.selectAll("g.area")
    .data(stacked)
    .enter().append("g")
              .attr("class","area")
    .append("path")  //add one path per group
              .attr("class","area")
              .attr("d",function(d){ return area(d); }); //we can access d even though we added the group in between

});
